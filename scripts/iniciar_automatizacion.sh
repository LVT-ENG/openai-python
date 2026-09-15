#!/bin/bash
# Script para iniciar la automatización de publicaciones de promociones

# Directorio base
BASE_DIR=$(pwd)

# Crear los directorios requeridos
mkdir -p "$BASE_DIR/promociones"
mkdir -p "$BASE_DIR/promociones_procesadas"
mkdir -p "$BASE_DIR/promociones_fallidas"

echo "Iniciando automatización de promociones..."

# Ejecutar el daemon en segundo plano (desatendido)
nohup python3 -u scripts/daemon_promociones.py > daemon_promociones.log 2>&1 &

PID=$!
echo "Daemon de promociones iniciado con PID $PID."
echo "Los logs se están guardando en daemon_promociones.log."
echo "Deposita tus archivos JSON en la carpeta promociones/ para su despliegue automático."
