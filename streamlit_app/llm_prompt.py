"""Prompt e schema compartilhados pelo metodo LLM -- usado tanto na
calibracao (calibrate_llm_prompt.py, poucos documentos, varios modelos)
quanto no lote completo (score_llm.py, 675 documentos, um modelo so).

Mantendo os dois num modulo so: a calibracao so vale alguma coisa se ela
testar EXATAMENTE o prompt que depois roda em escala. Qualquer mudanca no
rubric/few-shot deve acontecer aqui, nao duplicada em dois lugares.

Os exemplos few-shot abaixo sao genericos (nao tirados do corpus do SARB)
de proposito -- os documentos usados na calibracao (ver calibration_set.json)
precisam ficar de fora do prompt, senao a calibracao vira circular.
"""

from pydantic import BaseModel, Field


class StanceScore(BaseModel):
    score: float = Field(description="De -2 (mais dovish) a +2 (mais hawkish), pode usar decimais.")
    label: str = Field(description="Um de: strongly hawkish, leaning hawkish, neutral, leaning dovish, strongly dovish.")
    quote: str = Field(description="A frase ou trecho curto do texto que mais justifica essa nota.")
    on_topic: bool = Field(description="False se o texto nao trata primariamente de postura de politica monetaria (ex.: discurso sobre sistema de pagamentos, inclusao financeira, IA, etc.).")


SYSTEM_PROMPT = """You are analyzing central bank communication to determine monetary
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

Critical -- read for meaning and direction, not vocabulary:
A sentence like "growth has weakened sharply" is DOVISH even though it contains the
word "growth." A sentence like "the risk that inflation runs too hot" is HAWKISH even
though it contains the word "risk." A word-counting method gets both of these wrong;
you must not.

Example 1 (hawkish):
"The Committee judged that further policy tightening was warranted. Underlying
inflation remains too high, and recent data confirm continued strength in demand.
The Committee raised the policy rate and expects borrowing costs to stay higher for
longer, and judged that a firm and restrictive stance remains necessary until
inflation returns durably to target."
-> {"score": 1.9, "label": "strongly hawkish", "quote": "a firm and restrictive stance
remains necessary until inflation returns durably to target", "on_topic": true}

Example 2 (dovish):
"The Committee judged that a markedly accommodative stance was warranted. Economic
activity has slowed sharply, with soft demand and weak momentum across many sectors.
The Committee cut the policy rate, noting that borrowing costs are likely to fall
further as downside risks build."
-> {"score": -1.8, "label": "strongly dovish", "quote": "a markedly accommodative
stance was warranted", "on_topic": true}

If the text is not primarily about monetary policy stance (e.g. a speech about
payment systems, financial inclusion, artificial intelligence, or an unrelated topic),
set on_topic to false and score it close to 0 -- do not force a directional read based
on incidental word choice elsewhere in the text.

Read the full text below and return your assessment."""


def score_document(client, model: str, text: str) -> StanceScore:
    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
        output_format=StanceScore,
    )
    return response.parsed_output
