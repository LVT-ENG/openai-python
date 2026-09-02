#!/usr/bin/env python3
"""
Script para automatizar la publicación de promociones para tryonyou.pro.
Toma el contenido promocional generado, valida su estructura y ejecuta
el despliegue automático en producción de forma desatendida.
"""

import os
import sys
import json
import time
import shutil
import urllib.error
import urllib.request
from typing import Any, Dict

API_URL = "https://api.tryonyou.pro/v1/promotions"
REQUIRED_FIELDS = ["title", "description", "discount_code", "valid_until"]

def validar_promocion(data: Dict[str, Any]) -> bool:
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"Falta el campo requerido: {field}")
    return True

def desplegar_promocion(data: Dict[str, Any], api_key: str) -> bool:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        title = data.get("title", "Unknown")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Desplegando promoción '{title}' en {API_URL}...")
        response = urllib.request.urlopen(req, timeout=10)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Despliegue exitoso. Código: {response.status}")
        return True
    except urllib.error.URLError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error al desplegar la promoción: {e}")
        return False
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error inesperado al desplegar: {e}")
        return False

def procesar_directorio(input_dir: str, processed_dir: str, failed_dir: str, api_key: str):
    for filename in os.listdir(input_dir):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(input_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("El archivo JSON no contiene un objeto/diccionario.")

            validar_promocion(data)

            exito = desplegar_promocion(data, api_key)

            if exito:
                shutil.move(filepath, os.path.join(processed_dir, filename))
                print(f"Movido {filename} a procesados.")
            else:
                shutil.move(filepath, os.path.join(failed_dir, filename))
                print(f"Movido {filename} a fallidos debido a error de despliegue.")

        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error procesando el archivo {filename}: {e}")
            shutil.move(filepath, os.path.join(failed_dir, filename))
            print(f"Movido {filename} a fallidos debido a error de procesamiento.")

def main():
    base_dir = os.path.abspath(os.path.dirname(__file__) + "/..")
    input_dir = os.path.join(base_dir, "promotions_inbox")
    processed_dir = os.path.join(base_dir, "promotions_processed")
    failed_dir = os.path.join(base_dir, "promotions_failed")

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    api_key = os.environ.get("TRYONYOU_API_KEY", "")
    if not api_key:
        print("ADVERTENCIA: TRYONYOU_API_KEY no está configurada. Usando clave por defecto para pruebas.")
        api_key = "default_test_key"

    # Si se pasa --run-once (para test), se corre solo una vez
    if "--run-once" in sys.argv:
        procesar_directorio(input_dir, processed_dir, failed_dir, api_key)
        sys.exit(0)

    print(f"Iniciando rutina desatendida. Monitorizando: {input_dir}")

    try:
        while True:
            procesar_directorio(input_dir, processed_dir, failed_dir, api_key)
            time.sleep(10) # Espera 10 segundos antes de volver a comprobar
    except KeyboardInterrupt:
        print("\nRutina detenida por el usuario.")

if __name__ == "__main__":
    main()
