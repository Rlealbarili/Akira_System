#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p logs

./venv/bin/python src/atualizar_kpis.py >> logs/atualizar_kpis.log 2>&1
