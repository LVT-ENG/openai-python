#!/usr/bin/env bash
# auto_deploy.sh - Wrapper para ejecutar la rutina de despliegue automático
# de promociones en tryonyou.pro

if [ -z "$1" ]; then
    echo "Uso: ./auto_deploy.sh <archivo_promocion.json>"
    exit 1
fi

PROMO_FILE="$1"

# Ejecutar el script Python que contiene la lógica de validación y despliegue
python3 auto_deploy.py "$PROMO_FILE"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Despliegue automático completado con éxito."
else
    echo "Fallo en el despliegue automático."
    exit $EXIT_CODE
fi
