# Automatización de Publicación de Promociones para tryonyou.pro

Esta guía explica el funcionamiento del script unificado diseñado para validar y desplegar automáticamente las promociones en el entorno de producción de forma desatendida.

## Componentes del sistema

El sistema ahora se compone de un único script principal, preparado para operar en español:

1. **`scripts/daemon_promociones.py`**:
   - Funciona como un "daemon" que monitorea periódicamente el directorio `promociones/`.
   - Cuando encuentra un archivo JSON con contenido de promoción, valida su estructura asegurando que los campos obligatorios existen (`title`, `description`, `discount_code`, `valid_until`).
   - Ejecuta la petición HTTP POST para enviar los datos a la API de producción (`https://api.tryonyou.pro/v1/promotions`).
   - Mueve los archivos procesados exitosamente al directorio `promociones_procesadas/` o a `promociones_fallidas/` en caso de error de red o validación.
   - Soporta un modo `--dry-run` para probar el flujo completo sin realizar la petición de red real.

## Cómo usar el sistema

### Configuración del Despliegue Desatendido (Background)

Para que el script esté permanentemente escuchando y desplegando nuevos archivos que se depositen en la carpeta `promociones/`, ejecuta el daemon en segundo plano:

```bash
python3 scripts/daemon_promociones.py > daemon_promociones.log 2>&1 &
```

Esto iniciará el proceso en background. El sistema comprobará la carpeta cada 5 segundos.
Puedes monitorizar la actividad revisando el archivo de log:

```bash
tail -f daemon_promociones.log
```

Para detener el daemon, puedes buscar el PID y matarlo:
```bash
kill $(pgrep -f "daemon_promociones.py")
```

### Ejecución Única (One-off)

Si deseas probar o procesar los archivos de promoción actuales en el directorio solo una vez (sin quedarse corriendo):

```bash
python3 scripts/daemon_promociones.py --once
```

Para simularlo sin afectar a la API real, añade la bandera `--dry-run`:

```bash
python3 scripts/daemon_promociones.py --once --dry-run
```

## Directorios y Archivos

Al ejecutar el script, automáticamente creará la siguiente estructura si no existe:
- `promociones/` : Directorio donde debes depositar los archivos JSON promocionales nuevos.
- `promociones_procesadas/` : Directorio a donde se mueven los archivos que fueron validados y enviados con éxito.
- `promociones_fallidas/` : Directorio a donde se mueven los archivos con errores de validación o despliegue.

## Variables de Entorno

- **`TRYONYOU_API_KEY`**: Es requerida para realizar peticiones reales a la API de producción. Si no está configurada y no estás en modo `--dry-run`, el script mostrará un error y se detendrá.
