#! /usr/bin/env python3

"""
Sherlock: Optional Web UI

A lightweight Flask wrapper around the Sherlock CLI that streams scan progress
to the browser. Three display modes surface feedback at different levels of
detail so users see continuous progress instead of waiting in silence for a
full scan to complete.

Run with:
    python -m sherlock_project.web

Requires Flask (not a core dependency):
    pip install flask
"""

import os
import re
import subprocess
import sys
from typing import Iterator

try:
    from flask import Flask, Response, render_template_string, request
except ImportError:
    print("Flask is required to run the Sherlock web UI.")
    print("Install it with: pip install flask")
    sys.exit(1)


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5000
SCAN_TIMEOUT_SECONDS = 10
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")

PAGE_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sherlock</title>
  <style>
    :root{--bg:#0b0e14;--panel:#141925;--border:#242b3d;--muted:#7a829a;--text:#e6e6e6;--accent:#7aa2f7;--ok:#9ece6a;--miss:#f7768e;}
    *{box-sizing:border-box}
    body{font-family:-apple-system,system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;background:var(--bg);color:var(--text);}
    .header{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:1.5rem;}
    h1{color:var(--accent);margin:0 0 .25rem;font-size:1.75rem;}
    .sub{color:var(--muted);margin:0;font-size:.9rem;}
    form{display:flex;gap:.5rem;margin-bottom:1.25rem;}
    input[type=text]{flex:1;padding:.7rem .9rem;font-size:1rem;background:var(--panel);color:var(--text);border:1px solid var(--border);border-radius:6px;}
    input[type=text]:focus{outline:none;border-color:var(--accent);}
    button{padding:.7rem 1.3rem;font-size:1rem;background:var(--accent);color:#0b0e14;border:0;border-radius:6px;cursor:pointer;font-weight:600;}
    button:disabled{opacity:.5;cursor:not-allowed;}
    .toolbar{display:flex;align-items:center;justify-content:space-between;gap:1rem;margin-bottom:.5rem;flex-wrap:wrap;}
    .toolbar-label{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;}
    .segmented{display:inline-flex;background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:2px;}
    .segmented input{display:none;}
    .segmented label{padding:.4rem .85rem;font-size:.85rem;color:var(--muted);cursor:pointer;border-radius:4px;transition:all .15s;user-select:none;}
    .segmented input:checked + label{background:var(--accent);color:#0b0e14;font-weight:600;}
    .segmented label:hover{color:var(--text);}
    .segmented input:checked + label:hover{color:#0b0e14;}
    .stats{color:var(--muted);font-size:.8rem;font-variant-numeric:tabular-nums;}
    .stats .ok{color:var(--ok);}
    .stats .miss{color:var(--miss);}
    .output{background:var(--panel);border:1px solid var(--border);padding:1rem;border-radius:6px;min-height:120px;max-height:520px;overflow:auto;font-family:ui-monospace,SFMono-Regular,monospace;font-size:.82rem;line-height:1.5;white-space:pre-wrap;word-break:break-all;}
    .output .hit{color:var(--text);}
    .output .hit a{color:var(--ok);text-decoration:none;}
    .output .hit a:hover{text-decoration:underline;}
    .output .miss{color:var(--miss);}
    .output .info{color:var(--muted);}
    .output .dash-miss{color:var(--miss);}
    .output .visual{font-size:.85rem;line-height:1.7;}
    .placeholder{color:var(--muted);font-style:italic;}
    .lang{display:inline-flex;background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:2px;flex-shrink:0;}
    .lang input{display:none;}
    .lang label{padding:.3rem .6rem;font-size:.75rem;color:var(--muted);cursor:pointer;border-radius:4px;user-select:none;font-weight:600;}
    .lang input:checked + label{background:var(--accent);color:#0b0e14;}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>Sherlock</h1>
      <p class="sub" data-i18n="subtitle"></p>
    </div>
    <div class="lang" role="radiogroup" aria-label="Language">
      <input type="radio" name="lang" id="lang-en" value="en">
      <label for="lang-en">EN</label>
      <input type="radio" name="lang" id="lang-pt" value="pt">
      <label for="lang-pt">PT</label>
    </div>
  </div>

  <form id="f">
    <input type="text" id="u" required autofocus autocomplete="off"
           pattern="[A-Za-z0-9_.\-]{1,64}"
           data-i18n-attr="placeholder:inputPlaceholder">
    <button type="submit" id="b" data-i18n="searchBtn"></button>
  </form>

  <div class="toolbar">
    <div style="display:flex;align-items:center;gap:.75rem;">
      <span class="toolbar-label" data-i18n="displayLabel"></span>
      <div class="segmented" role="radiogroup" data-i18n-attr="aria-label:displayAria">
        <input type="radio" name="mode" id="m-found" value="found">
        <label for="m-found" data-i18n="modeFound" data-i18n-attr="title:modeFoundTip"></label>
        <input type="radio" name="mode" id="m-live" value="live" checked>
        <label for="m-live" data-i18n="modeLive" data-i18n-attr="title:modeLiveTip"></label>
        <input type="radio" name="mode" id="m-all" value="all">
        <label for="m-all" data-i18n="modeAll" data-i18n-attr="title:modeAllTip"></label>
      </div>
    </div>
    <div class="stats">
      <span class="ok">● <span id="nok">0</span> <span data-i18n="statFound"></span></span>
      &nbsp;·&nbsp;
      <span class="miss">● <span id="nmiss">0</span> <span data-i18n="statMiss"></span></span>
    </div>
  </div>

  <div class="output" id="out"></div>

<script>
const I18N={
  en:{subtitle:"Find social media accounts by username.",inputPlaceholder:"e.g. user123",searchBtn:"Search",searching:"Searching…",displayLabel:"Display",displayAria:"Display mode",modeFound:"Found",modeFoundTip:"Lists only profiles that were found",modeLive:"Live",modeLiveTip:"Shows progress: matches inline, misses as red dashes",modeAll:"Full log",modeAllTip:"Shows the complete log, including every failure",statFound:"found",statMiss:"misses",outEmpty:"Results will appear here.",noHitsYet:"No profiles found yet…",errorPrefix:"Error: "},
  pt:{subtitle:"Procure contas em redes sociais a partir de um nome de usuário.",inputPlaceholder:"ex.: user123",searchBtn:"Buscar",searching:"Buscando…",displayLabel:"Exibição",displayAria:"Modo de exibição",modeFound:"Encontrados",modeFoundTip:"Lista apenas os perfis que foram encontrados",modeLive:"Ao vivo",modeLiveTip:"Mostra progresso: sites encontrados como nomes, falhas como hífens vermelhos",modeAll:"Log completo",modeAllTip:"Mostra o log completo, incluindo todas as falhas",statFound:"encontrados",statMiss:"falhas",outEmpty:"Os resultados aparecerão aqui.",noHitsYet:"Nenhum perfil encontrado ainda…",errorPrefix:"Erro: "}
};

function detectLang(){const s=localStorage.getItem('sherlock_lang');if(s&&I18N[s])return s;return (navigator.language||'en').toLowerCase().startsWith('pt')?'pt':'en';}
let lang=detectLang();
function t(k){return (I18N[lang]&&I18N[lang][k])||I18N.en[k]||k;}

function applyI18n(){
  document.documentElement.lang=lang==='pt'?'pt-br':'en';
  document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n);});
  document.querySelectorAll('[data-i18n-attr]').forEach(el=>{
    el.dataset.i18nAttr.split(',').forEach(pair=>{
      const [attr,key]=pair.split(':');el.setAttribute(attr.trim(),t(key.trim()));
    });
  });
  document.getElementById('lang-'+lang).checked=true;
  render();
}

document.querySelectorAll('input[name=lang]').forEach(r=>r.addEventListener('change',e=>{
  lang=e.target.value;localStorage.setItem('sherlock_lang',lang);applyI18n();
}));

const f=document.getElementById('f'),u=document.getElementById('u'),b=document.getElementById('b'),o=document.getElementById('out');
const nok=document.getElementById('nok'),nmiss=document.getElementById('nmiss');
let events=[];

function parseLine(line){
  const clean=line.replace(/\x1b\[[0-9;]*m/g,'');
  let m=clean.match(/^\[\+\]\s*([^:]+):\s*(.+)$/);
  if(m) return {type:'hit',site:m[1].trim(),url:m[2].trim(),raw:clean};
  m=clean.match(/^\[-\]\s*([^:]+):\s*(.+)$/);
  if(m) return {type:'miss',site:m[1].trim(),raw:clean};
  if(clean.trim()) return {type:'info',raw:clean};
  return null;
}

function currentMode(){return document.querySelector('input[name=mode]:checked').value;}
function esc(s){return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

function render(){
  const mode=currentMode();
  const hits=events.filter(e=>e.type==='hit');
  const misses=events.filter(e=>e.type==='miss');
  const infos=events.filter(e=>e.type==='info');
  if(events.length===0){o.innerHTML=`<span class="placeholder">${esc(t('outEmpty'))}</span>`;nok.textContent='0';nmiss.textContent='0';return;}
  let html='';
  if(mode==='found'){
    html=hits.length===0
      ? `<span class="placeholder">${esc(t('noHitsYet'))}</span>`
      : hits.map(h=>`<div class="hit">[+] ${esc(h.site)}: <a href="${esc(h.url)}" target="_blank" rel="noopener">${esc(h.url)}</a></div>`).join('');
  } else if(mode==='live'){
    const banner=infos.slice(0,4).map(i=>`<div class="info">${esc(i.raw)}</div>`).join('');
    const rows=[];let dashes=[];
    const flush=()=>{if(dashes.length){rows.push(`<div class="visual">${dashes.join(' ')}</div>`);dashes=[];}};
    for(const e of events){
      if(e.type==='hit'){flush();rows.push(`<div class="hit">[+] <a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.site)}</a>: ${esc(e.url)}</div>`);}
      else if(e.type==='miss') dashes.push('<span class="dash-miss">-</span>');
    }
    flush();
    html=banner+rows.join('');
  } else {
    html=events.map(e=>{
      if(e.type==='hit') return `<div class="hit">[+] ${esc(e.site)}: <a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.url)}</a></div>`;
      if(e.type==='miss') return `<div class="miss">${esc(e.raw)}</div>`;
      return `<div class="info">${esc(e.raw)}</div>`;
    }).join('');
  }
  o.innerHTML=html;
  o.scrollTop=o.scrollHeight;
  nok.textContent=hits.length;
  nmiss.textContent=misses.length;
}

document.querySelectorAll('input[name=mode]').forEach(r=>r.addEventListener('change',render));

f.onsubmit=async e=>{
  e.preventDefault();
  b.disabled=true;b.textContent=t('searching');
  events=[];render();
  try{
    const r=await fetch('/search?u='+encodeURIComponent(u.value.trim()));
    const reader=r.body.getReader();const dec=new TextDecoder();let buf='';
    while(true){
      const {done,value}=await reader.read();if(done)break;
      buf+=dec.decode(value,{stream:true});
      const lines=buf.split('\n');buf=lines.pop();
      for(const ln of lines){const p=parseLine(ln);if(p)events.push(p);}
      render();
    }
    if(buf){const p=parseLine(buf);if(p){events.push(p);render();}}
  }catch(err){events.push({type:'info',raw:t('errorPrefix')+err.message});render();}
  b.disabled=false;b.textContent=t('searchBtn');
};

applyI18n();
</script>
</body>
</html>"""


def create_app() -> "Flask":
    """Build and return the Flask application."""
    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return render_template_string(PAGE_TEMPLATE)

    @app.route("/search")
    def search() -> Response:
        username = request.args.get("u", "").strip()
        if not USERNAME_PATTERN.fullmatch(username):
            return Response("Invalid username.", status=400, mimetype="text/plain")
        return Response(_stream_scan(username), mimetype="text/plain")

    return app


def _stream_scan(username: str) -> Iterator[str]:
    """Run a Sherlock scan as a subprocess and yield its output line by line."""
    proc = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "sherlock_project",
            "--print-all",
            "--no-color",
            "--timeout",
            str(SCAN_TIMEOUT_SECONDS),
            username,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        text=True,
        cwd=os.getcwd(),
    )
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            yield line
    finally:
        proc.wait()


def main() -> None:
    """Entry point for `python -m sherlock_project.web`."""
    host = os.environ.get("SHERLOCK_WEB_HOST", DEFAULT_HOST)
    port = int(os.environ.get("SHERLOCK_WEB_PORT", DEFAULT_PORT))
    print(f"Sherlock web UI running at http://{host}:{port}")
    create_app().run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
