#!/usr/bin/env bash
set -euo pipefail

# Creates/updates the Kubernetes Secret `secret-openai` from a local .env file
# Usage: copy .env.example -> .env (fill OPENAI_API_KEY) and run this script

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
NAMESPACE=${1:-default}

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: $ENV_FILE not found. Copy .env.example to .env and set OPENAI_API_KEY." >&2
  exit 2
fi

# Load OPENAI_API_KEY from file without exporting other values
OPENAI_API_KEY=$(grep -E '^OPENAI_API_KEY=' "$ENV_FILE" | sed -E 's/OPENAI_API_KEY=//') || true

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "REPLACE_ME" ]; then
  echo "Error: OPENAI_API_KEY is not set or still REPLACE_ME in $ENV_FILE" >&2
  exit 3
fi

echo "Creating/updating Kubernetes secret 'secret-openai' in namespace '$NAMESPACE'..."
kubectl delete secret secret-openai -n "$NAMESPACE" >/dev/null 2>&1 || true
kubectl create secret generic secret-openai --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" -n "$NAMESPACE"

echo "Secret created. Verify with: kubectl get secret secret-openai -n $NAMESPACE -o yaml"
