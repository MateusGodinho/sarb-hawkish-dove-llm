"""ETAPA 2 -- roda o metodo LLM (Haiku 4.5, decidido na calibracao) sobre
todo o corpus via Message Batches API (50% mais barato, assincrono).

So faz a pontuacao por documento -- a agregacao em indice combinado por
reuniao (equivalente ao combined_index_by_meeting.csv do Henry) e um passo
separado, depois que tivermos os scores brutos em mao.

Uso: python score_llm.py            # submete o lote e sai
     python score_llm.py --wait     # submete e fica esperando/baixando o resultado
     python score_llm.py --status <batch_id>
     python score_llm.py --fetch <batch_id>
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time

import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

import config
from llm_prompt import SYSTEM_PROMPT, StanceScore

# output_config espera {"format": {...}} -- o "type": "json_schema" fica
# DENTRO de format, nao no nivel de output_config (erro que derrubou o
# primeiro lote inteiro: "output_config.type: Extra inputs are not permitted").
OUTPUT_CONFIG = {
    "format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "label": {"type": "string"},
                "quote": {"type": "string"},
                "on_topic": {"type": "boolean"},
            },
            "required": ["score", "label", "quote", "on_topic"],
            "additionalProperties": False,
        },
    }
}


def _make_request(kind: str, idx: int, text: str) -> Request:
    return Request(
        custom_id=f"{kind}__{idx:04d}",
        params=MessageCreateParamsNonStreaming(
            model=config.LLM_MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
            output_config=OUTPUT_CONFIG,
        ),
    )


def build_requests() -> list[Request]:
    # custom_id tem limite de 64 caracteres na Batches API, e duas datas de
    # reuniao (1999-10-13, 1999-11-24) tem dois documentos cada -- por isso
    # os dois lados usam indice sequencial curto, com o mapeamento pro stem
    # do arquivo (que ja e unico) gravado a parte.
    requests = []
    id_map = {}

    statements = json.loads(config.DATASET_JSON.read_text(encoding="utf-8"))
    idx = 0
    for r in statements:
        if r.get("scrape_status") != "ok" or not r.get("raw_text_file"):
            continue
        text_path = config.PROJECT_ROOT / r["raw_text_file"]
        if not text_path.exists():
            continue
        custom_id = f"stmt__{idx:04d}"
        id_map[custom_id] = {"stem": text_path.stem, "meeting_date": r["meeting_date"]}
        requests.append(_make_request("stmt", idx, text_path.read_text(encoding="utf-8")))
        idx += 1

    speeches = json.loads(config.SPEECHES_DATASET_JSON.read_text(encoding="utf-8"))
    idx = 0
    for r in speeches:
        if r.get("scrape_status") != "ok" or not r.get("raw_text_file"):
            continue
        if r.get("is_english") is False:
            continue
        text_path = config.PROJECT_ROOT / r["raw_text_file"]
        if not text_path.exists():
            continue
        custom_id = f"sp__{idx:04d}"
        id_map[custom_id] = {"stem": text_path.stem, "publish_date": r.get("publish_date")}
        requests.append(_make_request("sp", idx, text_path.read_text(encoding="utf-8")))
        idx += 1

    (config.PROCESSED_DIR / "llm_id_map.json").write_text(
        json.dumps(id_map, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return requests


def submit(client: anthropic.Anthropic) -> str:
    requests = build_requests()
    print(f"{len(requests)} documentos a pontuar (custom_ids unicos).")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch criado: {batch.id} (status: {batch.processing_status})")
    (config.CALIBRATION_DIR.parent / "last_batch_id.txt").write_text(batch.id, encoding="utf-8")
    return batch.id


def wait_for_batch(client: anthropic.Anthropic, batch_id: str, poll_seconds: int = 30):
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        counts = batch.request_counts
        print(f"status={batch.processing_status} processing={counts.processing} succeeded={counts.succeeded} errored={counts.errored}")
        if batch.processing_status == "ended":
            return batch
        time.sleep(poll_seconds)


def fetch_results(client: anthropic.Anthropic, batch_id: str):
    stmt_rows = []
    speech_rows = []
    errors = []

    id_map = json.loads((config.PROCESSED_DIR / "llm_id_map.json").read_text(encoding="utf-8"))

    for result in client.messages.batches.results(batch_id):
        custom_id = result.custom_id
        if result.result.type != "succeeded":
            errors.append((custom_id, result.result.type))
            continue

        msg = result.result.message
        text = next((b.text for b in msg.content if b.type == "text"), "")
        try:
            parsed = StanceScore.model_validate_json(text)
        except Exception as e:
            errors.append((custom_id, f"parse_error: {e}"))
            continue

        kind = custom_id.split("__", 1)[0]
        meta = id_map.get(custom_id, {})
        row = {
            "id": meta.get("stem", custom_id),
            "meeting_date": meta.get("meeting_date"),
            "publish_date": meta.get("publish_date"),
            "llm_score": parsed.score,
            "llm_label": label_from_score(parsed.score),
            "llm_on_topic": parsed.on_topic,
            "llm_quote": parsed.quote,
        }
        if kind == "stmt":
            del row["publish_date"]
            stmt_rows.append(row)
        else:
            del row["meeting_date"]
            speech_rows.append(row)

    if errors:
        print(f"{len(errors)} erros/falhas:")
        for cid, err in errors[:20]:
            print(" ", cid, err)

    write_csv(config.SCORES_LLM_STATEMENTS_CSV, stmt_rows)
    write_csv(config.SCORES_LLM_SPEECHES_CSV, speech_rows)
    print(f"Salvo: {config.SCORES_LLM_STATEMENTS_CSV} ({len(stmt_rows)} linhas)")
    print(f"Salvo: {config.SCORES_LLM_SPEECHES_CSV} ({len(speech_rows)} linhas)")


def label_from_score(score: float) -> str:
    # mesmos limiares do artefato Hawkish/Dovish Reader, pra manter os dois
    # metodos comparaveis -- nao confiamos no rotulo que o proprio modelo
    # se atribui (ver achado da calibracao, round 1).
    if score >= 0.75:
        return "strongly hawkish"
    if score >= 0.15:
        return "leaning hawkish"
    if score > -0.15:
        return "neutral"
    if score > -0.75:
        return "leaning dovish"
    return "strongly dovish"


def write_csv(path, rows):
    if not rows:
        return
    rows.sort(key=lambda r: r["id"])
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", action="store_true", help="Submete e fica esperando ate terminar, depois ja salva os CSVs.")
    parser.add_argument("--status", metavar="BATCH_ID", help="So checa o status de um batch existente.")
    parser.add_argument("--fetch", metavar="BATCH_ID", help="Baixa e salva os resultados de um batch ja terminado.")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    if args.status:
        batch = client.messages.batches.retrieve(args.status)
        print(batch.processing_status, batch.request_counts)
        return

    if args.fetch:
        fetch_results(client, args.fetch)
        return

    batch_id = submit(client)
    if args.wait:
        wait_for_batch(client, batch_id)
        fetch_results(client, batch_id)


if __name__ == "__main__":
    main()
