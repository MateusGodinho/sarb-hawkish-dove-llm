"""Caminhos e constantes compartilhados por todo o pipeline.

Este projeto reutiliza o corpus e os metadados já coletados em
sarb_hawkish_dove/ (copiados, nao movidos -- aquele projeto e publico e
referenciado pelo artigo original, entao continua intacto e reproduzivel
por conta propria). Aqui nao ha scraping: o foco e o metodo de pontuacao
via LLM, rodando sobre o mesmo corpus (173 atas, 511 discursos, dos quais
502 em ingles).
"""

from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
RAW_TEXTS_DIR = DATA_DIR / "raw_texts"
PROCESSED_DIR = DATA_DIR / "processed"

STATEMENTS_INDEX_JSON = RAW_DIR / "statements_index.json"
DATASET_JSON = PROCESSED_DIR / "statements_dataset.json"
DATASET_CSV = PROCESSED_DIR / "statements_dataset.csv"

# Series diaria da SARB Policy Rate e a versao verificada (fonte de verdade
# pra rate_action_final / policy_rate_final), copiadas do projeto original.
POLICY_RATE_DAILY_CSV = RAW_DIR / "sarb_policy_rate_daily.csv"
POLICY_RATE_VERIFIED_CSV = PROCESSED_DIR / "policy_rate_verified.csv"

INFLATION_TARGETING_START = "2000-02-01"

# --- Speeches ---
SPEECHES_RAW_TEXTS_DIR = RAW_TEXTS_DIR / "speeches"
SPEECHES_INDEX_JSON = RAW_DIR / "speeches_index.json"
SPEECHES_DATASET_JSON = PROCESSED_DIR / "speeches_dataset.json"
SPEECHES_DATASET_CSV = PROCESSED_DIR / "speeches_dataset.csv"

# --- Metodo Henry (2008), copiado do projeto original -- usado aqui so
# como baseline de comparacao, nao recalculado neste projeto. ---
SCORES_HENRY_CSV = PROCESSED_DIR / "scores_henry.csv"
SPEECHES_SCORES_HENRY_CSV = PROCESSED_DIR / "speeches_scores_henry.csv"
COMBINED_INDEX_HENRY_CSV = PROCESSED_DIR / "combined_index_by_meeting.csv"

# --- Metodo LLM (este projeto) ---
CALIBRATION_DIR = PROCESSED_DIR / "calibration"
SCORES_LLM_STATEMENTS_CSV = PROCESSED_DIR / "scores_llm_statements.csv"
SCORES_LLM_SPEECHES_CSV = PROCESSED_DIR / "scores_llm_speeches.csv"
COMBINED_INDEX_LLM_CSV = PROCESSED_DIR / "combined_index_llm_by_meeting.csv"

# Modelo usado no lote completo, decidido so depois da calibracao (ver
# CALIBRATION_DIR). Mantido aqui como unico ponto de configuracao.
LLM_MODEL = "claude-haiku-4-5"

REPORTS_DIR = PROJECT_ROOT / "reports"

for _dir in (RAW_DIR, RAW_TEXTS_DIR, PROCESSED_DIR, CALIBRATION_DIR, REPORTS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
