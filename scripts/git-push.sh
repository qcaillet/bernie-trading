#!/usr/bin/env bash
# Helper pour push GitHub sans stocker le token dans .git/config
# Usage: ./scripts/git-push.sh [branch]

set -euo pipefail

BRANCH="${1:-main}"
TOKEN_FILE="$HOME/.openclaw/workspace/.secrets/github_token"

if [ ! -f "$TOKEN_FILE" ]; then
  echo "❌ Token introuvable: $TOKEN_FILE" >&2
  exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")
REPO_URL="https://x-access-token:${TOKEN}@github.com/qcaillet/bernie-trading.git"

git push "$REPO_URL" "$BRANCH"
