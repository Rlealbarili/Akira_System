#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TS="$(date +%Y%m%d_%H%M%S)"
JSON_OUT="logs/healthcheck_${TS}.json"

mkdir -p logs

./venv/bin/python src/healthcheck.py --json-out "$JSON_OUT" >> logs/healthcheck.log 2>&1
