#!/bin/bash
# scripts/auto_deploy_v2.sh

if [ -z "$1" ]; then
    echo "Error: Debes proporcionar la ruta a un archivo JSON de promoción."
    echo "Uso: $0 <ruta_al_archivo_json>"
    exit 1
fi

FILE_PATH="$1"

# Obtenemos la ruta absoluta del directorio del script bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_deploy_v2.py"

echo "Iniciando despliegue de promoción: $FILE_PATH"

python3 "$PYTHON_SCRIPT" "$FILE_PATH"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "========================================="
    echo "✅ Despliegue exitoso."
    echo "========================================="
    exit 0
else
    echo "========================================="
    echo "❌ Error en el despliegue. Revisa los logs arriba."
    echo "========================================="
    exit $EXIT_CODE
fi
