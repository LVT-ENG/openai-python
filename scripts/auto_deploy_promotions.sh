#!/bin/bash

# Por defecto a promotion_example.json si no se proporciona argumento
PROMO_FILE="${1:-promotion_example.json}"

if [ ! -f "$PROMO_FILE" ]; then
    echo "Error: No se encontró el archivo de contenido promocional '$PROMO_FILE'."
    exit 1
fi

# Comprobar si se proporciona clave de API para despliegue desatendido
if [ -z "$TRYONYOU_API_KEY" ]; then
    echo "Advertencia: La variable de entorno TRYONYOU_API_KEY no está configurada."
    echo "Ejecutando despliegue en modo dry-run para validación..."
    DRY_RUN="--dry-run"
else
    echo "TRYONYOU_API_KEY está configurada. Procediendo con el despliegue en producción..."
    DRY_RUN=""
fi

# Ejecutar el script de despliegue
echo "Ejecutando despliegue..."
python3 scripts/deploy_promotions.py "$PROMO_FILE" $DRY_RUN

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Rutina completada exitosamente."
else
    echo "La rutina falló con código de salida $EXIT_CODE."
    exit $EXIT_CODE
fi
