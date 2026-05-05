#!/usr/bin/env bash
set -euo pipefail

if ! command -v newman >/dev/null 2>&1; then
  printf 'Error: Newman no está instalado. Instálalo con: npm install -g newman\n' >&2
  exit 1
fi

if [ -z "${CLAUSTRUM_PASS:-}" ]; then
  printf 'Error: CLAUSTRUM_PASS es requerida. Ejemplo: CLAUSTRUM_PASS="***" scripts/run_postman.sh\n' >&2
  exit 1
fi

COLLECTION="postman/Integracion_Claustrum_Horarios.postman_collection.json"
ENVIRONMENT="postman/QA_API_LAB.postman_environment.json"
OUTPUT_DIR="evidencias/newman"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
CLI_REPORT="$OUTPUT_DIR/resultados-$TIMESTAMP.txt"

mkdir -p "$OUTPUT_DIR"

newman run "$COLLECTION" \
  -e "$ENVIRONMENT" \
  --env-var "claustrum_pass=$CLAUSTRUM_PASS" \
  --iteration-count 3 \
  --reporters cli \
  | tee "$CLI_REPORT"

printf '\nEvidencia CLI: %s\n' "$CLI_REPORT"
