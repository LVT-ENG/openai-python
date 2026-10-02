# Documentación de Rutina de Despliegue en Producción

Este documento explica cómo utilizar el script `scripts/rutina_despliegue_produccion.py` para la automatización y despliegue de promociones en `tryonyou.pro`.

## Funcionamiento

El script funciona monitoreando el directorio `promociones/`. Al detectar archivos JSON con promociones, los valida utilizando Pydantic para asegurar que todos los campos requeridos (`title`, `description`, `discount_code`, `valid_until`) estén presentes y sean correctos.

Si la validación es exitosa, los datos se despliegan automáticamente a la API en producción. El archivo se moverá a `promociones_procesadas/`. Si la validación falla, o hay un error en el despliegue, el archivo se moverá a `promociones_fallidas/`.

El script también está diseñado para extraer contenido JSON robustamente, permitiéndole entender datos generados por un LLM dentro de bloques de Markdown, etc.

## Requisitos

- `TRYONYOU_API_KEY`: Es necesario establecer esta variable de entorno para la comunicación con la API.

## Cómo Usarlo

### Ejecutar como Daemon

Para ejecutar el script de manera continua:

```bash
python scripts/rutina_despliegue_produccion.py
```

### Ejecutar una Sola Vez (One-off)

Para procesar los archivos actuales sin que se quede en ejecución continua:

```bash
python scripts/rutina_despliegue_produccion.py --once
```

### Simular (Dry Run)

Puedes probar el script sin enviar peticiones reales a la API de producción utilizando la bandera `--dry-run`:

```bash
python scripts/rutina_despliegue_produccion.py --dry-run
```
