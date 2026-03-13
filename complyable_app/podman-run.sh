#!/bin/bash

CONTAINER_NAME="complyable-app"
IMAGE_NAME="localhost/complyable"

# ── Host data directories ─────────────────────────────────────────────────────
# Works on Mac, Linux and Windows (Git Bash / WSL)
HOST_DATA="$HOME/Complyable"
HOST_VAULT="$HOST_DATA/vault"
HOST_OUTPUT="$HOST_DATA/output"
HOST_INPUT="$HOST_DATA/input"

# Create host directories if they don't exist
mkdir -p "$HOST_VAULT"
mkdir -p "$HOST_OUTPUT"
mkdir -p "$HOST_INPUT"

echo "📁 Data directory: $HOST_DATA"

# ── Stop and remove existing container ───────────────────────────────────────
podman rm -f $CONTAINER_NAME 2>/dev/null || true

# ── Run container with host path mounts ──────────────────────────────────────
podman run -d \
  --name $CONTAINER_NAME \
  -p 8501:8501 \
  -v "$HOST_VAULT":/app/data/vault \
  -v "$HOST_OUTPUT":/app/data/output \
  -v "$HOST_INPUT":/app/data/input \
  -e HOST_OUTPUT_PATH="$HOST_DATA/output" \
  -e HOST_VAULT_PATH="$HOST_DATA/vault" \
  $IMAGE_NAME

echo "✅ Complyable is running at http://localhost:8501"
echo "📂 Output files: $HOST_OUTPUT"
echo "🗄️  Database: $HOST_VAULT"