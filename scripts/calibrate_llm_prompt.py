"""ETAPA 1 (calibracao) -- roda o prompt em scripts/llm_prompt.py contra o
conjunto pequeno em calibration_set.json, em dois modelos (Haiku 4.5 e
Sonnet 5), e grava lado a lado pra revisao humana antes de rodar o lote
completo (675 documentos).

Uso: python calibrate_llm_prompt.py [--round N]
Saida: data/processed/calibration/round_N.csv
"""

from __future__ import annotations

import argparse
import csv
import json

import anthropic

import config
from llm_prompt import score_document

MODELS = ["claude-haiku-4-5", "claude-sonnet-5"]


def load_calibration_set() -> list[dict]:
    items = json.loads((config.SCRIPTS_DIR / "calibration_set.json").read_text(encoding="utf-8"))
    for item in items:
        if item["type"] == "sentence":
            item["text"] = item["text"]
        else:
            path = config.PROJECT_ROOT / item["file"]
            item["text"] = path.read_text(encoding="utf-8")
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, default=1, help="Numero da rodada de calibracao (so muda o nome do arquivo de saida).")
    args = parser.parse_args()

    client = anthropic.Anthropic()
    items = load_calibration_set()

    rows = []
    for item in items:
        row = {
            "id": item["id"],
            "type": item["type"],
            "why": item["why"],
            "henry_index": item.get("henry_index"),
        }
        for model in MODELS:
            print(f"scoring {item['id']} with {model}...")
            result = score_document(client, model, item["text"])
            prefix = model.replace("claude-", "").replace("-", "_")
            row[f"{prefix}_score"] = result.score
            row[f"{prefix}_label"] = result.label
            row[f"{prefix}_on_topic"] = result.on_topic
            row[f"{prefix}_quote"] = result.quote
        rows.append(row)

    out_path = config.CALIBRATION_DIR / f"round_{args.round}.csv"
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSalvo em: {out_path}")


if __name__ == "__main__":
    main()
