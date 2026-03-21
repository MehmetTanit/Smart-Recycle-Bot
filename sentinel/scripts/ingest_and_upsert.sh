#!/usr/bin/env bash
set -euo pipefail

# Ingest helper: generates points.json (using OPENAI_API_KEY from env or .env) and upserts to Qdrant
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EMBED_SCRIPT="$ROOT_DIR/sentinel-embed-chat/app/generate_points.py"
OUT_FILE="$ROOT_DIR/output/points.json"
QDRANT_URL=${QDRANT_URL:-http://localhost:6333}
COLLECTION=${QDRANT_COLLECTION:-sentinel_docs}

if [ -f "$ROOT_DIR/.env" ]; then
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.env"
fi

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "Error: OPENAI_API_KEY not set. Fill sentinel/.env with your key or export OPENAI_API_KEY." >&2
  exit 2
fi

echo "Generating embeddings and points.json..."
python "$EMBED_SCRIPT"

if [ ! -f "$OUT_FILE" ]; then
  echo "Error: points file not found at $OUT_FILE" >&2
  exit 3
fi

echo "Ensuring Qdrant collection $COLLECTION exists at $QDRANT_URL..."
curl -sSf -X PUT "$QDRANT_URL/collections/$COLLECTION" -H "Content-Type: application/json" \
  -d '{"vectors":{"size":1536,"distance":"Cosine"}}' || true

echo "Upserting points to Qdrant (may take a moment)..."
curl -sS -X PUT "$QDRANT_URL/collections/$COLLECTION/points?wait=true" \
  -H "Content-Type: application/json" --data-binary @"$OUT_FILE" | jq -C . || true

echo "Done. You can now query Qdrant at $QDRANT_URL and use the chat/api services."
