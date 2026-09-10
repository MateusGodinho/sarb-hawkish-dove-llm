# Reading the SARB With an LLM

A sequel to [`sarb-hawkish-dove`](https://github.com/MateusGodinho/sarb-hawkish-dove):
same corpus, same 173 MPC statements and 502 English-language speeches, but scored by a
calibrated LLM (Claude Haiku 4.5) instead of a Henry (2008) word-count dictionary. That
project's Roadmap flagged this as *"a scaffolded but not-yet-run LLM classifier"* — this
repo is that classifier, run, calibrated, and validated against the same 173 meetings.

Full write-up (why this exists, what it fixes, what it doesn't):
**[Reading the SARB With an LLM: Context Always Matters](https://mateusgodinho.github.io/articles/sarb-llm-index)**.

**Just want to try the method, no setup?** [Live demo](https://sarb-hawkish-dove-llm-59qcmhguxqvpvab9kldq2q.streamlit.app/) --
paste any central-bank text and see it scored both ways, side by side (the dictionary
method and this one). Source: [`streamlit_app/`](streamlit_app/) — see [Try it
yourself](#try-it-yourself-no-python-required) below. (A [Claude Artifact
version](https://claude.ai/code/artifact/b905c07a-f730-44f9-b705-f38de8bd6fff) of the LLM
reader also exists, but Anthropic's sharing rules don't let artifacts that call Claude be
shared with "anyone with the link" — the Streamlit demo is the actual public option.)

## Abstract

The dictionary method's index (see the [companion repo](https://github.com/MateusGodinho/sarb-hawkish-dove))
tracks real policy directionally but runs structurally hot — even rate cuts average a
positive (hawkish) score, because a bag-of-words dictionary can't tell "growth has
weakened sharply" (dovish) from "growth" the keyword (scored hawkish), or "the risk that
inflation runs too hot" (hawkish) from "risk" the keyword (scored dovish). This project
replaces that dictionary with Claude Haiku 4.5, prompted with a fixed -2..+2 rubric and
calibrated by hand against 15 real documents and two adversarial sentences before touching
the full corpus, plus an `on_topic` flag that lets the model exclude speeches that aren't
really about policy stance at all (43% of the speech corpus, 215 of 502) instead of scoring
them as false directional extremes.

## Key results

**1. The skew goes away.** Splitting all 173 meetings by what the MPC actually did:

| | hike | hold | cut |
|---|---|---|---|
| Henry (dictionary) | +0.77 | +0.63 | +0.38 |
| LLM | **+1.01** | **+0.19** | **−0.98** |

The dictionary never goes negative. The LLM index crosses zero in the right direction for
every bucket, and correlation with the actual size of the rate move (bps) moves the same
way: r = 0.48 → 0.80 for the combined index, r = 0.49 → 0.86 for statements alone.

![SARB combined index: Henry dictionary vs. LLM classifier, by meeting](reports/henry-vs-llm-index.html)
*(open directly in a browser — GitHub's file preview renders raw HTML as text, not as a page)*

**2. On the meeting that motivated the whole series.** Henry reads July 2026 at +0.78; the
LLM combined index reads it at +0.53 — still hawkish of neutral, but markedly more
measured, closer to how that meeting's communication was actually described at the time
(hawkish on the external backdrop, benign domestically).

**3. Speech contribution shrinks, mostly for a calibration reason, not just a filtering
one.** The on-topic filter alone cuts the average speeches counted per meeting window from
2.37 (Henry) to 1.31 (LLM). But that's the smaller effect: Henry's mean score across every
speech was +0.756; the LLM's mean across on-topic speeches only was +0.397 — roughly half,
even after the filter already removed the speeches with nothing to do with policy. The
excluded speeches scored a mean of +0.036 (near zero, not extreme), so removing them should
have pulled the remaining average up, not down. The larger driver is the same calibration
difference already visible on the statements side.

Interactive chart: [`reports/llm-contribution-full.html`](reports/llm-contribution-full.html)
(statement vs. speech contribution by meeting, LLM version of the dictionary project's chart).

## Methodology summary

| | This project |
|---|---|
| Corpus | Same 173 MPC statements + 502 English-language speeches as the dictionary project — copied, not re-scraped, into `data/` |
| Model | Claude Haiku 4.5, chosen over Sonnet 5 after calibration (see below) |
| Scoring | Whole-document read, -2 (most dovish) to +2 (most hawkish), fixed rubric anchors given in the prompt — see [`scripts/llm_prompt.py`](scripts/llm_prompt.py) |
| Output | Claude's structured-output mode (`output_config` + JSON schema), server-validated — never an unparseable reply |
| Calibration | 15 real documents spanning known extremes + 2 hand-built negation sentences, scored by both Haiku 4.5 and Sonnet 5, reviewed by hand against what actually happened at each meeting — see [`scripts/calibrate_llm_prompt.py`](scripts/calibrate_llm_prompt.py) and `data/processed/calibration/round_1.csv` |
| Full run | All 675 documents, submitted as one job via the Messages Batches API — see [`scripts/score_llm.py`](scripts/score_llm.py) |
| `on_topic` flag | A field the dictionary method has no equivalent for: excludes documents that aren't primarily about policy stance (banknote launches, payment-system addresses, green-finance speeches) instead of scoring them as directional extremes on incidental vocabulary |
| Combined index | Same per-meeting decomposition as the dictionary project (`combined = contribution from the statement + contribution from that window's on-topic speeches`), recomputed here with the LLM scores — see [`scripts/build_combined_index_llm.py`](scripts/build_combined_index_llm.py) |

Calibration itself was a real decision point, not a formality: both models passed the two
negation tests cleanly, and the only case where they disagreed was the July 2026 meeting
itself — Haiku's reading (weighing the case for holding against the case for hiking) held
up better on review than Sonnet's, which leaned harder into the hawkish scenario. That
single differentiating case settled the model choice for the full run.

## Repository structure

```
sarb-hawkish-dove-llm/
├── README.md
├── requirements.txt
├── streamlit_app/                public demo, both methods side by side (self-contained, deployable as-is)
│   ├── app.py
│   ├── lexicon_henry.py            mirrored from the companion repo, for the dictionary column
│   ├── llm_prompt.py               mirrored from scripts/llm_prompt.py, for the LLM column
│   └── requirements.txt
├── scripts/                      one file per pipeline step
│   ├── config.py                   every shared file path
│   ├── llm_prompt.py               the rubric, calibration few-shot examples, and StanceScore schema (shared by calibration + full run)
│   ├── calibration_set.json        the 15 real documents + 2 adversarial sentences used to calibrate
│   ├── calibrate_llm_prompt.py     runs the calibration set through both candidate models
│   ├── score_llm.py                the full 675-document batch run (submit / wait / fetch)
│   ├── build_combined_index_llm.py per-meeting combined index from the LLM scores
│   ├── validate_llm_index.py       by-decision means + correlation with bps change, Henry vs. LLM
│   ├── build_llm_contribution_chart.py  the statement/speech contribution chart
│   ├── build_henry_vs_llm_chart.py      the direct Henry-vs-LLM comparison chart
│   ├── build_llm_reader.py         generates the "SARB LLM Reader" Claude Artifact (self-contained HTML, IBM Plex fonts inlined from fonts/)
│   └── fonts/                      base64 IBM Plex font assets used by build_llm_reader.py
├── data/
│   ├── raw/                        scraped indices + the official policy-rate series (copied from the companion repo)
│   ├── raw_texts/                   full text of every statement and speech (copied, for manual audit)
│   └── processed/
│       ├── statements_dataset.json / speeches_dataset.json    corpus metadata (copied)
│       ├── scores_henry.csv / speeches_scores_henry.csv        dictionary-method baseline (copied, not recomputed)
│       ├── combined_index_by_meeting.csv                       dictionary-method combined index (copied)
│       ├── scores_llm_statements.csv / scores_llm_speeches.csv 675 rows: score, label, quote, on_topic per document
│       ├── combined_index_llm_by_meeting.csv                   this project's combined index
│       └── calibration/round_1.csv                             the 15+2 calibration documents scored by both candidate models
└── reports/                       3 interactive HTML artifacts (open directly in a browser)
    ├── henry-vs-llm-index.html
    ├── llm-contribution-full.html
    └── llm-reader.html             source for the Claude Artifact reader
```

## Installation & usage

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...   # only needed to re-run calibration or the full scoring batch
cd scripts
```

The processed CSVs in `data/processed/` are already the output of a completed run, so
charts and validation can be regenerated without an API key:

```bash
python build_combined_index_llm.py
python validate_llm_index.py
python build_llm_contribution_chart.py
python build_henry_vs_llm_chart.py
python build_llm_reader.py
```

Re-running the scoring itself (calibration or the full batch) needs `ANTHROPIC_API_KEY`:

```bash
python calibrate_llm_prompt.py --round 2          # re-run calibration on both models
python score_llm.py --wait                        # submit the full batch and block until done
python score_llm.py --status <BATCH_ID>           # check on a submitted batch
python score_llm.py --fetch <BATCH_ID>            # pull results once the batch is done
```

## Try it yourself, no Python required

Live: [sarb-hawkish-dove-llm-59qcmhguxqvpvab9kldq2q.streamlit.app](https://sarb-hawkish-dove-llm-59qcmhguxqvpvab9kldq2q.streamlit.app/).
[`streamlit_app/`](streamlit_app/) is a small web app: paste in a paragraph from any
central bank (an FOMC statement, an ECB speech, anything), click a button, and see it
scored hawkish/dovish two ways side by side — the Henry dictionary (always on) and the
calibrated LLM (Claude Haiku 4.5, on if the deployment has an `ANTHROPIC_API_KEY`). To run
it on your own computer:

```bash
cd streamlit_app
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...   # optional -- omit and the LLM column just says "not configured"
streamlit run app.py
```

The public deployment linked from the article runs on the project owner's own API key, not
the visitor's — a shared free demo, so it has a short per-session cooldown between LLM
calls rather than a hard usage limit.

## Methodology & AI Usage

Like the root project, this one was built with Claude as an active collaborator, not just
for drafting text:

- **Prompt and rubric design**: the -2..+2 scale, its anchors, and the negation examples
  were iterated against 15 real documents chosen to span known extremes, plus two
  hand-built sentences designed to break a word-count method. The Haiku-vs-Sonnet 4.5
  model choice came down to one differentiating case (the July 2026 meeting) reviewed by
  hand, not a benchmark score.
- **Batches API engineering**: two real bugs were hit and fixed before the full run —
  `custom_id` exceeding the API's 64-character limit for long speech filenames (fixed with
  short sequential IDs plus a side lookup file), and a first submission that errored on
  every one of 675 requests from a malformed `output_config` (missing a nesting level),
  caught by testing one live call before resubmitting.
- **Charts and the reader demo**: built to match the root project's visual system, then
  iterated against direct testing — a labelling bug in the reader (score thresholds tuned
  for a normalized -1..1 scale instead of the actual -2..2 one) was only caught because it
  was tested live, not assumed correct from the code.
- **The public Streamlit demo**: filled in a "coming soon" placeholder already present in
  the root project's `streamlit_app/`, then deployed through a real troubleshooting
  session (a missing GitHub OAuth repo-access scope, a wrong main-file-path setting, and a
  stale app-slug cache) resolved interactively rather than guessed at.
- **Writing**: the article and this README were drafted from verified results and revised
  through several rounds of direct feedback — including a citation-fidelity check against
  the primary sources for each paper referenced (full-text verification for two, secondary
  summaries only for the paper eventually left out of the final draft when that
  distinction mattered).

## Known limitations

- **This is one run, not an average of several.** LLM output isn't fully deterministic even
  at low temperature; a second run would likely shift individual scores by a few tenths
  without changing the picture above.
- **The Haiku-over-Sonnet call rests on a single differentiating case** in calibration
  (July 2026), not a large sample — a reasonable bet, not a proof.
- **The `on_topic` flag was spot-checked on a sample of exclusions**, not audited across
  all 215.
- **The model is a moving target.** Pin the exact version if you rerun this — "the same
  prompt" stops being the same experiment when the model behind it changes.
- **This calibration is SARB's, not a general-purpose one.** The anchors, the examples, and
  the July 2026 tie-break were all chosen by reading SARB's own communication style.
  Pointing this same prompt at the Fed, the ECB, or any other central bank wouldn't
  transfer cleanly — each would need its own calibration pass against its own history
  first.
- **Private communication is invisible to this method, and always will be.** SARB
  officials give remarks at private events, closed-door briefings, and calls that never
  become a public transcript. That material would very plausibly sharpen what the model
  has learned about how these specific speakers actually talk, but there's no path to
  recovering it — it was never public to begin with.

## Related project

[`sarb-hawkish-dove`](https://github.com/MateusGodinho/sarb-hawkish-dove) — the original
replication of du Rand et al. (2021), with the Henry (2008) dictionary method, the topic
model, and the communication-volume timeline this project builds on. This repo reuses that
one's corpus and dictionary-method baseline (copied into `data/`, not recomputed) purely
as a comparison point.

## Citation

If you use this code or data, please cite the original paper the underlying corpus and
dictionary baseline come from:

> Gideon du Rand, Ruan Erasmus, Hylton Hollander, Monique Reid & Dawie van Lill (2021) The
> evolution of central bank communication as experienced by the South Africa Reserve Bank,
> *Economic History of Developing Regions*, 36:2, 282-312, DOI: 10.1080/20780389.2021.192510

for the sentiment dictionary used as a baseline:

> Henry, E. (2008). Are Investors Influenced By How Earnings Press Releases Are Written?
> *Journal of Business Communication*, 45(4).

and for the literature this LLM method's design choices are grounded in:

> Silva, T. C., Moriya, K., & Veyrune, R. M. (2025). From Text to Quantified Insights: A
> Large-Scale LLM Analysis of Central Bank Communication. *IMF Working Paper* WP/25/109.

> Kim, W., Spörer, J., Lee, C. L., & Handschuh, S. (2024). Is Small Really Beautiful for
> Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4,
> FinBERT-FOMC, FinBERT, and VADER. *5th ACM International Conference on AI in Finance
> (ICAIF '24)*.
