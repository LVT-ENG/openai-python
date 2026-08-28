# Documentación de Scripts de Promociones

Este documento explica cómo usar los scripts que automatizan la publicación de promociones para `tryonyou.pro`.

## Scripts disponibles

Los scripts se encuentran en el directorio raíz del repositorio.

### 1. `auto_deploy.sh`

Este es un wrapper en Bash que toma el archivo promocional, y llama a `auto_deploy.py` para procesarlo, controlando el código de salida.

**Uso:**

```bash
./auto_deploy.sh <ruta_al_archivo_json>
```

**Ejemplo de uso:**
```bash
./auto_deploy.sh promotion_example.json
```

### 2. `auto_deploy.py`

Es el script principal desarrollado en Python que lee el JSON de la promoción, valida los campos requeridos (`title`, `description`, `discount_code`, `valid_until`) y realiza el POST de despliegue a la API de producción.

**Uso directo:**
```bash
python3 auto_deploy.py <ruta_al_archivo_json>
```

**Variables de entorno:**
- `TRYONYOU_API_KEY`: Clave API para autenticar la petición. Si no está definida, se enviará un valor por defecto.

## Formato del archivo JSON de promoción

Todos los archivos de promoción deben seguir la siguiente estructura:

```json
{
    "title": "Summer Sale 2024",
    "description": "Get 50% off on all items this summer!",
    "discount_code": "SUMMER50",
    "valid_until": "2024-08-31T23:59:59Z"
}
```
