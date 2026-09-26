#!/usr/bin/env python3
"""Render raw-leads-ranked.json into a single self-contained HTML board that
opens in the user's own browser (file://) with search + filters + bulk-open."""
import datetime as dt
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "raw-leads-ranked.json")
OUT = os.path.join(HERE, "leads-board.html")
MIN_SCORE = 6
CAP = 2600

rows = json.load(open(IN))
rows = [r for r in rows if r.get("score", 0) >= MIN_SCORE][:CAP]

TECH_TAGS = [
    ("python", r"python"), ("typescript/js", r"typescript|javascript|node|react|next|astro"),
    ("go", r"\bgo\b|golang"), ("fullstack", r"full[\s-]?stack"),
    ("backend", r"back[\s-]?end"), ("frontend", r"front[\s-]?end"),
    ("ai/ml", r"\bai\b|\bml\b|machine learning|llm|agent|nlp"),
    ("data", r"data"), ("devops/cloud", r"devops|cloud|docker|kubernetes|linux|sre|infra"),
    ("security/privacy", r"security|privacy|cyber"),
    ("open source", r"open[\s-]?source|foss"), ("fresher-friendly", r"intern|fresher|junior|entry"),
]


def tags_of(r):
    blob = " ".join([r.get("title", ""), " ".join(r.get("tags") or []), r.get("company", "")])
    return [label for label, rx in TECH_TAGS if re.search(rx, blob, re.I)]


items = []
for r in rows:
    items.append({
        "t": r.get("title", ""),
        "c": r.get("company") or "",
        "s": r.get("source", ""),
        "loc": r.get("location") or "",
        "jt": r.get("job_type") or "",
        "pay": (r.get("stipend") or ""),
        "dur": (r.get("duration") or ""),
        "u": r.get("url", ""),
        "sc": r.get("score", 0),
        "age": r.get("age_days"),
        "tags": tags_of(r) + [x for x in (r.get("tags") or []) if isinstance(x, str)][:3],
        "ec": bool(re.search(r"intern|trainee|apprentice|graduate|entry[\s-]?level|junior|associate|fresher", r.get("title", ""), re.I)
                   or r.get("job_type") in ("Internship", "Part-time")),
    })

counts = {}
for i in items:
    counts[i["s"]] = counts.get(i["s"], 0) + 1

# fold in the curated OSS/privacy employer board hits (Canonical, Supabase, Proton, …)
BOARD = os.path.join(HERE, "board-focus.json")
SENIOR_RX = re.compile(r"senior|director|manager|staff|principal|lead\b|head of|\bvp\b|architect|chief|recruit", re.I)
if os.path.exists(BOARD):
    added = 0
    for entry in json.load(open(BOARD)):
        try:
            src, title, loc, url = entry
        except Exception:
            continue
        if SENIOR_RX.search(title) or not url.startswith("http"):
            continue
        items.append({"t": title, "c": src.replace("gh:", "").replace("ashby:", "").title(),
                      "s": "board", "loc": loc, "jt": "Remote", "pay": "", "dur": "",
                      "u": url, "sc": 25, "age": None, "tags": [src.split(":")[0]], "ec": True})
        added += 1
    print(f"folded in {added} company-board roles")

counts = {}
for i in items:
    counts[i["s"]] = counts.get(i["s"], 0) + 1
sources = sorted(counts.items(), key=lambda x: -x[1])
stamp = dt.datetime.now().strftime("%d %b %Y, %H:%M")

payload = json.dumps(items, ensure_ascii=False)
source_opts = "".join(f'<option value="{html.escape(s)}">{html.escape(s)} ({n})</option>' for s, n in sources)

html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Prit's job board — {len(items)} remote/intern leads</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--bg:#0d1117;--card:#161b22;--line:#30363d;--tx:#e6edf3;--mut:#8b949e;--acc:#1e40af;--acc2:#2ea043}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--tx);font:14px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}}
header{{padding:18px 20px 12px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:5}}
h1{{margin:0 0 4px;font-size:19px}}
.sub{{color:var(--mut);font-size:12.5px}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;align-items:center}}
input,select,button{{background:var(--card);color:var(--tx);border:1px solid var(--line);border-radius:7px;padding:7px 10px;font-size:13px}}
input#q{{flex:1;min-width:240px}}
button{{cursor:pointer}}button:hover{{border-color:var(--acc)}}
button.go{{background:var(--acc);border-color:var(--acc)}}
main{{padding:14px 20px 60px;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:10px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:11px 12px;display:flex;flex-direction:column;gap:6px}}
.card a.t{{color:var(--tx);font-weight:600;text-decoration:none;font-size:14px}}
.card a.t:hover{{color:#79c0ff;text-decoration:underline}}
.meta{{color:var(--mut);font-size:12px}}
.badges{{display:flex;gap:5px;flex-wrap:wrap}}
.b{{font-size:10.5px;padding:2px 7px;border-radius:20px;border:1px solid var(--line);color:var(--mut)}}
.b.sc{{color:#d29922;border-color:#9e6a03}}
.b.pt{{color:#a371f7;border-color:#6e40c9}}
.b.in{{color:#2ea043;border-color:#238636}}
.b.src{{color:#79c0ff;border-color:#1f6feb}}
footer{{color:var(--mut);font-size:12px;padding:0 20px 30px}}
.none{{color:var(--mut);padding:20px}}
</style></head><body>
<header>
<h1>Prit's job board — {len(items)} leads scored for your profile</h1>
<div class="sub">Remote internships / part-time technical work · filtered to score ≥ {MIN_SCORE} · generated {stamp}<br>
Sources: {', '.join(f'{s} ({n})' for s,n in sources)}</div>
<div class="bar">
<input id="q" placeholder="search title, company, tag… (e.g. python, react, privacy)">
<select id="src"><option value="">all sources</option>{source_opts}</select>
<select id="jt"><option value="">any type</option><option>Internship</option><option>Part-time</option><option>Remote</option><option>FOSS</option></select>
<select id="tag"><option value="">any stack</option>{''.join(f'<option>{t}</option>' for t,_ in TECH_TAGS)}</select>
<select id="sort"><option value="sc">best fit</option><option value="age">newest</option></select>
<label class="sub"><input type="checkbox" id="ec" checked> early-career only</label>
<label class="sub"><input type="checkbox" id="paid"> paid only</label>
<button class="go" id="open10">open top 10 in tabs</button>
<span class="sub" id="count"></span>
</div></header>
<main id="grid"></main>
<footer>Click a title to open the posting. "open top 10" opens the 10 best currently-filtered leads in new tabs (browsers cap popups per click — click again for the next batch). Built from your resume repo's job-hunt pipeline.</footer>
<script>
const JOBS = {payload};
const grid = document.getElementById('grid');
const q = document.getElementById('q'), src = document.getElementById('src'), jt = document.getElementById('jt'),
      tag = document.getElementById('tag'), sort = document.getElementById('sort'), paid = document.getElementById('paid'),
      ec = document.getElementById('ec');
let shown = [];
function esc(s){{return (s||'').replace(/[<>&]/g, c => ({{'<':'&lt;','>':'&gt;','&':'&amp;'}})[c]);}}
function payBool(j){{return /[₹$€£]|rs|inr|month|stipend|salary|annual/i.test(j.pay||'') && !/unpaid/i.test(j.pay||'');}}
function render(){{
  const term = q.value.trim().toLowerCase();
  shown = JOBS.filter(j => {{
    if (src.value && j.s !== src.value) return false;
    if (jt.value && j.jt !== jt.value) return false;
    if (tag.value && !(j.tags||[]).includes(tag.value)) return false;
    if (paid.checked && !payBool(j)) return false;
    if (ec.checked && !j.ec) return false;
    if (term) {{
      const hay = (j.t + ' ' + j.c + ' ' + j.tags.join(' ') + ' ' + j.loc + ' ' + j.jt).toLowerCase();
      if (!term.split(' ').filter(Boolean).every(w => hay.includes(w))) return false;
    }}
    return true;
  }});
  shown.sort((a,b) => sort.value === 'age'
    ? ((a.age ?? 9999) - (b.age ?? 9999)) || (b.sc - a.sc)
    : (b.sc - a.sc));
  grid.innerHTML = shown.map(j => {{
    const cls = j.jt === 'Part-time' ? 'pt' : (j.jt === 'Internship' ? 'in' : '');
    const age = (j.age === null || j.age === undefined) ? '' : `<span class="b">${{j.age}}d</span>`;
    const extra = [j.pay, j.dur, j.loc].filter(Boolean).map(esc).join(' · ');
    return `<div class="card">
      <a class="t" href="${{esc(j.u)}}" target="_blank" rel="noopener">${{esc(j.t)}}</a>
      <div class="meta">${{esc(j.c) || '&nbsp;'}}</div>
      <div class="badges"><span class="b sc">${{j.sc}}</span><span class="b src">${{esc(j.s)}}</span>
      ${{j.jt ? `<span class="b ${{cls}}">${{esc(j.jt)}}</span>` : ''}}${{age}}
      ${{(j.tags||[]).slice(0,4).map(t => `<span class="b">${{esc(t)}}</span>`).join('')}}</div>
      <div class="meta">${{extra}}</div></div>`;
  }}).join('') || '<div class="none">No leads match those filters.</div>';
  document.getElementById('count').textContent = shown.length + ' leads';
}}
[q,src,jt,tag,sort,paid,ec].forEach(el => el.addEventListener('input', render));
document.getElementById('open10').onclick = () => {{
  shown.slice(0,10).forEach(j => window.open(j.u, '_blank', 'noopener'));
}};
render();
</script></body></html>
"""

with open(OUT, "w") as fh:
    fh.write(html_doc)
print(f"wrote {OUT}: {len(items)} leads ({os.path.getsize(OUT)//1024} KB)")
