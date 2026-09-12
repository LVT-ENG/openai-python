#!/usr/bin/env python3
# scripts/auto_deploy_v2.py
import sys
import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any

def validar_promocion(data: Dict[str, Any]) -> None:
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            raise ValueError(f"Falta el campo requerido: {campo}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 auto_deploy_v2.py <ruta_al_archivo_json>")
        sys.exit(1)

    archivo = sys.argv[1]

    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo}'.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: El archivo no es un JSON válido. Detalles: {e}")
        sys.exit(1)

    try:
        validar_promocion(data)
    except ValueError as e:
        print(f"Error de validación: {e}")
        sys.exit(1)

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key:
        print("Error: La variable de entorno TRYONYOU_API_KEY no está definida.")
        sys.exit(1)

    api_url = "https://api.tryonyou.pro/v1/promotions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        req = urllib.request.Request(api_url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        response = urllib.request.urlopen(req)
        response_body = response.read().decode('utf-8')
        print(f"Despliegue exitoso. Respuesta de la API: {response_body}")
    except urllib.error.URLError as e:
        print(f"Error en el despliegue de red o HTTP: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado durante el despliegue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
