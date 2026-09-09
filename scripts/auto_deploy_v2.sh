#!/bin/bash
# scripts/auto_deploy_v2.sh

if [ -z "$1" ]; then
    echo "Uso: $0 <ruta_al_archivo_json>"
    exit 1
fi

JSON_FILE=$1

echo "Iniciando despliegue de promociones usando $JSON_FILE..."

python3 scripts/auto_deploy_v2.py "$JSON_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Despliegue completado con éxito."
else
    echo "Fallo en el despliegue. Por favor revisa los logs."
    # Para pruebas locales sin mockear API, si hay error de red no bloquearemos CI necesariamente.
fi

exit $EXIT_CODE
