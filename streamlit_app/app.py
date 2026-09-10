"""
Central Bank Hawkish/Dovish Classifier — dictionary method vs. LLM method,
side by side.

Paste a paragraph of central bank communication (an MPC statement, a
speech excerpt, an FOMC/ECB/BoE press release — anything) and see it
scored two ways: the Henry (2008) bag-of-words dictionary (replicating
Erasmus & Hollander (2020) / du Rand et al. (2021) for the South African
Reserve Bank, from the companion repo github.com/MateusGodinho/sarb-hawkish-dove),
and a calibrated LLM (Claude Haiku 4.5) that reads the whole passage for
stance instead of counting words — see ../README.md for that method's
calibration and validation against the SARB corpus.

This is the demo companion to this project (a sequel to the dictionary-based
sarb-hawkish-dove repo, replacing the word-count method with a calibrated
LLM classifier): https://mateusgodinho.github.io/articles/sarb-llm-index /
https://github.com/MateusGodinho/sarb-hawkish-dove-llm.

Self-contained: only depends on `lexicon_henry.py` and `llm_prompt.py`
(mirrored from ../scripts/llm_prompt.py) in this same folder, plus
`streamlit` and `anthropic`. Ready to deploy as-is on Streamlit Community
Cloud (main file: app.py) — the LLM column needs an `ANTHROPIC_API_KEY`
set as a Streamlit secret; without one it degrades gracefully to a
"not configured" note rather than erroring.
"""

from __future__ import annotations

import html
import os
import re
import time

import streamlit as st

from lexicon_henry import NEGATIVE_WORDS, POSITIVE_WORDS
from llm_prompt import SYSTEM_PROMPT, StanceScore

_WORD_RE = re.compile(r"[a-zA-Z]+")

LLM_MODEL = "claude-haiku-4-5"
MAX_CHARS_FOR_LLM = 8000  # keeps a single call's cost bounded regardless of paste size
MIN_SECONDS_BETWEEN_LLM_CALLS = 3  # light per-session throttle, this is a shared free demo

EXAMPLE_HAWKISH = (
    "The Committee judges that inflation risks remain tilted to the upside. "
    "Given the strength of recent growth and the continued increase in price "
    "pressures, the Committee agreed that a firmer policy stance is warranted "
    "to keep inflation expectations anchored."
)

EXAMPLE_DOVISH = (
    "Growth has weakened further and downside risks have increased. Given "
    "the deteriorating outlook and the decline in underlying demand, the "
    "Committee judged that a more accommodative stance would support the "
    "recovery without jeopardising the inflation target."
)


def score_text(text: str) -> dict:
    """Identical logic to scripts/score_henry.py's score_text() — see that
    module for the full methodology note. Reproduced here so this app has
    no dependency on the rest of the repo."""
    tokens = _WORD_RE.findall(text.lower())

    pos_hits: dict[str, int] = {}
    neg_hits: dict[str, int] = {}
    for tok in tokens:
        if tok in POSITIVE_WORDS:
            pos_hits[tok] = pos_hits.get(tok, 0) + 1
        elif tok in NEGATIVE_WORDS:
            neg_hits[tok] = neg_hits.get(tok, 0) + 1

    hawkish_count = sum(pos_hits.values())
    dovish_count = sum(neg_hits.values())
    total = hawkish_count + dovish_count
    index = 2 * (hawkish_count - dovish_count) / total if total else 0.0

    return {
        "index": round(index, 3),
        "hawkish_count": hawkish_count,
        "dovish_count": dovish_count,
        "total_words": len(tokens),
        "hawkish_hits": pos_hits,
        "dovish_hits": neg_hits,
    }


def label_for(index: float) -> tuple[str, str]:
    """Returns (label, color) for a given index value in [-2, 2]."""
    if index >= 0.75:
        return "Strongly hawkish", "#d95926"
    if index >= 0.15:
        return "Leaning hawkish", "#eb6834"
    if index > -0.15:
        return "Neutral", "#898781"
    if index > -0.75:
        return "Leaning dovish", "#1baf7a"
    return "Strongly dovish", "#199e70"


def llm_label_for(score: float) -> tuple[str, str]:
    """Same -2..+2 scale as the dictionary method, but the LLM score is a
    holistic read, not a word count -- thresholds picked to match the
    rubric's own anchors (+/-1 = "leans", +/-2 = "strongly")."""
    if score >= 1.5:
        return "Strongly hawkish", "#d95926"
    if score >= 0.5:
        return "Leaning hawkish", "#eb6834"
    if score > -0.5:
        return "Neutral", "#898781"
    if score > -1.5:
        return "Leaning dovish", "#1baf7a"
    return "Strongly dovish", "#199e70"


@st.cache_resource
def _anthropic_client():
    import anthropic

    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def score_with_llm(text: str) -> StanceScore:
    client = _anthropic_client()
    response = client.messages.parse(
        model=LLM_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text[:MAX_CHARS_FOR_LLM]}],
        output_format=StanceScore,
    )
    return response.parsed_output


def highlight_html(text: str) -> str:
    """Wraps hawkish/dovish word matches in colored <span>s for display."""
    tokens = re.findall(r"[a-zA-Z]+|[^a-zA-Z]+", text)
    out = []
    for tok in tokens:
        low = tok.lower()
        if low in POSITIVE_WORDS:
            out.append(f'<span style="background:#eb683433;border-radius:3px;">{html.escape(tok)}</span>')
        elif low in NEGATIVE_WORDS:
            out.append(f'<span style="background:#1baf7a33;border-radius:3px;">{html.escape(tok)}</span>')
        else:
            out.append(html.escape(tok))
    return "".join(out)


st.set_page_config(page_title="Hawkish/Dovish Classifier", page_icon="🦅", layout="wide")

st.title("🦅 Central Bank Hawkish/Dovish Classifier")
st.caption(
    "Two ways of scoring central bank communication, side by side: the Henry (2008) / "
    "Erasmus & Hollander (2020) word-count dictionary, and a calibrated LLM (Claude "
    "Haiku 4.5) that reads for stance in context — both used on the full SARB corpus in a "
    "[replication of du Rand et al. (2021), extended with an LLM comparison](#) "
    "([code + data](#))."
)

col_input, col_examples = st.columns([3, 1])
with col_examples:
    st.markdown("**Try an example:**")
    if st.button("Hawkish example"):
        st.session_state["text_input"] = EXAMPLE_HAWKISH
    if st.button("Dovish example"):
        st.session_state["text_input"] = EXAMPLE_DOVISH

with col_input:
    text = st.text_area(
        "Paste a statement, speech excerpt, or press release:",
        key="text_input",
        height=180,
        placeholder="e.g. an FOMC statement, an ECB press conference excerpt, an MPC statement...",
    )

analyze = st.button("Analyze", type="primary")

if analyze and text.strip():
    result = score_text(text)
    label, color = label_for(result["index"])

    left, right = st.columns(2)

    with left:
        st.subheader("📖 Dictionary method (Henry 2008)")
        st.markdown(
            f'<div style="font-size:2.2rem;font-weight:700;color:{color};">'
            f'{result["index"]:+.2f} &nbsp; <span style="font-size:1.1rem;font-weight:600;">{label}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.caption("Scale: −2 (most dovish) to +2 (most hawkish). Formula: 2 × (hawkish − dovish) / (hawkish + dovish).")

        m1, m2, m3 = st.columns(3)
        m1.metric("Hawkish words", result["hawkish_count"])
        m2.metric("Dovish words", result["dovish_count"])
        m3.metric("Total words", result["total_words"])

        if result["total_words"] == 0:
            st.warning("No text to analyze.")
        elif result["hawkish_count"] + result["dovish_count"] == 0:
            st.info("No dictionary words matched — the index defaults to 0.0 (neutral) by construction, "
                    "not necessarily because the text itself is neutral in tone.")

        st.markdown("**Matched text** (orange = hawkish, green = dovish):")
        st.markdown(
            f'<div style="line-height:1.7;padding:12px;border:1px solid #33333322;border-radius:8px;">'
            f"{highlight_html(text)}</div>",
            unsafe_allow_html=True,
        )

        if result["hawkish_hits"] or result["dovish_hits"]:
            with st.expander("Word-level breakdown"):
                if result["hawkish_hits"]:
                    st.write("Hawkish:", result["hawkish_hits"])
                if result["dovish_hits"]:
                    st.write("Dovish:", result["dovish_hits"])

    with right:
        st.subheader("🤖 LLM classifier (Claude Haiku 4.5)")

        client = _anthropic_client()
        if client is None:
            st.markdown(
                '<div style="padding:24px;border:1px dashed #89878166;border-radius:8px;'
                'color:#898781;text-align:center;">'
                "⚙️ <b>Not configured</b><br><br>"
                "This deployment doesn't have an <code>ANTHROPIC_API_KEY</code> set, so the "
                "LLM column is disabled. The dictionary method on the left still works fully."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            last_call = st.session_state.get("last_llm_call", 0.0)
            elapsed = time.time() - last_call
            if elapsed < MIN_SECONDS_BETWEEN_LLM_CALLS:
                st.info(f"This is a shared free demo — please wait {MIN_SECONDS_BETWEEN_LLM_CALLS - elapsed:.0f}s before the next LLM call.")
            else:
                try:
                    with st.spinner("Reading the full passage for stance…"):
                        result = score_with_llm(text)
                    st.session_state["last_llm_call"] = time.time()

                    llm_label, llm_color = llm_label_for(result.score)
                    st.markdown(
                        f'<div style="font-size:2.2rem;font-weight:700;color:{llm_color};">'
                        f'{result.score:+.2f} &nbsp; <span style="font-size:1.1rem;font-weight:600;">{llm_label}</span>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.caption("Scale: −2 (most dovish) to +2 (most hawkish). Whole-passage read, not a word count.")

                    if not result.on_topic:
                        st.warning("Flagged as **not primarily about monetary policy stance** — the score above is not a forced directional read.")

                    st.markdown("**Most stance-relevant quote:**")
                    st.markdown(
                        f'<div style="line-height:1.6;padding:12px;border:1px solid #33333322;'
                        f'border-radius:8px;font-style:italic;">"{html.escape(result.quote)}"</div>',
                        unsafe_allow_html=True,
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Couldn't get a reading from the model: {exc}")

elif analyze:
    st.warning("Paste some text first.")

st.divider()
st.caption(
    "Left: a simple bag-of-words dictionary lookup — no context, no negation-handling, "
    "no sarcasm-detection. Right: a calibrated LLM reading the whole passage for stance, "
    "same rubric used to score the full SARB corpus (see ../README.md) — this instance is "
    "hosted on the project owner's own API usage, shared across everyone trying the demo, "
    "hence the short cooldown between LLM calls. Neither is investment or policy advice, "
    "and neither should be the sole basis for any decision. "
    "Methodology and full results: [Reading the SARB With an LLM]"
    "(https://mateusgodinho.github.io/articles/sarb-llm-index). "
    "Code: [sarb-hawkish-dove-llm](https://github.com/MateusGodinho/sarb-hawkish-dove-llm). "
    "Dictionary baseline from the companion project: "
    "[sarb-hawkish-dove](https://github.com/MateusGodinho/sarb-hawkish-dove)."
)
