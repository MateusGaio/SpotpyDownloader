#!/usr/bin/env bash
set -a
source "$(dirname "$0")/.env"
set +a
"$(dirname "$0")/.venv/bin/spotpydownloader"
echo
read -n1 -r -p "Pressione qualquer tecla para fechar..."
