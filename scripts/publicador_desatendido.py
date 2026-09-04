#!/usr/bin/env python3
import os
import json
from typing import Any, Dict


def validar_promocion(data: Dict[str, Any]) -> bool:
    """Valida que los datos de la promoción contengan los campos requeridos."""
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            raise ValueError(f"Falta el campo requerido: {campo}")
    return True

def parsear_archivo(ruta_archivo: str) -> Dict[str, Any]:
    """Lee y parsea un archivo JSON de promoción."""
    from typing import cast
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
        if not isinstance(datos, dict):
            raise ValueError("El archivo JSON debe contener un diccionario")
        return cast(Dict[str, Any], datos)

def desplegar_promocion(data: Dict[str, Any], api_url: str, api_key: str, dry_run: bool = False) -> bool:
    """Ejecuta el despliegue automático en producción o simula en modo dry-run."""
    if dry_run:
        print(f"Simulando el despliegue de '{data.get('title')}' (modo dry-run)...")
        return True

    if not api_key:
        print("Error: TRYONYOU_API_KEY no configurada. Usa --dry-run para simular.")
        return False

    import urllib.error
    import urllib.request

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(
        api_url,
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    try:
        titulo = data.get("title", "Sin título")
        print(f"Desplegando promoción '{titulo}' en {api_url}...")
        respuesta = urllib.request.urlopen(req)
        print(f"Despliegue exitoso: {respuesta.read().decode('utf-8')}")
        return True
    except urllib.error.URLError as e:
        print(f"Error en el despliegue: {e}")
        return False

def ciclo_monitoreo(directorio_base: str, api_url: str, api_key: str, dry_run: bool = False, intervalo_segundos: int = 5) -> None:
    """Monitorea infinitamente un directorio en busca de promociones para desplegar."""
    import time
    import shutil

    dir_promociones = os.path.join(directorio_base, "promotions")
    dir_procesadas = os.path.join(directorio_base, "promotions_processed")
    dir_fallidas = os.path.join(directorio_base, "promotions_failed")

    for directorio in [dir_promociones, dir_procesadas, dir_fallidas]:
        os.makedirs(directorio, exist_ok=True)

    print(f"Iniciando monitoreo de {dir_promociones} cada {intervalo_segundos} segundos...")
    if dry_run:
        print("Modo DRY-RUN activado. No se realizarán peticiones reales.")

    while True:
        try:
            archivos = [f for f in os.listdir(dir_promociones) if f.endswith(".json")]
            for archivo in archivos:
                ruta_archivo = os.path.join(dir_promociones, archivo)
                print(f"Encontrado nuevo archivo: {archivo}")
                exito = False
                try:
                    datos = parsear_archivo(ruta_archivo)
                    validar_promocion(datos)
                    exito = desplegar_promocion(datos, api_url, api_key, dry_run)
                except Exception as e:
                    print(f"Error procesando {archivo}: {e}")

                if exito:
                    shutil.move(ruta_archivo, os.path.join(dir_procesadas, archivo))
                    print(f"Movido {archivo} a procesadas.")
                else:
                    shutil.move(ruta_archivo, os.path.join(dir_fallidas, archivo))
                    print(f"Movido {archivo} a fallidas.")

            time.sleep(intervalo_segundos)
        except KeyboardInterrupt:
            print("Deteniendo el monitoreo por interrupción del usuario.")
            break
        except Exception as e:
            print(f"Error en el ciclo de monitoreo: {e}")
            time.sleep(intervalo_segundos)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automatiza la publicación desatendida de promociones.")
    parser.add_argument("--api-url", default="https://api.tryonyou.pro/v1/promotions", help="URL de la API de promociones.")
    parser.add_argument("--dry-run", action="store_true", help="Simula el despliegue sin realizar llamadas de red.")
    parser.add_argument("--intervalo", type=int, default=5, help="Intervalo de sondeo en segundos (por defecto 5).")

    args = parser.parse_args()

    api_key = os.environ.get("TRYONYOU_API_KEY", "")

    ciclo_monitoreo(
        directorio_base=os.getcwd(),
        api_url=args.api_url,
        api_key=api_key,
        dry_run=args.dry_run,
        intervalo_segundos=args.intervalo
    )
