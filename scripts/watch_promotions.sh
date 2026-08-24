#!/usr/bin/env bash
# scripts/watch_promotions.sh
# Automatiza la publicación de promociones monitorizando el directorio en busca de nuevos archivos.
# Uso: ./scripts/watch_promotions.sh [--dry-run]

BASE_DIR="$(pwd)"
PROMOTIONS_DIR="${BASE_DIR}/promotions"

# Crear directorio si no existe
mkdir -p "$PROMOTIONS_DIR"

echo "Monitorizando $PROMOTIONS_DIR en busca de nuevos archivos JSON..."

# Monitorizar continuamente
inotifywait -m -e close_write -e moved_to -q --format '%f' "$PROMOTIONS_DIR" | while read -r filename; do
    if [[ "$filename" == *.json ]]; then
        echo "Detectado nuevo archivo promocional: $filename"
        echo "Ejecutando despliegue..."
        "${BASE_DIR}/scripts/automate_promotions.sh" "$@"
        echo "Monitorización reanudada..."
    fi
done
