# src/web.py
"""Local web UI built on the standard library (no Flask/FastAPI needed).

Start with:  python -m src.main --web [port]
"""

import io
import json
import os
import re
import tempfile
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from src.analyzer import TextAnalyzer
from src.history import DB_PATH, list_analyses, log_analysis
from src.readers import SUPPORTED_EXTENSIONS

MAX_upload = 10 * 1024 * 1024

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Text Analyzer</title>
<style>
:root{--bg:#f6f7fb;--card:#fff;--ink:#1d2433;--mut:#6b7385;--acc:#4f7cff;--ok:#1a9c5b;--bad:#d34444}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{background:var(--ink);color:#fff;padding:18px 28px;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:18px;margin:0}header span{color:#aab3c5;font-size:13px}
main{max-width:1100px;margin:24px auto;padding:0 20px}
textarea{width:100%;min-height:160px;padding:14px;border:1px solid #d6dae3;border-radius:10px;font:inherit;resize:vertical}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0}
button{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:10px 18px;font:inherit;font-weight:600;cursor:pointer}
button.ghost{background:#fff;color:var(--acc);border:1px solid var(--acc)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;margin-top:18px}
.card{background:var(--card);border-radius:12px;padding:14px;box-shadow:0 1px 3px rgba(20,30,60,.08)}
.card b{display:block;font-size:20px;color:var(--acc)}.card small{color:var(--mut)}
section{background:var(--card);border-radius:12px;padding:18px;margin-top:18px;box-shadow:0 1px 3px rgba(20,30,60,.08)}
section h2{margin:0 0 12px;font-size:15px}
.bar{display:flex;align-items:center;gap:8px;margin:4px 0}.bar span{width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}
.bar i{display:block;height:16px;background:var(--acc);border-radius:4px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:6px 8px;border-bottom:1px solid #eceef3;text-align:left}
.pos{color:var(--ok)}.neg{color:var(--bad)}.neu{color:var(--mut)}
#sentences em{background:#fff3b0;padding:0 2px;border-radius:3px}
footer{color:var(--mut);font-size:12px;text-align:center;margin:26px 0}
</style></head><body>
<header><h1>Python Text Analyzer</h1><span>paste text or upload a file &mdash; runs 100% locally</span></header>
<main>
<textarea id="text" placeholder="Paste your text here..."></textarea>
<div class="row">
  <button onclick="analyze()">Analyze</button>
  <input type="file" id="file" accept=".txt,.md,.docx,.pdf" onchange="loadFile(this)">
  <label style="color:var(--mut);font-size:13px"><input type="checkbox" id="findOn"> find word</label>
  <input id="findWord" placeholder="word" style="padding:8px;border:1px solid #d6dae3;border-radius:8px;display:none">
  <a id="dlCsv" style="display:none"><button class="ghost">Download CSV</button></a>
  <a id="dlJson" style="display:none"><button class="ghost">Download JSON</button></a>
</div>
<div id="out"></div>
<section><h2>History</h2><table id="hist"><tr><td>Loading...</td></tr></table></section>
</main>
<footer>Python Text Analyzer &middot; standard library only &middot; nothing leaves your computer</footer>
<script>
const $=id=>document.getElementById(id);
$('findOn').onchange=e=>$('findWord').style.display=e.target.checked?'inline-block':'none';
async function loadFile(inp){const f=inp.files[0];if(!f)return;
 const buf=await f.arrayBuffer();const r=await fetch('/upload',{method:'POST',body:buf,
 headers:{'X-File-Name':encodeURIComponent(f.name),'Content-Type':'application/octet-stream'}});
 const d=await r.json();if(d.error){alert(d.error);return}$('text').value=d.text;analyze();}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
async function analyze(){
 const body={text:$('text').value};if($('findOn').checked&&$('findWord').value)body.find=$('findWord').value.toLowerCase();
 const r=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 const d=await r.json();render(d);loadHistory();}
function render(d){const m=d.metrics;
 const order=[['Words',m.Words],['Sentences',m.Sentences],['Characters',m.Characters],['Unique words',m.UniqueWords],
 ['Paragraphs',m.Paragraphs],['Avg sentence length',m.AvgSentenceLength],['Syllables',m.Syllables],
 ['Flesch reading ease',m.FleschReadingEase],['Grade level',m.GradeLevel],['Vocab richness',m.VocabularyRichness],
 ['Reading time',m.ReadingTimeMinutes+' min'],['Sentiment',d.sentiment.label+' ('+d.sentiment.score+')']];
 let html='<div class="cards">'+order.map(([k,v])=>`<div class="card"><b>${esc(v)}</b><small>${k}</small></div>`).join('')+'</div>';
 const top=d.topWords,max=top.length?top[0][1]:1;
 html+=`<section><h2>Top words</h2>${top.map(([w,c])=>`<div class="bar"><span>${esc(w)}</span><i style="width:${Math.max(3,c/max*62)}%"></i><small>${c}</small></div>`).join('')}</section>`;
 html+=`<section><h2>Keywords</h2>${d.keywords.map(k=>`<div class="bar"><span>${esc(k.word)}</span><i style="width:${Math.max(3,k.weight/d.keywords[0].weight*62)}%"></i><small>${k.count}</small></div>`).join('')}</section>`;
 const sc=d.sentiment.label==='positive'?'pos':d.sentiment.label==='negative'?'neg':'neu';
 let extra=`<section><h2>Longest sentence</h2>${esc(d.longest)}</section><section><h2>Shortest sentence</h2>${esc(d.shortest)}</section>`;
 if(d.find!==null&&d.find!==undefined){extra+=`<section><h2>Word search: "${esc(d.find)}" (${d.findCount} match${d.findCount===1?'':'es'})</h2><div id="sentences">`+
 (d.findSentences.length?d.findSentences.map(s=>'<p>'+esc(s).replace(new RegExp('('+d.find.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','gi'),'<em>$1</em>')+'</p>').join(''):'<p>No sentences found.</p>')+'</div></section>';}
 html=html.replace('<div class="cards">',`<div class="sent ${sc}" style="margin-bottom:8px;font-weight:600"></div><div class="cards">`)+extra;
 $('out').innerHTML=html;$('dlCsv').style.display=$('dlJson').style.display='inline-block';
 $('dlCsv').href='/download?kind=csv&token='+d.token;$('dlJson').href='/download?kind=json&token='+d.token;}
async function loadHistory(){const r=await fetch('/api/history');const rows=await r.json();
 $('hist').innerHTML=rows.length?'<tr><th>ID</th><th>When</th><th>Source</th><th>Words</th><th>Sentences</th><th>Flesch</th></tr>'+
 rows.map(x=>`<tr><td>${x.id}</td><td>${esc(x.timestamp)}</td><td>${esc(x.source)}</td><td>${x.words}</td><td>${x.sentences}</td><td>${x.flesch}</td></tr>`).join(''):
 '<tr><td>No analyses yet.</td></tr>';}
loadHistory();
</script></body></html>"""

LAST_RESULTS = {}


def _multipart_text(raw, content_type):
    message = BytesParser().parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + raw
    )
    for part in message.get_payload():
        filename = part.get_filename()
        if filename and part.get_content_disposition() == "file":
            return filename, part.get_payload(decode=True)
    return None, None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="application/json", extra_headers=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for name, value in (extra_headers or {}).items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if path == "/api/history":
            rows = [
                {"id": r[0], "timestamp": r[1], "source": r[2], "words": r[3],
                 "sentences": r[4], "flesch": r[7], "sentiment": r[8]}
                for r in list_analyses(limit=15)
            ]
            return self._send(200, json.dumps(rows))
        if path == "/download":
            params = parse_qs(urlparse(self.path).query)
            token = params.get("token", [""])[0]
            kind = params.get("kind", ["csv"])[0]
            result = LAST_RESULTS.get(token)
            if not result:
                return self._send(404, '{"error":"expired"}')
            analyzer, text = result
            ext = "csv" if kind == "csv" else "json"
            tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
            tmp.close()
            if kind == "csv":
                analyzer.save_to_csv(tmp.name)
                ctype = "text/csv"
            else:
                analyzer.save_to_json(tmp.name)
                ctype = "application/json"
            with open(tmp.name, "rb") as f:
                data = f.read()
            os.remove(tmp.name)
            filename = "analysis.csv" if kind == "csv" else "analysis.json"
            return self._send(200, data, ctype,
                              {"Content-Disposition": f"attachment; filename={filename}"})
        self._send(404, '{"error":"not found"}')

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/upload":
            length = int(self.headers.get("Content-Length", 0))
            if length > MAX_upload:
                return self._send(400, '{"error":"file too large"}')
            name = self.headers.get("X-File-Name", "upload.txt")
            from urllib.parse import unquote
            name = unquote(name)
            ext = os.path.splitext(name)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                return self._send(400, json.dumps({"error": f"unsupported file type: {ext}"}))
            raw = self.rfile.read(length)
            tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            try:
                tmp.write(raw)
                tmp.close()
                from src.readers import read_text_file
                text = read_text_file(tmp.name)
            except Exception as exc:
                return self._send(400, json.dumps({"error": f"could not read file: {exc}"}))
            finally:
                os.remove(tmp.name)
            return self._send(200, json.dumps({"text": text}))
        if path == "/api/analyze":
            try:
                body = self._json_body()
            except (ValueError, json.JSONDecodeError):
                return self._send(400, '{"error":"invalid json"}')
            analyzer = TextAnalyzer(["pasted text"]).from_text(body.get("text", ""))
            if analyzer.word_count() == 0:
                return self._send(400, '{"error":"no text to analyze"}')
            metrics = analyzer.metrics()
            metrics["GradeLevel"] = analyzer.grade_level_label()
            response = {
                "metrics": metrics,
                "sentiment": analyzer.sentiment(),
                "topWords": analyzer.most_common_words(10, ignore_stopwords=True),
                "keywords": analyzer.keywords(10),
                "longest": analyzer.longest_sentence(),
                "shortest": analyzer.shortest_sentence(),
                "find": None, "findCount": 0, "findSentences": [],
                "token": "",
            }
            find = body.get("find")
            if find:
                response["find"] = find
                response["findCount"] = analyzer.word_frequency(find)
                response["findSentences"] = [s for s in analyzer.sentences if find in s.lower()][:20]
            token = re.sub(r"\W", "", os.urandom(9).hex())
            LAST_RESULTS[token] = (analyzer, body.get("text", ""))
            if len(LAST_RESULTS) > 50:
                LAST_RESULTS.pop(next(iter(LAST_RESULTS)))
            response["token"] = token
            source = "web paste" if not body.get("file") else f"web upload: {body['file']}"
            log_analysis(analyzer, source=source)
            return self._send(200, json.dumps(response))
        self._send(404, '{"error":"not found"}')


def serve(port=8000, open_browser=False):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}"
    print(f"Text Analyzer web UI running at {url}  (Ctrl+C to stop)")
    if open_browser:
        import threading
        import webbrowser
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
