"""Gera a versao LLM do grafico 'Contribution to the combined index, by
meeting' -- mesmo template visual/interativo (SVG desenhado via JS, sem
biblioteca externa) do grafico Henry original, so trocando os dados e o
titulo/legenda pra deixar claro que agora e o metodo LLM (Claude Haiku 4.5).
"""

import csv
import json
from datetime import date

import config

OUT_HTML = config.REPORTS_DIR / "llm-contribution-full.html"


def main():
    titles_by_date = {}
    for r in json.loads(config.DATASET_JSON.read_text(encoding="utf-8")):
        if r.get("meeting_date"):
            titles_by_date.setdefault(r["meeting_date"], r.get("title"))

    rows = list(csv.DictReader(open(config.COMBINED_INDEX_LLM_CSV, encoding="utf-8-sig")))
    rows = [r for r in rows if r.get("meeting_date")]
    rows.sort(key=lambda r: r["meeting_date"])

    first_date = date.fromisoformat(rows[0]["meeting_date"])

    data = []
    for r in rows:
        d = date.fromisoformat(r["meeting_date"])
        x = (d - first_date).days
        n_speech = int(r["n_speeches_in_window"])
        avg_speech = float(r["avg_speech_index"]) if r["avg_speech_index"] not in ("", None) else None
        data.append({
            "date": r["meeting_date"],
            "title": titles_by_date.get(r["meeting_date"], ""),
            "n_speech": n_speech,
            "avg_stmt": float(r["statement_index"]),
            "avg_speech": avg_speech,
            "contrib_stmt": float(r["contrib_statement"]),
            "contrib_speech": float(r["contrib_speech"]),
            "combined": float(r["combined_index"]),
            "x": x,
        })

    x_max = data[-1]["x"]
    data_json = json.dumps(data, ensure_ascii=False)

    html = f"""<title>SARB — LLM index: contribution to the combined index, by meeting (1999–2026)</title>

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
  --stmt:           #2a78d6;
  --speech:         #eb6834;
  --combined:       #0b0b0b;
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
    --stmt:           #3987e5;
    --speech:         #d95926;
    --combined:       #ffffff;
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
  --stmt:           #3987e5;
  --speech:         #d95926;
  --combined:       #ffffff;
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
.legend .swatch {{ width:11px; height:11px; border-radius:2px; display:inline-block; }}
.legend .line {{ width:16px; height:2px; display:inline-block; background: var(--combined); }}
svg {{ width: 100%; height: auto; overflow: visible; display:block; }}
.axis-label {{ fill: var(--muted); font-size: 10.5px; }}
.grid-line {{ stroke: var(--grid); stroke-width: 1; }}
.baseline {{ stroke: var(--baseline); stroke-width: 1.2; }}
.bar-stmt {{ fill: var(--stmt); cursor: pointer; }}
.bar-speech {{ fill: var(--speech); cursor: pointer; }}
.combined-dot {{ fill: var(--combined); }}
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
    <h1>SARB — LLM index: contribution to the combined index, by meeting (1999–2026)</h1>
    <div class="sub">Claude Haiku 4.5, whole-document read (not a word dictionary) &middot; 1 bar per MPC meeting &middot; speeches between the previous meeting and this one are aggregated and attached to it &middot; off-topic speeches excluded</div>
    <div class="legend">
      <span class="item"><span class="swatch" style="background:var(--stmt)"></span> contribution from the statement itself</span>
      <span class="item"><span class="swatch" style="background:var(--speech)"></span> contribution from the window's speeches</span>
      <span class="item"><span class="line"></span> combined index</span>
    </div>
    <svg id="chart" viewBox="0 0 1060 360" preserveAspectRatio="xMidYMid meet"></svg>
  </div>
</div>

<div class="note">173 meetings, scored with the same rubric-calibrated LLM method throughout (Claude Haiku 4.5). Blue = contribution from the statement itself; orange = contribution from speeches given since the previous meeting (on-topic only); black dot = combined index (exact sum). Compare with the original Henry (2008) dictionary version: this index actually crosses zero on cutting cycles instead of running structurally hot.</div>

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

const allVals = DATA.flatMap(d => [d.contrib_stmt, d.contrib_speech, d.combined, 0]);
const vMax = Math.max(...allVals, 0.2);
const vMin = Math.min(...allVals, -0.2);
const yMax = Math.ceil(vMax * 5) / 5 + 0.1;
const yMin = Math.floor(vMin * 5) / 5 - 0.1;

const barW = 3.2;

function y(v) {{ return M.top + (1 - (v - yMin) / (yMax - yMin)) * plotH; }}
function xCenter(i) {{ return M.left + ((DATA[i].x - X_MIN) / (X_MAX - X_MIN)) * plotW; }}

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
    const gx = xCenter(i);
    const lbl = svgEl('text', {{x: gx, y: H - M.bottom + 16, class: 'axis-label', 'text-anchor': 'middle'}});
    lbl.textContent = year;
    svg.appendChild(lbl);
    lastYear = year;
  }} else if (year !== lastYear) {{
    lastYear = year;
  }}
}});

const tooltip = document.getElementById('tooltip');

function addSegment(i, d, value, cls) {{
  if (value === 0) return;
  const cx = xCenter(i);
  const x0 = cx - barW / 2;
  const yTop = y(Math.max(value, 0));
  const yBot = y(Math.min(value, 0));
  const h = Math.max(yBot - yTop, 0.5);
  const rect = svgEl('rect', {{x: x0, y: yTop, width: barW, height: h, class: cls, rx: 2}});
  rect.addEventListener('mouseenter', (ev) => showTooltip(ev, d));
  rect.addEventListener('mousemove', positionTooltip);
  rect.addEventListener('mouseleave', () => tooltip.style.display = 'none');
  svg.appendChild(rect);
}}

DATA.forEach((d, i) => {{
  if (d.contrib_stmt >= 0 && d.contrib_speech >= 0) {{
    addSegment(i, d, d.contrib_stmt, 'bar-stmt');
    const cx = xCenter(i);
    const x0 = cx - barW / 2;
    const yTop = y(d.contrib_stmt + d.contrib_speech);
    const yBot = y(d.contrib_stmt);
    const rect = svgEl('rect', {{x: x0, y: yTop, width: barW, height: Math.max(yBot - yTop, 0.5), class: 'bar-speech', rx: 2}});
    rect.addEventListener('mouseenter', (ev) => showTooltip(ev, d));
    rect.addEventListener('mousemove', positionTooltip);
    rect.addEventListener('mouseleave', () => tooltip.style.display = 'none');
    svg.appendChild(rect);
  }} else if (d.contrib_stmt <= 0 && d.contrib_speech <= 0) {{
    addSegment(i, d, d.contrib_stmt, 'bar-stmt');
    const cx = xCenter(i);
    const x0 = cx - barW / 2;
    const yTop = y(d.contrib_stmt);
    const yBot = y(d.contrib_stmt + d.contrib_speech);
    const rect = svgEl('rect', {{x: x0, y: yTop, width: barW, height: Math.max(yBot - yTop, 0.5), class: 'bar-speech', rx: 2}});
    rect.addEventListener('mouseenter', (ev) => showTooltip(ev, d));
    rect.addEventListener('mousemove', positionTooltip);
    rect.addEventListener('mouseleave', () => tooltip.style.display = 'none');
    svg.appendChild(rect);
  }} else {{
    addSegment(i, d, d.contrib_stmt, 'bar-stmt');
    addSegment(i, d, d.contrib_speech, 'bar-speech');
  }}
  const cx = xCenter(i);
  svg.appendChild(svgEl('circle', {{cx: cx, cy: y(d.combined), r: 3, class: 'combined-dot'}}));
}});

function showTooltip(ev, d) {{
  const fmt = (v) => (v === null ? 'n/a' : v.toFixed(3));
  let html = `<div style="font-weight:600">${{d.date}}</div>`;
  html += `<div style="color:var(--text-secondary); margin-bottom:4px;">${{d.title}}</div>`;
  html += `<div>Statement: index ${{fmt(d.avg_stmt)}}, contribution ${{d.contrib_stmt.toFixed(3)}}</div>`;
  html += `<div>Speeches in window: ${{d.n_speech}}, average index ${{fmt(d.avg_speech)}}, contribution ${{d.contrib_speech.toFixed(3)}}</div>`;
  html += `<div style="margin-top:4px; font-weight:600;">Combined: ${{d.combined.toFixed(3)}}</div>`;
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
