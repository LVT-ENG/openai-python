# Publicador Desatendido de Promociones

Este documento explica cómo utilizar el script `scripts/publicador_desatendido.py`, diseñado para automatizar la publicación de promociones para `tryonyou.pro` de manera desatendida y continua.

## Funcionamiento

El script implementa un ciclo de monitoreo infinito que vigila el directorio `promotions/`. Cuando detecta un nuevo archivo JSON en este directorio, realiza las siguientes acciones:

1. **Lectura y Parseo:** Lee el archivo y verifica que contenga un diccionario JSON válido.
2. **Validación:** Verifica que la estructura de la promoción contenga todos los campos requeridos (`title`, `description`, `discount_code`, `valid_until`).
3. **Despliegue:** Ejecuta una petición POST a la API de producción para publicar la promoción.
4. **Enrutamiento:** Si el proceso es exitoso, mueve el archivo a la carpeta `promotions_processed/`. Si ocurre algún error durante el parseo, validación o despliegue, el archivo es movido a `promotions_failed/`.

## Requisitos

El sistema de despliegue requiere de una clave API válida configurada como variable de entorno para realizar las peticiones al entorno de producción:

```bash
export TRYONYOU_API_KEY="tu_clave_api_aqui"
```

## Uso

### Ejecución estándar

Para ejecutar el script y que empiece a monitorear el directorio (por defecto sondea cada 5 segundos):

```bash
./scripts/publicador_desatendido.py
```

### Ejecución en modo simulación (Dry-Run)

Si deseas probar el enrutamiento y la validación de archivos sin realizar peticiones HTTP reales a la API, puedes usar el modo `--dry-run`:

```bash
./scripts/publicador_desatendido.py --dry-run
```
*Nota: En este modo, el sistema simulará que el despliegue es exitoso sin requerir la variable `TRYONYOU_API_KEY`.*

### Opciones avanzadas

Puedes personalizar la URL de la API y el intervalo de monitoreo en segundos:

```bash
./scripts/publicador_desatendido.py --api-url "https://api.tryonyou.pro/v1/promotions" --intervalo 10
```

### Ejecución en Background

Para mantener el script funcionando en segundo plano de manera continua e independiente de la sesión de la terminal, puedes usar:

```bash
nohup python3 -u scripts/publicador_desatendido.py > monitoreo.log 2>&1 &
```

Esto enviará toda la salida al archivo `monitoreo.log`, el cual puedes inspeccionar con `tail -f monitoreo.log`.