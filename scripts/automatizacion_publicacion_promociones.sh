#!/usr/bin/env bash

# Script para iniciar la rutina de publicación de promociones
# en segundo plano de forma desatendida.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${BASE_DIR}/promotions_unattended.log"

echo "Iniciando despliegue desatendido de promociones..."
# Iniciando con el script de Python en background.
python3 "${SCRIPT_DIR}/automatizacion_publicacion_promociones.py" > "$LOG_FILE" 2>&1 &
PID=$!

echo "Rutina ejecutándose en background con PID: $PID"
echo "Logs disponibles en $LOG_FILE"
