#!/usr/bin/env bash
# scripts/automate_promotions.sh
# Automatiza la publicación de promociones
# Uso: ./scripts/automate_promotions.sh [--dry-run]

set -e

# Directorios de trabajo
BASE_DIR="$(pwd)"
PROMOTIONS_DIR="${BASE_DIR}/promotions"
PROCESSED_DIR="${BASE_DIR}/promotions_processed"
FAILED_DIR="${BASE_DIR}/promotions_failed"

# Crear directorios si no existen
mkdir -p "$PROMOTIONS_DIR"
mkdir -p "$PROCESSED_DIR"
mkdir -p "$FAILED_DIR"

# Flags para el script python
PY_ARGS=""
if [ "$1" == "--dry-run" ]; then
    PY_ARGS="--dry-run"
fi

# Iterar sobre todos los archivos JSON en el directorio de promociones
shopt -s nullglob
for file in "$PROMOTIONS_DIR"/*.json; do
    echo "Procesando: $file"

    # Ejecutar deploy_promotions.py
    if python3 "${BASE_DIR}/scripts/deploy_promotions.py" "$file" $PY_ARGS; then
        echo "Éxito: moviendo a $PROCESSED_DIR"
        mv "$file" "$PROCESSED_DIR/"
    else
        echo "Fallo: moviendo a $FAILED_DIR"
        mv "$file" "$FAILED_DIR/"
    fi
done
shopt -u nullglob

echo "Procesamiento completado."
