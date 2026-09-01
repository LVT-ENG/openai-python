#!/usr/bin/env python3
import os
import sys
import json
import argparse
import urllib.error
import urllib.request
from typing import Any, Dict, cast


def validate_promotion(data: Dict[str, Any]) -> bool:
    required_fields = ["title", "description", "discount_code", "valid_until"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Falta un campo requerido: {field}")
    return True

def deploy_promotion(data: Dict[str, Any], api_url: str, api_key: str) -> bool:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(api_url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        title = data.get("title")
        if not isinstance(title, str):
            title = str(title)
        print(f"Desplegando promoción '{title}' en {api_url}...")
        response = urllib.request.urlopen(req)
        response_data = response.read()
        print(f"Despliegue exitoso: {response_data}")
        return True
    except urllib.error.URLError as e:
        print(f"Error al desplegar: {e}")
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Desplegar contenido promocional para tryonyou.pro")
    parser.add_argument("file", help="Ruta al archivo JSON que contiene el contenido promocional")
    parser.add_argument("--api-url", default="https://api.tryonyou.pro/v1/promotions", help="URL del endpoint de la API")
    parser.add_argument("--dry-run", action="store_true", help="Simular despliegue sin realizar la petición HTTP")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: El archivo {args.file} no existe.")
        sys.exit(1)

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            if not isinstance(loaded_data, dict):
                raise ValueError("El archivo JSON debe contener un diccionario")
            data = cast(Dict[str, Any], loaded_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error al procesar JSON: {e}")
        sys.exit(1)

    try:
        validate_promotion(data)
        print("Validación exitosa.")
    except ValueError as e:
        print(f"Fallo en la validación: {e}")
        sys.exit(1)

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: La variable de entorno TRYONYOU_API_KEY no está configurada.")
        sys.exit(1)

    if args.dry_run:
        print("Simulando despliegue (modo dry-run)...")
        print("Despliegue simulado exitoso.")
    else:
        if api_key is None:
            api_key = ""
        success = deploy_promotion(data, args.api_url, api_key)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
