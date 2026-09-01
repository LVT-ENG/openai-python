#!/usr/bin/env bash
# scripts/rutina_desatendida_promociones.sh
# Inicia la monitorización y despliegue automático de promociones en background.

BASE_DIR="$(pwd)"
LOG_FILE="${BASE_DIR}/promotions.log"

echo "Iniciando rutina desatendida de promociones..."
echo "Los registros se guardarán en: $LOG_FILE"

# Ejecutar el script watch_promotions.sh en background y redirigir la salida al log
nohup "${BASE_DIR}/scripts/watch_promotions.sh" "$@" > "$LOG_FILE" 2>&1 &
PID=$!

echo "Rutina ejecutándose en background con PID: $PID"
