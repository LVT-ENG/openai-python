#!/usr/bin/env python3
"""
Unattended promotional content deployment routine.
This script monitors the 'promotions/' directory for new JSON files,
validates and deploys them using 'scripts/deploy_promotions.py',
and moves the processed files to 'promotions_processed/' or 'promotions_failed/'.
"""

import os
import re
import sys
import json
import time
import shutil
import argparse
import subprocess
from typing import Any, Dict, cast

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROMOTIONS_DIR = os.path.join(BASE_DIR, "promotions")
PROCESSED_DIR = os.path.join(BASE_DIR, "promociones_procesadas")
FAILED_DIR = os.path.join(BASE_DIR, "promociones_fallidas")

def setup_directories() -> None:
    os.makedirs(PROMOTIONS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FAILED_DIR, exist_ok=True)

def validar_promocion(data: Dict[str, Any]) -> None:
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            raise ValueError(f"Falta el campo requerido: {campo}")

def process_file(filepath: str, dry_run: bool) -> bool:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Procesando: {filepath}")

    exito = False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido_archivo = f.read()

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", contenido_archivo, re.DOTALL)
        if match:
            contenido_limpio = match.group(1).strip()
        else:
            contenido_limpio = contenido_archivo.strip()

        try:
            datos_cargados = json.loads(contenido_limpio)
        except json.JSONDecodeError as e:
            # Fallback en caso de que el LLM incluya texto extra
            if e.pos > 0:
                try:
                    datos_cargados = json.loads(contenido_limpio[:e.pos])
                except json.JSONDecodeError as err:
                    raise ValueError(f"Error parseando JSON incluso con el texto extra cortado.") from err
            else:
                 raise

        if not isinstance(datos_cargados, dict):
            raise ValueError("El archivo JSON debe contener un diccionario")

        datos = cast(Dict[str, Any], datos_cargados)
        validar_promocion(datos)
        print("Validación completada con éxito.")

        # Si el JSON era malformado pero lo pudimos arreglar, sobreescribimos el archivo
        # con la version correcta para que deploy_promotions.py (que requiere JSON puro) no falle.
        with open(filepath, "w", encoding="utf-8") as f:
             json.dump(datos, f)

        # Ejecutamos el script de despliegue
        cmd = [sys.executable, os.path.join(SCRIPT_DIR, "deploy_promotions.py"), filepath]
        if dry_run:
            cmd.append("--dry-run")

        result = subprocess.run(cmd, capture_output=False, env=os.environ)

        if result.returncode == 0:
            print("Despliegue automático ejecutado correctamente.")
            exito = True
        else:
             print("Fallo en la ejecución del despliegue.")
             exito = False

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error de validación o JSON en el contenido generado: {e}")
        exito = False
    except Exception as e:
        print(f"Error inesperado al procesar el archivo: {e}")
        exito = False

    filename = os.path.basename(filepath)
    if exito:
        print(f"Éxito: moviendo {filename} a {PROCESSED_DIR}")
        shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
        return True
    else:
        print(f"Fallo: moviendo {filename} a {FAILED_DIR}")
        shutil.move(filepath, os.path.join(FAILED_DIR, filename))
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Rutina de despliegue desatendido para promociones.")
    parser.add_argument("--dry-run", action="store_true", help="Simula el despliegue sin peticiones reales HTTP.")
    parser.add_argument("--interval", type=int, default=5, help="Intervalo de sondeo en segundos.")
    parser.add_argument("--once", action="store_true", help="Ejecutar una única pasada y salir.")
    args = parser.parse_args()

    setup_directories()

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: TRYONYOU_API_KEY no está definida y no estamos en dry-run.")
        sys.exit(1)

    print(f"Monitorizando '{PROMOTIONS_DIR}' por nuevas promociones (intervalo: {args.interval}s)...")
    if args.dry_run:
        print("Modo dry-run activado.")

    if args.once:
        files = [os.path.join(PROMOTIONS_DIR, f) for f in os.listdir(PROMOTIONS_DIR) if f.endswith('.json')]
        files.sort()
        for filepath in files:
             process_file(filepath, args.dry_run)
        print("Ejecución única completada.")
        return

    try:
        while True:
            # List all JSON files in the directory
            files = [os.path.join(PROMOTIONS_DIR, f) for f in os.listdir(PROMOTIONS_DIR) if f.endswith('.json')]
            files.sort()  # Process in alphabetical order

            current_time = time.time()
            for filepath in files:
                # To prevent race conditions with incomplete file writes,
                # only process files that haven't been modified in the last 2 seconds.
                try:
                    mtime = os.path.getmtime(filepath)
                    if current_time - mtime > 2.0:
                        process_file(filepath, args.dry_run)
                except OSError:
                    # File might have been removed or is inaccessible
                    pass

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nRutina detenida por el usuario.")
        sys.exit(0)

if __name__ == "__main__":
    main()
