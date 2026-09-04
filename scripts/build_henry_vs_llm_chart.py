"""Gera um grafico comparativo direto: combined_index Henry (dicionario) vs
combined_index LLM (Claude Haiku 4.5), reuniao a reuniao. Mesma estetica dos
outros graficos do projeto (SVG via JS, sem lib externa, tema claro/escuro).
"""

import csv
import json
from collections import defaultdict
from datetime import date

import config

OUT_HTML = config.REPORTS_DIR / "henry-vs-llm-index.html"


def load_by_date(csv_path):
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    by_date = defaultdict(list)
    titles = {}
    for r in rows:
        if not r.get("meeting_date"):
            continue
        by_date[r["meeting_date"]].append(float(r["combined_index"]))
        titles.setdefault(r["meeting_date"], r.get("title", ""))
    # Duas reunioes de 1999 tem duas atas no mesmo dia -- media simples.
    return {d: sum(v) / len(v) for d, v in by_date.items()}, titles


def main():
    henry_by_date, titles = load_by_date(config.COMBINED_INDEX_HENRY_CSV)
    llm_by_date, _ = load_by_date(config.COMBINED_INDEX_LLM_CSV)

    dates = sorted(set(henry_by_date) & set(llm_by_date))
    first_date = date.fromisoformat(dates[0])

    data = []
    for d_str in dates:
        d = date.fromisoformat(d_str)
        data.append({
            "date": d_str,
            "title": titles.get(d_str, ""),
            "henry": round(henry_by_date[d_str], 4),
            "llm": round(llm_by_date[d_str], 4),
            "x": (d - first_date).days,
        })

    x_max = data[-1]["x"]
    data_json = json.dumps(data, ensure_ascii=False)

    html = f"""<title>SARB combined index: Henry dictionary vs. LLM classifier, by meeting (1999-2026)</title>

<style>
.viz-root {{
  color-scheme: light;
  --surface-1:      #eaf2f8;
  --page:           #f9f9f7;
  --text-primary:   #0b0b0b;
  --text-secondary: #52514e;
  --muted:          #6b7580;
  --grid:           #ffffff;
  --baseline:       #0b0b0b;
  --henry:          #8a8578;
  --llm:            #2a78d6;
  --border:         rgba(11,11,11,0.10);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}}
@media (prefers-color-scheme: dark) {{
  :root:where(:not([data-theme="light"])) .viz-root {{
    color-scheme: dark;
    --surface-1:      #1c2732;
    --page:           #0d0d0d;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --muted:          #9aa5af;
    --grid:           #2c3a47;
    --baseline:       #ffffff;
    --henry:          #a3a191;
    --llm:            #3987e5;
    --border:         rgba(255,255,255,0.10);
  }}
}}
:root[data-theme="dark"] .viz-root {{
  color-scheme: dark;
  --surface-1:      #1c2732;
  --page:           #0d0d0d;
  --text-primary:   #ffffff;
  --text-secondary: #c3c2b7;
  --muted:          #9aa5af;
  --grid:           #2c3a47;
  --baseline:       #ffffff;
  --henry:          #a3a191;
  --llm:            #3987e5;
  --border:         rgba(255,255,255,0.10);
}}

.viz-root {{ background: var(--page); padding: 24px; box-sizing: border-box; }}
.card {{
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 22px 12px;
  max-width: 1100px;
  margin: 0 auto 14px;
}}
.card h1 {{ font-size: 16px; margin: 0 0 2px; color: var(--text-primary); font-weight: 600; }}
.card .sub {{ font-size: 12.5px; color: var(--text-secondary); margin-bottom: 12px; }}
.legend {{ display:flex; gap:16px; font-size:11.5px; color:var(--text-secondary); margin: 6px 0 2px; flex-wrap: wrap; align-items: center; }}
.legend .item {{ display:flex; align-items:center; gap:6px; }}
.legend .line {{ width:16px; height:2px; display:inline-block; }}
svg {{ width: 100%; height: auto; overflow: visible; display:block; }}
.axis-label {{ fill: var(--muted); font-size: 10.5px; }}
.grid-line {{ stroke: var(--grid); stroke-width: 1; }}
.baseline {{ stroke: var(--baseline); stroke-width: 1.2; }}
.line-henry {{ fill:none; stroke: var(--henry); stroke-width: 1.6; }}
.line-llm {{ fill:none; stroke: var(--llm); stroke-width: 1.6; }}
.dot-henry {{ fill: var(--henry); }}
.dot-llm {{ fill: var(--llm); }}
#tooltip {{
  position: fixed; pointer-events: none;
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px;
  padding: 9px 11px; font-size: 12px; color: var(--text-primary);
  box-shadow: 0 4px 16px rgba(0,0,0,0.18); max-width: 300px; display: none; z-index: 10; line-height: 1.5;
}}
.note {{ font-size: 11.5px; color: var(--text-secondary); max-width: 1100px; margin: 8px auto 20px; padding: 0 4px; }}
</style>

<div class="viz-root">
  <div class="card">
    <h1>SARB combined index: dictionary vs. LLM, by meeting (1999-2026)</h1>
    <div class="sub">Same 173 meetings, same corpus, two scoring methods &middot; Henry (2008) word-count dictionary vs. Claude Haiku 4.5 whole-document read</div>
    <div class="legend">
      <span class="item"><span class="line" style="background:var(--henry)"></span> Henry (dictionary)</span>
      <span class="item"><span class="line" style="background:var(--llm)"></span> LLM (Claude Haiku 4.5)</span>
    </div>
    <svg id="chart" viewBox="0 0 1060 360" preserveAspectRatio="xMidYMid meet"></svg>
  </div>
</div>

<div class="note">Same underlying documents, same meeting windows -- only the scoring method changes. The LLM line spends real time below zero on cutting cycles; the Henry line almost never does.</div>

<div id="tooltip"></div>

<script>
const DATA = {data_json};
const X_MIN = 0, X_MAX = {x_max};
const YEAR_STEP = 2;

const svg = document.getElementById('chart');
const W = 1060, H = 360;
const M = {{top: 14, right: 18, bottom: 32, left: 40}};
const plotW = W - M.left - M.right;
const plotH = H - M.top - M.bottom;

const allVals = DATA.flatMap(d => [d.henry, d.llm, 0]);
const vMax = Math.max(...allVals, 0.2);
const vMin = Math.min(...allVals, -0.2);
const yMax = Math.ceil(vMax * 5) / 5 + 0.1;
const yMin = Math.floor(vMin * 5) / 5 - 0.1;

function y(v) {{ return M.top + (1 - (v - yMin) / (yMax - yMin)) * plotH; }}
function x(i) {{ return M.left + ((DATA[i].x - X_MIN) / (X_MAX - X_MIN)) * plotW; }}

function svgEl(tag, attrs) {{
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const k in attrs) el.setAttribute(k, attrs[k]);
  return el;
}}

for (let v = Math.ceil(yMin * 5) / 5; v <= yMax; v += 0.2) {{
  const gy = y(v);
  const isZero = Math.abs(v) < 1e-9;
  svg.appendChild(svgEl('line', {{x1: M.left, x2: W - M.right, y1: gy, y2: gy, class: isZero ? 'baseline' : 'grid-line'}}));
  const lbl = svgEl('text', {{x: M.left - 8, y: gy + 4, class: 'axis-label', 'text-anchor': 'end'}});
  lbl.textContent = v.toFixed(1);
  svg.appendChild(lbl);
}}

let lastYear = null;
DATA.forEach((d, i) => {{
  const year = d.date.slice(0, 4);
  if (year !== lastYear && (parseInt(year) % YEAR_STEP === 0)) {{
    const gx = x(i);
    const lbl = svgEl('text', {{x: gx, y: H - M.bottom + 16, class: 'axis-label', 'text-anchor': 'middle'}});
    lbl.textContent = year;
    svg.appendChild(lbl);
    lastYear = year;
  }} else if (year !== lastYear) {{
    lastYear = year;
  }}
}});

function pathFor(key) {{
  return DATA.map((d, i) => `${{i === 0 ? 'M' : 'L'}} ${{x(i).toFixed(2)}} ${{y(d[key]).toFixed(2)}}`).join(' ');
}}
svg.appendChild(svgEl('path', {{d: pathFor('henry'), class: 'line-henry'}}));
svg.appendChild(svgEl('path', {{d: pathFor('llm'), class: 'line-llm'}}));

const tooltip = document.getElementById('tooltip');

DATA.forEach((d, i) => {{
  const cx = x(i);
  const dotHenry = svgEl('circle', {{cx: cx, cy: y(d.henry), r: 3.2, class: 'dot-henry'}});
  const dotLlm = svgEl('circle', {{cx: cx, cy: y(d.llm), r: 3.2, class: 'dot-llm'}});
  [dotHenry, dotLlm].forEach(dot => {{
    dot.style.cursor = 'pointer';
    dot.addEventListener('mouseenter', (ev) => showTooltip(ev, d));
    dot.addEventListener('mousemove', positionTooltip);
    dot.addEventListener('mouseleave', () => tooltip.style.display = 'none');
  }});
  svg.appendChild(dotHenry);
  svg.appendChild(dotLlm);
}});

function showTooltip(ev, d) {{
  let html = `<div style="font-weight:600">${{d.date}}</div>`;
  html += `<div style="color:var(--text-secondary); margin-bottom:4px;">${{d.title}}</div>`;
  html += `<div>Henry: ${{d.henry.toFixed(3)}}</div>`;
  html += `<div>LLM: ${{d.llm.toFixed(3)}}</div>`;
  tooltip.innerHTML = html;
  tooltip.style.display = 'block';
  positionTooltip(ev);
}}
function positionTooltip(ev) {{
  const pad = 16;
  let left = ev.clientX + pad;
  let top = ev.clientY + pad;
  if (left + 300 > window.innerWidth) left = ev.clientX - 300 - pad;
  tooltip.style.left = left + 'px';
  tooltip.style.top = top + 'px';
}}
</script>
"""

    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Salvo em: {OUT_HTML}")
    print(f"{len(data)} reunioes plotadas.")


if __name__ == "__main__":
    main()
