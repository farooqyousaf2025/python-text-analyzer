# src/readers.py
"""Read text from .txt, .md, .docx and .pdf files.

.txt/.md  -> read as plain text
.docx     -> stdlib zipfile + XML (no dependency)
.pdf      -> optional pypdf if installed, otherwise a built-in
             stdlib parser that works for most text-based PDFs
"""

import os
import re
import zipfile
from xml.etree import ElementTree

WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
SUPPORTED_EXTENSIONS = (".txt", ".md", ".docx", ".pdf")


def read_docx(path):
    with zipfile.ZipFile(path) as z:
        root = ElementTree.fromstring(z.read("word/document.xml"))
    paragraphs = []
    for para in root.iter(f"{WORD_NS}p"):
        runs = [node.text or "" for node in para.iter(f"{WORD_NS}t")]
        text = "".join(runs).strip()
        if text:
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _decode_pdf_string(raw):
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == "\\" and i + 1 < len(raw):
            nxt = raw[i + 1]
            mapping = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f",
                       "\\": "\\", "(": "(", ")": ")"}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            if nxt.isdigit():
                octal = re.match(r"[0-7]{1,3}", raw[i + 1:])
                out.append(chr(int(octal.group(), 8)))
                i += 1 + octal.end()
                continue
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def read_pdf_basic(path):
    """Dependency-free PDF text extraction.

    Handles uncompressed streams and FlateDecode (via zlib). Works for
    typical digitally-generated PDFs; scanned/image PDFs need OCR.
    """
    import zlib

    with open(path, "rb") as f:
        data = f.read()
    if not data.lstrip().startswith(b"%PDF"):
        raise ValueError(f"{path} does not look like a PDF file")

    chunks = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        stream = m.group(1)
        head = data[max(0, m.start() - 400):m.start()]
        if b"FlateDecode" in head:
            try:
                stream = zlib.decompress(stream)
            except zlib.error:
                continue
        if not (b"BT" in stream or b"Tj" in stream or b"TJ" in stream):
            continue
        pieces = []
        for sm in re.finditer(rb"\((?:\\.|[^\\()])*\)|<[0-9A-Fa-f\s]+>", stream):
            token = sm.group(0)
            if token.startswith(b"("):
                pieces.append(_decode_pdf_string(token[1:-1].decode("latin-1")))
            else:
                hexstr = re.sub(rb"\s", b"", token[1:-1])
                try:
                    raw = bytes.fromhex(hexstr.decode("ascii"))
                except ValueError:
                    continue
                text = raw.decode("utf-16-be", errors="ignore") if len(raw) % 2 == 0 \
                    else raw.decode("latin-1", errors="ignore")
                pieces.append(re.sub(r"[\x00-\x1f]", "", text))
            # tokens are joined; line structure is not preserved
        text = "".join(pieces)
        if text:
            chunks.append(text + "\n")
    return "\n".join(chunks).strip()


def read_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return read_pdf_basic(path)
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def read_text_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return read_docx(path)
    if ext == ".pdf":
        return read_pdf(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
