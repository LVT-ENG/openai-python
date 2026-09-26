#!/usr/bin/env python3
"""
Rutina de Despliegue Automático de Promociones (TryOnYou.pro)
Monitorea un directorio para detectar nuevo contenido promocional generado,
valida su estructura mediante Pydantic y ejecuta el despliegue en producción.
"""

import os
import re
import sys
import json
import time
import shutil
import argparse
import urllib.error
import urllib.request
from typing import Any, Dict, List, cast

from pydantic import BaseModel, ValidationError

# Directorios
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROMOTIONS_DIR = os.path.join(BASE_DIR, "promociones")
PROCESSED_DIR = os.path.join(BASE_DIR, "promociones_procesadas")
FAILED_DIR = os.path.join(BASE_DIR, "promociones_fallidas")


class Promocion(BaseModel):
    title: str
    description: str
    discount_code: str
    valid_until: str


def setup_directories() -> None:
    os.makedirs(PROMOTIONS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FAILED_DIR, exist_ok=True)


def extraer_json_robusto(contenido_archivo: str) -> Any:
    """
    Extrae JSON generado por un LLM.
    Busca bloques de markdown, delimitadores {} y [], y tiene un fallback con e.pos.
    """
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", contenido_archivo, re.DOTALL)
    if match:
        contenido_limpio = match.group(1).strip()
    else:
        contenido_limpio = contenido_archivo.strip()

    start_obj = contenido_limpio.find("{")
    end_obj = contenido_limpio.rfind("}")

    start_arr = contenido_limpio.find("[")
    end_arr = contenido_limpio.rfind("]")

    is_obj = start_obj != -1 and end_obj != -1 and end_obj > start_obj
    is_arr = start_arr != -1 and end_arr != -1 and end_arr > start_arr

    if is_obj and is_arr:
        if start_obj < start_arr:
            is_arr = False
        else:
            is_obj = False

    if is_obj:
        contenido_limpio = contenido_limpio[start_obj : end_obj + 1]
    elif is_arr:
        contenido_limpio = contenido_limpio[start_arr : end_arr + 1]

    try:
        return json.loads(contenido_limpio)
    except json.JSONDecodeError as e:
        if e.pos > 0:
            try:
                return json.loads(contenido_limpio[: e.pos])
            except json.JSONDecodeError as err:
                raise ValueError("Error parseando JSON incluso con el texto extra cortado.") from err
        raise


def validar_promocion(datos: Any) -> List[Promocion]:
    """Valida los datos usando Pydantic."""
    if isinstance(datos, dict):
        # pyright ignora tipos en el unpacking, por lo que convertimos
        data_dict = cast(Dict[str, Any], datos)
        return [Promocion(**data_dict)]
    elif isinstance(datos, list):
        lista_datos = cast(List[Dict[str, Any]], datos)
        return [Promocion(**item) for item in lista_datos]
    else:
        raise ValueError("El JSON debe ser un objeto o una lista de objetos.")


def desplegar_promocion(promo: Promocion, api_url: str, api_key: str, dry_run: bool) -> bool:
    if dry_run:
        print(f"Modo dry-run: Despliegue simulado exitoso para '{promo.title}'.")
        return True

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # Soporta Pydantic v1 y v2
    if hasattr(promo, "model_dump"):
        promo_dict = promo.model_dump()
    else:
        promo_dict = getattr(promo, "dict")()  # noqa: B009
    data_json = json.dumps(promo_dict)

    req = urllib.request.Request(api_url, data=data_json.encode("utf-8"), headers=headers, method="POST")
    try:
        print(f"Desplegando promoción '{promo.title}' en {api_url}...")
        respuesta = urllib.request.urlopen(req)
        datos_respuesta = respuesta.read()

        try:
            respuesta_texto = datos_respuesta.decode("utf-8")
        except UnicodeDecodeError:
            respuesta_texto = str(datos_respuesta)

        print(f"Despliegue exitoso: {respuesta_texto}")
        return True
    except urllib.error.URLError as e:
        print(f"Error en el despliegue: {e}")
        return False


def procesar_archivo(filepath: str, api_url: str, api_key: str, dry_run: bool) -> bool:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Procesando: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            contenido = f.read()

        datos_cargados = extraer_json_robusto(contenido)
        promociones = validar_promocion(datos_cargados)

        exito_total = True
        for promo in promociones:
            exito = desplegar_promocion(promo, api_url, api_key, dry_run)
            if not exito:
                exito_total = False

        return exito_total
    except ValidationError as e:
        print(f"Error de validación Pydantic en {filepath}:\n{e}")
        return False
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error de formato JSON en {filepath}: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al procesar {filepath}: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Rutina automática para validar y desplegar promociones generadas.")
    parser.add_argument(
        "--api-url", default="https://api.tryonyou.pro/v1/promotions", help="URL del Endpoint de la API"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simula el despliegue sin hacer peticiones HTTP")
    parser.add_argument("--interval", type=int, default=5, help="Intervalo de sondeo en segundos")
    parser.add_argument("--once", action="store_true", help="Ejecutar una única pasada y salir")
    args = parser.parse_args()

    setup_directories()

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: Falta la variable de entorno TRYONYOU_API_KEY y no se ha especificado --dry-run.")
        sys.exit(1)

    print(f"Monitorizando '{PROMOTIONS_DIR}' por nuevas promociones (intervalo: {args.interval}s)...")
    if args.dry_run:
        print("Modo dry-run activado.")

    if args.once:
        files = [os.path.join(PROMOTIONS_DIR, f) for f in os.listdir(PROMOTIONS_DIR) if f.endswith(".json")]
        files.sort()
        for filepath in files:
            exito = procesar_archivo(filepath, args.api_url, api_key or "", args.dry_run)
            filename = os.path.basename(filepath)
            if exito:
                print(f"Éxito: moviendo {filename} a promociones_procesadas")
                shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
            else:
                print(f"Fallo: moviendo {filename} a promociones_fallidas")
                shutil.move(filepath, os.path.join(FAILED_DIR, filename))
        print("Ejecución única completada.")
        return

    try:
        while True:
            files = [os.path.join(PROMOTIONS_DIR, f) for f in os.listdir(PROMOTIONS_DIR) if f.endswith(".json")]
            files.sort()

            current_time = time.time()
            for filepath in files:
                try:
                    mtime = os.path.getmtime(filepath)
                    if current_time - mtime > 2.0:
                        exito = procesar_archivo(filepath, args.api_url, api_key or "", args.dry_run)
                        filename = os.path.basename(filepath)
                        if exito:
                            print(f"Éxito: moviendo {filename} a promociones_procesadas")
                            shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
                        else:
                            print(f"Fallo: moviendo {filename} a promociones_fallidas")
                            shutil.move(filepath, os.path.join(FAILED_DIR, filename))
                except OSError:
                    pass
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nRutina detenida por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    main()
