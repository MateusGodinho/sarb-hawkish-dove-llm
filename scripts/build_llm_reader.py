import pathlib

base = pathlib.Path(__file__).resolve().parent / "fonts"

b64 = {}
for name in ["plex-serif-600", "plex-sans-400", "plex-sans-600", "plex-mono-500", "plex-mono-600"]:
    b64[name] = (base / f"{name}.b64").read_text().strip()

css = f"""
@font-face {{ font-family: "Plex Serif"; font-style: normal; font-weight: 600; src: url(data:font/woff2;base64,{b64['plex-serif-600']}) format('woff2'); }}
@font-face {{ font-family: "Plex Sans"; font-style: normal; font-weight: 400; src: url(data:font/woff2;base64,{b64['plex-sans-400']}) format('woff2'); }}
@font-face {{ font-family: "Plex Sans"; font-style: normal; font-weight: 600; src: url(data:font/woff2;base64,{b64['plex-sans-600']}) format('woff2'); }}
@font-face {{ font-family: "Plex Mono"; font-style: normal; font-weight: 500; src: url(data:font/woff2;base64,{b64['plex-mono-500']}) format('woff2'); }}
@font-face {{ font-family: "Plex Mono"; font-style: normal; font-weight: 600; src: url(data:font/woff2;base64,{b64['plex-mono-600']}) format('woff2'); }}

:root {{
  --bg: #eef1f4; --surface: #ffffff; --text: #17222f; --text-2: #4c5b6b; --muted: #8894a0;
  --border: rgba(23,34,47,0.11); --accent: #1f5a80; --accent-soft: rgba(31,90,128,0.12);
  --accent-ink: #ffffff; --hawk: #c1592f; --hawk-tint: rgba(193,89,47,0.13);
  --dove: #2f8f6c; --dove-tint: rgba(47,143,108,0.13);
  --shadow-lg: 0 2px 4px rgba(23,34,47,0.06), 0 14px 28px rgba(23,34,47,0.10);
  --radius: 18px;
  --font-body: "Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-display: "Plex Serif", Georgia, serif;
  --font-mono: "Plex Mono", ui-monospace, "SF Mono", Consolas, monospace;
  color-scheme: light;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #10161d; --surface: #182028; --text: #eef2f6; --text-2: #b3c0cc; --muted: #74838f;
    --border: rgba(255,255,255,0.1); --accent: #6cb2dd; --accent-soft: rgba(108,178,221,0.16);
    --accent-ink: #10161d; --hawk: #e8935f; --hawk-tint: rgba(232,147,95,0.16);
    --dove: #5cc79e; --dove-tint: rgba(92,199,158,0.16);
    --shadow-lg: 0 4px 12px rgba(0,0,0,0.35), 0 20px 48px rgba(0,0,0,0.4);
    color-scheme: dark;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #10161d; --surface: #182028; --text: #eef2f6; --text-2: #b3c0cc; --muted: #74838f;
  --border: rgba(255,255,255,0.1); --accent: #6cb2dd; --accent-soft: rgba(108,178,221,0.16);
  --accent-ink: #10161d; --hawk: #e8935f; --hawk-tint: rgba(232,147,95,0.16);
  --dove: #5cc79e; --dove-tint: rgba(92,199,158,0.16);
  --shadow-lg: 0 4px 12px rgba(0,0,0,0.35), 0 20px 48px rgba(0,0,0,0.4);
  color-scheme: dark;
}}

* {{ box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: var(--font-body); line-height: 1.5; -webkit-font-smoothing: antialiased; }}
.wrap {{ max-width: 720px; margin: 0 auto; padding: 56px 24px 72px; }}
.kicker {{ display:flex; align-items:center; gap:9px; font-family: var(--font-mono); font-size:12.5px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color: var(--accent); margin-bottom:16px; }}
h1 {{ font-family: var(--font-display); font-size: clamp(28px,5vw,38px); font-weight:600; letter-spacing:-0.01em; line-height:1.15; text-wrap:balance; margin:0 0 14px; }}
.lede {{ font-size:16px; color: var(--text-2); max-width:58ch; margin:0 0 40px; }}
.lede a {{ color: var(--accent); text-decoration:none; border-bottom:1px solid transparent; }}
.lede a:hover {{ border-bottom-color: currentColor; }}
.card {{ background: var(--surface); border-radius: var(--radius); border-top: 3px solid var(--accent); box-shadow: var(--shadow-lg); padding:24px; margin-bottom:22px; }}
.card-label {{ font-family: var(--font-mono); font-size:11.5px; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; color: var(--muted); margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; }}
textarea {{ width:100%; min-height:150px; resize:vertical; border:1px solid transparent; border-radius:14px; background: var(--bg); color: var(--text); font-family: inherit; font-size:14.5px; line-height:1.65; padding:16px; }}
textarea:focus-visible {{ outline:none; border-color: var(--accent); background: var(--surface); box-shadow: 0 0 0 3px var(--accent-soft); }}
textarea::placeholder {{ color: var(--muted); }}
.row {{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:16px; flex-wrap:wrap; }}
.examples {{ display:flex; gap:8px; flex-wrap:wrap; }}
button {{ font-family: var(--font-body); font-size:13.5px; cursor:pointer; border-radius:999px; border:1px solid var(--border); background: var(--surface); color: var(--text-2); padding:9px 15px; transition: background .15s ease, color .15s ease, transform .1s ease; }}
button:hover {{ background: var(--accent-soft); color: var(--text); }}
button:active {{ transform: scale(0.97); }}
button:disabled {{ opacity:0.5; cursor:not-allowed; }}
.btn-primary {{ background: var(--accent); border-color: var(--accent); color: var(--accent-ink); font-weight:600; padding:11px 20px; }}
.btn-primary:hover {{ filter: brightness(1.08); color: var(--accent-ink); }}
#result {{ display:none; }}
#result.show {{ display:block; animation: rise .32s cubic-bezier(.2,.8,.3,1); }}
@keyframes rise {{ from {{ opacity:0; transform: translateY(8px); }} to {{ opacity:1; transform: translateY(0); }} }}
.readout {{ display:flex; align-items:baseline; gap:14px; margin-bottom:6px; }}
.score {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size:40px; font-weight:600; letter-spacing:-0.01em; }}
.label {{ font-size:14.5px; font-weight:600; }}
.gauge {{ position:relative; height:10px; border-radius:999px; background: linear-gradient(90deg, var(--dove) 0%, var(--bg) 48%, var(--bg) 52%, var(--hawk) 100%); margin:22px 0 8px; }}
.gauge-marker {{ position:absolute; top:50%; width:18px; height:18px; border-radius:50%; background: var(--surface); border:3px solid var(--text); transform: translate(-50%,-50%); transition: left .4s cubic-bezier(.2,.8,.3,1); box-shadow: 0 1px 2px rgba(23,34,47,.05), 0 0 0 5px var(--bg); }}
.gauge-ticks {{ display:flex; justify-content:space-between; font-family: var(--font-mono); font-size:11px; color: var(--muted); margin-bottom:18px; }}
.quote-box {{ font-size:14.5px; line-height:1.8; color: var(--text-2); border-top:1px solid var(--border); padding-top:20px; font-style:italic; }}
.badge {{ display:inline-block; font-family: var(--font-mono); font-size:11px; font-weight:500; text-transform:uppercase; letter-spacing:.04em; border-radius:4px; padding:3px 9px; margin-top:14px; }}
.badge.off {{ background: var(--hawk-tint); color: var(--hawk); }}
.hint {{ font-size:12.5px; color: var(--muted); }}
.error-box {{ font-size:13.5px; color: var(--hawk); background: var(--hawk-tint); border-radius:10px; padding:12px 16px; margin-top:12px; }}
.about {{ margin-top:44px; padding-top:26px; border-top:1px solid var(--border); font-size:13.5px; color: var(--text-2); display:flex; flex-direction:column; gap:10px; }}
.about strong {{ color: var(--text); }}
.about a {{ color: var(--accent); }}
.about a:hover {{ text-decoration:underline; }}
"""

html = f"""<title>SARB LLM Reader</title>
<style>{css}</style>

<div class="wrap">
  <div class="kicker">
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="20" height="20">
      <path d="M12 3c3 3 7 3.5 9 3-1 4-3 6-9 9-6-3-8-5-9-9 2 0.5 6 0 9-3Z" fill="var(--hawk)" opacity="0.85"/>
      <path d="M12 3c-3 3-7 3.5-9 3 1 4 3 6 9 9V3Z" fill="var(--dove)" opacity="0.85"/>
    </svg>
    Central bank communication tone reader — LLM edition
  </div>
  <h1>What does an LLM make of this SARB communication?</h1>
  <p class="lede">
    Paste a real SARB statement or speech excerpt and Claude reads it whole -- for meaning,
    not word counts -- using the exact rubric calibrated for
    <a href="https://mateusgodinho.github.io/articles/sarb-communication" target="_blank" rel="noopener">this project's LLM-based hawkish/dovish index</a>.
    Runs on your own Claude usage, not ours -- see <em>How this works</em> below.
  </p>

  <div class="card">
    <div class="card-label"><span>Text</span><span id="charCount">0 characters</span></div>
    <textarea id="input" placeholder="Paste a SARB statement, speech excerpt, or your own draft of central-bank-style language here…"></textarea>
    <div class="row">
      <div class="examples">
        <button type="button" id="exHawk">Hawkish example</button>
        <button type="button" id="exLeanHawk">Lean hawkish example</button>
        <button type="button" id="exNeutral">Neutral example</button>
        <button type="button" id="exLeanDove">Lean dovish example</button>
        <button type="button" id="exDove">Dovish example</button>
        <button type="button" id="clearBtn">Clear</button>
      </div>
      <button type="button" class="btn-primary" id="analyzeBtn">Analyze →</button>
    </div>
  </div>

  <div class="card" id="result">
    <div class="card-label"><span>Result</span><span id="tierUsed"></span></div>
    <div class="readout">
      <span class="score" id="scoreOut">+0.00</span>
      <span class="label" id="labelOut">—</span>
    </div>
    <div class="gauge"><div class="gauge-marker" id="gaugeMarker" style="left:50%"></div></div>
    <div class="gauge-ticks"><span>−2 dovish</span><span>0</span><span>+2 hawkish</span></div>
    <div id="offTopicBadge"></div>
    <div class="quote-box" id="quoteOut"></div>
  </div>

  <div id="unavailableNote" class="error-box" style="display:none;">
    This artifact's "ask Claude" feature isn't available in this view -- open it directly on
    claude.ai to try the live reader.
  </div>

  <div class="about">
    <p><strong>How this works.</strong> This page asks Claude directly -- on <em>your</em> Claude
    account and usage, not a key belonging to this project -- using the same prompt (rubric,
    anchors, few-shot calibration) validated against 15 held-out real SARB documents and two
    hand-built negation tests before it was run over the full 675-document corpus. The first
    request will ask your permission.</p>
    <p>Full methodology, the validation results, and the code:
    <a href="https://github.com/MateusGodinho/sarb-hawkish-dove" target="_blank" rel="noopener">github.com/MateusGodinho/sarb-hawkish-dove</a>.</p>
  </div>
</div>

<script>
  const SYSTEM_PROMPT = `You are analyzing central bank communication to determine monetary
policy stance. Score the text on a scale from -2 (most dovish) to +2 (most hawkish),
based on the OVERALL policy stance being communicated -- not on counting individual
words or keywords.

Scale anchors:
+2  Explicit, unambiguous signal of monetary tightening -- e.g. committed to further
    rate hikes, inflation risks dominate the outlook, policy must stay restrictive.
+1  Leans hawkish -- concerned about inflation, cautious about easing, but not
    committing to aggressive tightening.
 0  Balanced / neutral -- growth and inflation risks roughly balanced, no clear
    directional signal, or the text does not address policy stance at all.
-1  Leans dovish -- concerned about growth or downside risks, open to easing, but not
    committing to aggressive cuts.
-2  Explicit, unambiguous signal of monetary easing -- e.g. committed to further rate
    cuts, growth risks dominate the outlook, policy must stay accommodative.

Critical -- read for meaning and direction, not vocabulary: a sentence like "growth has
weakened sharply" is DOVISH even though it contains the word "growth." A sentence like
"the risk that inflation runs too hot" is HAWKISH even though it contains the word "risk."

If the text is not primarily about monetary policy stance (e.g. a speech about payment
systems, financial inclusion, artificial intelligence, or an unrelated topic), set
on_topic to false and score it close to 0 -- do not force a directional read.

Reply with ONLY a JSON object, no other text: {{"score": number, "label": string, "quote": string, "on_topic": boolean}}
"label" must be one of: "strongly hawkish", "leaning hawkish", "neutral", "leaning dovish", "strongly dovish".
"quote" is the single sentence or short phrase that most justifies the score.

Text to analyze:
`;

  const EXAMPLES = {{
    hawk: "The Committee judged that further policy tightening was warranted. Underlying inflation remains too high, and recent data confirm continued strength in demand, with wage growth increasing and price pressures broadening rather than easing. The Committee raised the policy rate and expects borrowing costs to stay higher for longer, and judged that a firm and restrictive stance remains necessary until inflation returns durably to target.",
    leanHawk: "The Committee noted that inflation remains somewhat above target and that underlying price pressures have shown some persistence. While economic activity has been broadly resilient, the Committee will continue to monitor incoming data closely and remains prepared to act further should inflation risks intensify. The policy rate was left unchanged at this meeting.",
    neutral: "The Committee judged that risks to the inflation outlook are currently balanced. Growth has been broadly in line with expectations, and while some upside price pressures have emerged, they are expected to ease over the coming quarters as base effects fade. The Committee decided to keep the policy rate unchanged, noting that the current stance remains appropriate given the balance of risks on both sides.",
    leanDove: "The Committee observed that growth has slowed somewhat and that some downside risks to the outlook have emerged. Inflation continues to move gradually toward target, and wage pressures have moderated. While the Committee sees scope for the policy stance to become more supportive over time, it judged that a cautious, gradual approach remains appropriate for now, and left the policy rate unchanged.",
    dove: "The Committee judged that a markedly accommodative stance was warranted. Economic activity has slowed sharply, with soft demand and weak momentum across many sectors. The outlook has deteriorated amid heightened uncertainty, and the Committee cut the policy rate, noting that borrowing costs are likely to fall further as downside risks build."
  }};

  const $ = (id) => document.getElementById(id);
  const input = $("input");

  function updateCharCount() {{
    $("charCount").textContent = input.value.length + " characters";
  }}
  input.addEventListener("input", updateCharCount);

  function loadExample(key) {{
    input.value = EXAMPLES[key];
    updateCharCount();
    input.focus();
    $("result").classList.remove("show");
  }}
  $("exHawk").addEventListener("click", () => loadExample("hawk"));
  $("exLeanHawk").addEventListener("click", () => loadExample("leanHawk"));
  $("exNeutral").addEventListener("click", () => loadExample("neutral"));
  $("exLeanDove").addEventListener("click", () => loadExample("leanDove"));
  $("exDove").addEventListener("click", () => loadExample("dove"));
  $("clearBtn").addEventListener("click", () => {{
    input.value = "";
    updateCharCount();
    $("result").classList.remove("show");
    input.focus();
  }});

  function labelFor(idx) {{
    if (idx >= 1.5) return ["Strongly hawkish", "var(--hawk)"];
    if (idx >= 0.5) return ["Leaning hawkish", "var(--hawk)"];
    if (idx > -0.5) return ["Neutral", "var(--muted)"];
    if (idx > -1.5) return ["Leaning dovish", "var(--dove)"];
    return ["Strongly dovish", "var(--dove)"];
  }}

  const ERROR_COPY = {{
    not_granted: "You declined (or your organization blocks) letting this page ask Claude. Refresh to try again.",
    rate_limited: "Too many requests right now -- wait a moment and try again.",
    invalid_json: "Claude's reply couldn't be read as a score -- try again, or shorten the text.",
    prompt_too_large: "That text is too long for one request -- try a shorter excerpt.",
    refused: "Claude declined to analyze this text.",
    upstream_error: "Something went wrong on Claude's end -- try again.",
  }};

  let sampleFn = null;
  let analyzeBtn;

  async function init() {{
    analyzeBtn = $("analyzeBtn");
    if (!window.claude || !window.claude.use) {{
      $("unavailableNote").style.display = "block";
      analyzeBtn.disabled = true;
      return;
    }}
    sampleFn = await window.claude.use("sample");
    if (!sampleFn) {{
      $("unavailableNote").style.display = "block";
      analyzeBtn.disabled = true;
      return;
    }}
    analyzeBtn.addEventListener("click", analyze);
  }}

  async function analyze() {{
    const text = input.value.trim();
    if (!text || !sampleFn) {{ input.focus(); return; }}

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Thinking…";
    $("unavailableNote").style.display = "none";

    try {{
      const data = await sampleFn.json(SYSTEM_PROMPT + text, {{ modelTier: "quick" }});
      const idx = Math.max(-2, Math.min(2, Number(data.score) || 0));
      const [label, color] = labelFor(idx);

      $("scoreOut").textContent = (idx >= 0 ? "+" : "") + idx.toFixed(2);
      $("scoreOut").style.color = color;
      $("labelOut").textContent = label;
      $("labelOut").style.color = color;

      const pct = ((idx + 2) / 4) * 100;
      $("gaugeMarker").style.left = pct + "%";

      $("quoteOut").textContent = data.quote ? `"${{data.quote}}"` : "";
      $("offTopicBadge").innerHTML = data.on_topic === false
        ? '<span class="badge off">Not primarily about policy stance</span>'
        : "";
      $("tierUsed").textContent = "";

      $("result").classList.add("show");
    }} catch (e) {{
      const msg = ERROR_COPY[e.code] || "Something went wrong -- try again.";
      const box = document.createElement("div");
      box.className = "error-box";
      box.textContent = msg;
      $("result").parentElement.insertBefore(box, $("result"));
      setTimeout(() => box.remove(), 6000);
    }} finally {{
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze →";
    }}
  }}

  updateCharCount();
  init();
</script>
"""

out = pathlib.Path(__file__).resolve().parent.parent / "reports" / "llm-reader.html"
out.write_text(html, encoding="utf-8")
print("wrote", len(html), "chars to", out)
