#!/usr/bin/env python3
"""
automatizacion_promociones.py - Rutina para automatizar la publicación de promociones.
Toma el contenido promocional generado (JSON), valida su estructura, y
ejecuta el despliegue automático en producción de forma desatendida.
"""

import os
import sys
import json
import urllib.error
import urllib.request

API_URL = "https://api.tryonyou.pro/v1/promotions"
CAMPOS_REQUERIDOS = ["title", "description", "discount_code", "valid_until"]

def main():
    if len(sys.argv) < 2:
        print("Uso: ./automatizacion_promociones.py <archivo_promocion.json>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]

    # 1. Leer el archivo
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        sys.exit(1)

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
    except Exception as e:
        print(f"Error leyendo el archivo JSON: {e}")
        sys.exit(1)

    # 2. Validar estructura
    if not isinstance(datos, dict):
        print("Error: El contenido del JSON debe ser un objeto/diccionario.")
        sys.exit(1)

    for campo in CAMPOS_REQUERIDOS:
        if campo not in datos:
            print(f"Error de validación: Falta el campo requerido '{campo}'.")
            sys.exit(1)

    print("Validación de estructura completada exitosamente.")

    # 3. Ejecutar el despliegue en producción de forma desatendida
    api_key = os.environ.get("TRYONYOU_API_KEY", "default-unattended-key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(datos).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    print(f"Iniciando despliegue desatendido en producción ({API_URL})...")

    try:
        response = urllib.request.urlopen(req, timeout=10)
        print(f"Despliegue exitoso. Código de respuesta: {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Error HTTP en el despliegue: {e.code} - {e.reason}")
        # En caso de error HTTP, retornamos éxito parcial para no romper el flujo
        # a menos que sea un error crítico, pero aquí registramos y salimos
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Fallo de red en el despliegue: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"Error en el despliegue: {e}")
        sys.exit(1)

    print("Rutina de despliegue completada.")

if __name__ == "__main__":
    main()
