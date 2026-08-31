#!/usr/bin/env python3
# scripts/rutina_promociones.py
# Script para automatizar la publicación de promociones de forma desatendida.

import os
import sys
import json
import argparse
import shutil
import urllib.error
import urllib.request
from typing import Any, Dict, cast

def validar_promocion(data: Dict[str, Any]) -> bool:
    """Valida la estructura de una promoción."""
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            raise ValueError(f"Falta el campo requerido: {campo}")
    return True

def desplegar_promocion(data: Dict[str, Any], api_url: str, api_key: str) -> bool:
    """Ejecuta el despliegue automático en producción."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(api_url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        titulo = data.get("title", "Sin título")
        print(f"Desplegando promoción '{titulo}' en {api_url}...")
        respuesta = urllib.request.urlopen(req)
        datos_respuesta = respuesta.read()
        print(f"Despliegue exitoso: {datos_respuesta.decode('utf-8') if isinstance(datos_respuesta, bytes) else datos_respuesta}")
        return True
    except urllib.error.URLError as e:
        print(f"Error en el despliegue: {e}")
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Automatiza la publicación de promociones para tryonyou.pro")
    parser.add_argument("--api-url", default="https://api.tryonyou.pro/v1/promotions", help="URL del Endpoint de la API")
    parser.add_argument("--dry-run", action="store_true", help="Simula el despliegue sin hacer la petición HTTP")
    args = parser.parse_args()

    directorio_base = os.getcwd()
    dir_promociones = os.path.join(directorio_base, "promociones")
    dir_procesadas = os.path.join(directorio_base, "promociones_procesadas")
    dir_fallidas = os.path.join(directorio_base, "promociones_fallidas")

    # Crear directorios si no existen
    for directorio in [dir_promociones, dir_procesadas, dir_fallidas]:
        os.makedirs(directorio, exist_ok=True)

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: Falta la variable de entorno TRYONYOU_API_KEY.")
        sys.exit(1)

    archivos_procesados = 0
    if not os.path.exists(dir_promociones):
        print(f"El directorio '{dir_promociones}' no existe.")
        sys.exit(0)

    for nombre_archivo in os.listdir(dir_promociones):
        if not nombre_archivo.endswith('.json'):
            continue

        ruta_archivo = os.path.join(dir_promociones, nombre_archivo)
        print(f"Procesando: {ruta_archivo}")
        archivos_procesados += 1

        exito = False
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
                if not isinstance(datos_cargados, dict):
                    raise ValueError("El archivo JSON debe contener un diccionario")
                datos = cast(Dict[str, Any], datos_cargados)

            validar_promocion(datos)
            print("Validación completada con éxito.")

            if args.dry_run:
                print("Simulando el despliegue (modo dry-run)...")
                print("Despliegue simulado exitoso.")
                exito = True
            else:
                exito = desplegar_promocion(datos, args.api_url, api_key or "")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error al procesar JSON o validar: {e}")
            exito = False
        except Exception as e:
            print(f"Error inesperado: {e}")
            exito = False

        if exito:
            print(f"Éxito: moviendo a {dir_procesadas}")
            shutil.move(ruta_archivo, os.path.join(dir_procesadas, nombre_archivo))
        else:
            print(f"Fallo: moviendo a {dir_fallidas}")
            shutil.move(ruta_archivo, os.path.join(dir_fallidas, nombre_archivo))

    if archivos_procesados == 0:
        print(f"No se encontraron archivos JSON en {dir_promociones}.")

    print("Rutina de automatización completada.")

if __name__ == "__main__":
    main()
