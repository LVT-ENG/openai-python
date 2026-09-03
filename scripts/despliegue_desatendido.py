#!/usr/bin/env python3
import os
import sys
import json
import shutil
import argparse
import urllib.error
import urllib.request
from typing import Any, Dict, cast


def validar_promocion(data: Dict[str, Any]) -> bool:
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            raise ValueError(f"Falta el campo requerido: {campo}")
    return True

def procesar_archivos(directorio_base: str, dry_run: bool) -> None:
    dir_promociones = os.path.join(directorio_base, "promotions")
    dir_procesados = os.path.join(directorio_base, "promotions_processed")
    dir_fallidos = os.path.join(directorio_base, "promotions_failed")

    for directorio in [dir_promociones, dir_procesados, dir_fallidos]:
        os.makedirs(directorio, exist_ok=True)

    api_url = "https://api.tryonyou.pro/v1/promotions"
    api_key = os.environ.get("TRYONYOU_API_KEY", "")

    if not api_key and not dry_run:
        print("Error: La variable de entorno TRYONYOU_API_KEY no está configurada.")
        sys.exit(1)

    archivos = [f for f in os.listdir(dir_promociones) if f.endswith(".json")]
    if not archivos:
        print(f"No se encontraron archivos JSON en {dir_promociones}")
        return

    for archivo in archivos:
        ruta_archivo = os.path.join(dir_promociones, archivo)
        print(f"Procesando archivo: {archivo}")

        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_raw = json.load(f)
                if not isinstance(datos_raw, dict):
                    raise ValueError("El archivo JSON debe contener un diccionario")
                datos = cast(Dict[str, Any], datos_raw)

            validar_promocion(datos)
            print("Validación completada.")

            exito = False
            if dry_run:
                print(f"Simulando despliegue de '{datos.get('title')}' (dry-run)...")
                exito = True
            else:
                print(f"Desplegando promoción '{datos.get('title')}' a {api_url}...")
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                req = urllib.request.Request(api_url, data=json.dumps(datos).encode('utf-8'), headers=headers, method='POST')
                try:
                    response = urllib.request.urlopen(req)
                    print(f"Despliegue exitoso: {response.read()}")
                    exito = True
                except urllib.error.URLError as e:
                    print(f"Fallo en el despliegue: {e}")
                    exito = False

            if exito:
                shutil.move(ruta_archivo, os.path.join(dir_procesados, archivo))
                print(f"Movido {archivo} a {dir_procesados}")
            else:
                shutil.move(ruta_archivo, os.path.join(dir_fallidos, archivo))
                print(f"Movido {archivo} a {dir_fallidos}")

        except Exception as e:
            print(f"Error procesando {archivo}: {e}")
            shutil.move(ruta_archivo, os.path.join(dir_fallidos, archivo))
            print(f"Movido {archivo} a {dir_fallidos}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Despliegue desatendido de promociones")
    parser.add_argument("--dry-run", action="store_true", help="Simular despliegue sin hacer peticiones HTTP")
    args = parser.parse_args()

    directorio_base = os.getcwd()
    procesar_archivos(directorio_base, args.dry_run)
    print("Procesamiento completado.")
