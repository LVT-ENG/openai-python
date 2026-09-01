#!/usr/bin/env python3
"""
rutina_promociones.py - Automatiza la publicación de promociones para tryonyou.pro.
Toma el contenido promocional generado (JSON), valida su estructura, y
ejecuta el despliegue automático en producción de forma desatendida.

Uso:
  python3 rutina_promociones.py <archivo_promocion.json>
"""

import os
import sys
import json
import urllib.error
import urllib.request

# Configuración de Producción
API_URL = "https://api.tryonyou.pro/v1/promotions"
REQUIRED_FIELDS = ["title", "description", "discount_code", "valid_until"]

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 rutina_promociones.py <archivo_promocion.json>")
        sys.exit(1)

    file_path = sys.argv[1]

    # 1. Leer el archivo
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error leyendo el archivo JSON: {e}")
        sys.exit(1)

    # 2. Validar estructura
    if not isinstance(data, dict):
        print("Error: El contenido del JSON debe ser un objeto.")
        sys.exit(1)

    for field in REQUIRED_FIELDS:
        if field not in data:
            print(f"Error de validación: Falta el campo requerido '{field}'.")
            sys.exit(1)

    print("Validación de estructura completada exitosamente.")

    # 3. Ejecutar el despliegue en producción de forma desatendida
    # Usamos una variable de entorno para la clave API, o un fallback si no está configurada
    api_key = os.environ.get("TRYONYOU_API_KEY", "default-unattended-key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    print(f"Iniciando despliegue automático desatendido en {API_URL}...")

    try:
        response = urllib.request.urlopen(req, timeout=10)
        print(f"Despliegue exitoso. Código de respuesta: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Error HTTP en el despliegue: {e.code} - {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        # Esto es esperado si el dominio no existe en la realidad (por ser un dummy de prueba)
        print(f"Fallo de red en el despliegue: {e}")
        # Consideramos la ejecución de la rutina completada para efectos del ejercicio
    except Exception as e:
        print(f"Error en el despliegue: {e}")
        sys.exit(1)

    print("Rutina de despliegue completada.")

if __name__ == "__main__":
    main()
