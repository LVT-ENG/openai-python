# Automatización de Publicación de Promociones para tryonyou.pro

Esta guía explica el funcionamiento de los scripts diseñados para validar, monitorizar y desplegar automáticamente las promociones en el entorno de producción.

## Componentes del sistema

El sistema se compone de varios scripts, todos ellos preparados para operar en español:

1. **`deploy_promotions.py`**:
   - Toma el archivo JSON con el contenido de la promoción.
   - Valida su estructura asegurando que los campos obligatorios existen.
   - Ejecuta la petición HTTP para enviar los datos a la API en producción.
   - Soporta un modo `--dry-run` para validar sin realizar la petición de red.

2. **`automate_promotions.sh`**:
   - Itera a través del directorio `promotions/`.
   - Llama a `deploy_promotions.py` para cada archivo JSON.
   - Mueve los archivos procesados exitosamente a `promotions_processed/` o a `promotions_failed/` en caso de error.

3. **`watch_promotions.sh`**:
   - Utiliza `inotifywait` para monitorizar continuamente el directorio `promotions/`.
   - Cuando se añade o modifica un archivo JSON de promoción, dispara automáticamente `automate_promotions.sh`.

4. **`rutina_desatendida_promociones.sh`**:
   - Es el punto de entrada principal para la automatización en background.
   - Lanza `watch_promotions.sh` en modo desacoplado (utilizando `nohup`).
   - Redirige todas las salidas (logs y errores) al archivo central `promotions.log`.

## Cómo usar el sistema

### Despliegue manual e interactivo

Si deseas probar o desplegar un único archivo promocional:

```bash
./scripts/auto_deploy_promotions.sh <archivo.json>
```

Para simularlo sin afectar a la API real, asegúrate de que no esté definida la variable `TRYONYOU_API_KEY` o utiliza explícitamente `--dry-run` donde se soporte.

### Configuración del Despliegue Desatendido (Background)

Para que el servidor esté permanentemente escuchando y desplegando nuevos archivos que se depositen en la carpeta `promotions/`, ejecuta:

```bash
./scripts/rutina_desatendida_promociones.sh
```

Esto iniciará el proceso en background. El sistema te mostrará un número de proceso (PID).
Puedes monitorizar la actividad revisando el archivo de log:

```bash
tail -f promotions.log
```

### Configuración con Cron (Alternativa)

Si prefieres ejecutar el despliegue de forma periódica en lugar de reaccionar a eventos (inotify), puedes añadir una tarea cron para ejecutar el procesamiento en bloque:

1. Abre la configuración de cron:
   ```bash
   crontab -e
   ```
2. Añade la siguiente línea para que se ejecute cada hora (por ejemplo):
   ```cron
   0 * * * * /ruta/absoluta/al/proyecto/scripts/automate_promotions.sh >> /ruta/absoluta/al/proyecto/promotions.log 2>&1
   ```
*(Nota: Si usas cron, no es necesario ejecutar la rutina desatendida con `watch_promotions.sh`, ya que ambos cumplirían propósitos similares.)*

## Variables de Entorno

- **`TRYONYOU_API_KEY`**: Es requerida para realizar peticiones reales a la API de producción. Si no está configurada, los scripts de despliegue operarán o advertirán en modo *dry-run* o simulación.
