#!/usr/bin/env python3
# scripts/daemon_promociones.py
# Script para automatizar la publicación de promociones de forma desatendida.
# Este script funciona como un daemon (bucle infinito) que monitorea un directorio
# y publica los archivos JSON de promociones en la API.

import os
import sys
import json
import shutil
import argparse
import time
import urllib.error
import urllib.request
from typing import Any, Dict, cast

def validar_promocion(data: Dict[str, Any]) -> bool:
    """Valida la estructura de una promoción asegurando los campos mínimos."""
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            raise ValueError(f"Falta el campo requerido: {campo}")
    return True

def desplegar_promocion(data: Dict[str, Any], api_url: str, api_key: str) -> bool:
    """Ejecuta el despliegue automático enviando los datos a la API de producción."""
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

        try:
            respuesta_texto = datos_respuesta.decode('utf-8')
        except UnicodeDecodeError:
            respuesta_texto = str(datos_respuesta)

        print(f"Despliegue exitoso: {respuesta_texto}")
        return True
    except urllib.error.URLError as e:
        print(f"Error en el despliegue: {e}")
        return False

def procesar_archivos(dir_promociones: str, dir_procesadas: str, dir_fallidas: str, api_url: str, api_key: str, dry_run: bool) -> None:
    """Revisa el directorio por archivos nuevos y los procesa."""
    for nombre_archivo in os.listdir(dir_promociones):
        if not nombre_archivo.endswith('.json'):
            continue

        ruta_archivo = os.path.join(dir_promociones, nombre_archivo)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Procesando: {ruta_archivo}")

        exito = False
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                datos_cargados = json.load(f)
                if not isinstance(datos_cargados, dict):
                    raise ValueError("El archivo JSON debe contener un diccionario")
                datos = cast(Dict[str, Any], datos_cargados)

            validar_promocion(datos)
            print("Validación completada con éxito.")

            if dry_run:
                print("Simulando el despliegue (modo dry-run)...")
                print("Despliegue simulado exitoso.")
                exito = True
            else:
                exito = desplegar_promocion(datos, api_url, api_key)

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

def main() -> None:
    parser = argparse.ArgumentParser(description="Daemon para automatizar la publicación desatendida de promociones para tryonyou.pro")
    parser.add_argument("--api-url", default="https://api.tryonyou.pro/v1/promotions", help="URL del Endpoint de la API")
    parser.add_argument("--dry-run", action="store_true", help="Simula el despliegue sin hacer la petición HTTP")
    parser.add_argument("--interval", type=int, default=5, help="Intervalo en segundos para revisar el directorio")
    parser.add_argument("--once", action="store_true", help="Ejecutar solo una vez en lugar de modo daemon")
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
        print("Error: Falta la variable de entorno TRYONYOU_API_KEY y no se ha especificado --dry-run.")
        sys.exit(1)

    print(f"Iniciando daemon de promociones en directorio: {dir_promociones}")
    if args.dry_run:
        print("Modo DRY RUN activado.")

    if args.once:
        procesar_archivos(dir_promociones, dir_procesadas, dir_fallidas, args.api_url, api_key or "", args.dry_run)
        print("Ejecución única completada.")
        return

    # Bucle infinito (daemon)
    try:
        while True:
            procesar_archivos(dir_promociones, dir_procesadas, dir_fallidas, args.api_url, api_key or "", args.dry_run)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nDaemon detenido por el usuario.")

if __name__ == "__main__":
    main()
