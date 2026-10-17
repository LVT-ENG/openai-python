#!/usr/bin/env bash
# Despliegue desatendido de promociones (invocado por GitHub Actions y cron).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p promociones promociones_procesadas promociones_fallidas

exec python3 scripts/daemon_promociones.py --once
