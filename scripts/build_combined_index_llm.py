"""Equivalente LLM do build_combined_index.py do projeto original --
mesma janela de agregacao por reuniao (janela = da reuniao anterior,
exclusive, ate a atual, inclusive), mesma decomposicao exata
contrib_statement + contrib_speech = combined_index.

Uma diferenca de metodo em relacao ao Henry: discursos marcados
on_topic=False pelo LLM (fora do escopo de postura de politica monetaria --
ver achados da calibracao) sao EXCLUIDOS da janela, nao tratados como
neutros. Um "0" de um discurso sobre financas verdes nao e um sinal de
politica neutro, e ausencia de sinal -- inclui-lo dilui o que os discursos
que sao sobre postura estao realmente dizendo.

Uso: python build_combined_index_llm.py
"""

from __future__ import annotations

import csv
import json

import config

OUT_CSV = config.COMBINED_INDEX_LLM_CSV


def _load_statement_rows() -> list[dict]:
    titles_by_date = {}
    for r in json.loads(config.DATASET_JSON.read_text(encoding="utf-8")):
        if r.get("meeting_date"):
            titles_by_date.setdefault(r["meeting_date"], r.get("title"))

    rows = []
    with open(config.SCORES_LLM_STATEMENTS_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            date = r.get("meeting_date")
            if not date:
                continue
            rows.append({
                "date": date,
                "index": float(r["llm_score"]),
                "title": titles_by_date.get(date),
            })
    rows.sort(key=lambda r: r["date"])
    return rows


def _load_speech_rows() -> tuple[list[dict], int]:
    rows = []
    n_off_topic = 0
    with open(config.SCORES_LLM_SPEECHES_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            date = r.get("publish_date")
            if not date:
                continue
            if r.get("llm_on_topic") in ("False", "false", False):
                n_off_topic += 1
                continue
            rows.append({"date": date, "index": float(r["llm_score"])})
    rows.sort(key=lambda r: r["date"])
    return rows, n_off_topic


def main():
    meetings = _load_statement_rows()
    speeches, n_off_topic = _load_speech_rows()

    out_rows = []
    prev_date = None
    speech_i = 0

    for meeting in meetings:
        meeting_date = meeting["date"]

        window_scores = []
        while speech_i < len(speeches) and speeches[speech_i]["date"] <= meeting_date:
            if prev_date is not None and speeches[speech_i]["date"] > prev_date:
                window_scores.append(speeches[speech_i]["index"])
            speech_i += 1

        n_stmt = 1
        n_speech = len(window_scores)
        n_total = n_stmt + n_speech

        avg_stmt = meeting["index"]
        avg_speech = sum(window_scores) / n_speech if n_speech else 0.0

        contrib_stmt = (n_stmt / n_total) * avg_stmt
        contrib_speech = (n_speech / n_total) * avg_speech
        combined_index = contrib_stmt + contrib_speech

        out_rows.append({
            "meeting_date": meeting_date,
            "title": meeting["title"],
            "window_start": prev_date,
            "n_speeches_in_window": n_speech,
            "statement_index": round(avg_stmt, 4),
            "avg_speech_index": round(avg_speech, 4) if n_speech else None,
            "contrib_statement": round(contrib_stmt, 4),
            "contrib_speech": round(contrib_speech, 4),
            "combined_index": round(combined_index, 4),
        })

        prev_date = meeting_date

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    total_speeches_used = sum(r["n_speeches_in_window"] for r in out_rows)
    print(f"Indice combinado (LLM) calculado para {len(out_rows)} reunioes.")
    print(f"Discursos usados (dentro de alguma janela, on-topic): {total_speeches_used}/{len(speeches) + n_off_topic}")
    print(f"Discursos excluidos por on_topic=False: {n_off_topic}")
    print(f"Salvo em: {OUT_CSV}")


if __name__ == "__main__":
    main()
