"""Replica os dois testes de sanidade da Secao 3 do artigo original (media
por tipo de decisao, correlacao com bps), agora pro indice LLM -- e
compara lado a lado com o Henry, pra ver se o vies hawkish estrutural
persiste ou desaparece.
"""

import csv
import statistics

import config


def load_rate_actions() -> dict:
    out = {}
    with open(config.POLICY_RATE_VERIFIED_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("series_action") and r.get("series_change_bps"):
                out[r["meeting_date"]] = {
                    "action": r["series_action"],
                    "bps": float(r["series_change_bps"]),
                }
    return out


def load_index(path: str) -> dict:
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("combined_index"):
                out[r["meeting_date"]] = float(r["combined_index"])
    return out


def load_statement_only(path: str, col: str) -> dict:
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get(col):
                out[r["meeting_date"]] = float(r[col])
    return out


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    return cov / (sx * sy)


def report(name: str, index_by_date: dict, rates: dict):
    by_action = {"hike": [], "hold": [], "cut": []}
    paired_idx, paired_bps = [], []
    for date, idx in index_by_date.items():
        r = rates.get(date)
        if not r:
            continue
        by_action[r["action"]].append(idx)
        paired_idx.append(idx)
        paired_bps.append(r["bps"])

    print(f"--- {name} ---")
    for action in ("hike", "hold", "cut"):
        vals = by_action[action]
        if vals:
            print(f"  {action:5s} n={len(vals):3d}  mean={statistics.mean(vals):.3f}")
    if len(paired_idx) > 2:
        r = pearson(paired_idx, paired_bps)
        print(f"  Pearson r (index vs bps change), n={len(paired_idx)}: {r:.3f}")
    print()


def main():
    rates = load_rate_actions()

    llm_combined = load_index(str(config.COMBINED_INDEX_LLM_CSV))
    henry_combined = load_index(str(config.COMBINED_INDEX_HENRY_CSV))

    llm_stmt_only = {}
    with open(config.SCORES_LLM_STATEMENTS_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("meeting_date"):
                llm_stmt_only[r["meeting_date"]] = float(r["llm_score"])
    henry_stmt_only = {}
    with open(config.SCORES_HENRY_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r.get("meeting_date"):
                henry_stmt_only[r["meeting_date"]] = float(r["henry_index"])

    report("LLM -- combined index", llm_combined, rates)
    report("Henry -- combined index", henry_combined, rates)
    report("LLM -- statements only", llm_stmt_only, rates)
    report("Henry -- statements only", henry_stmt_only, rates)

    print("--- Julho 2026 (a reuniao que motivou o projeto) ---")
    print("  Henry combined:", henry_combined.get("2026-07-23"))
    print("  LLM combined:  ", llm_combined.get("2026-07-23"))


if __name__ == "__main__":
    main()
