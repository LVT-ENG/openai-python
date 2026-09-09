#!/usr/bin/env python3
# scripts/auto_deploy_v2.py
import os
import sys
import json
import urllib.error
import urllib.request


def validar_promocion(data):
    campos_requeridos = ["title", "description", "discount_code", "valid_until"]
    for campo in campos_requeridos:
        if campo not in data:
            print(f"Error: Falta el campo requerido: {campo}")
            return False
    return True

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/auto_deploy_v2.py <ruta_al_archivo_json>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")
        sys.exit(1)

    if not validar_promocion(data):
        sys.exit(1)

    api_key = os.environ.get("TRYONYOU_API_KEY", "default_key_if_none")
    api_url = "https://api.tryonyou.pro/v1/promotions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(api_url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    try:
        titulo = data.get("title", "Sin título")
        print(f"Desplegando promoción '{titulo}' en {api_url}...")

        # En el entorno de desarrollo podemos simular la petición si queremos, pero el script
        # debe estar preparado para producción.
        # Aquí controlamos errores de red gracefully.
        respuesta = urllib.request.urlopen(req)
        respuesta_texto = respuesta.read().decode("utf-8")
        print(f"Despliegue exitoso: {respuesta_texto}")
        sys.exit(0)
    except urllib.error.URLError as e:
        print(f"Error en el despliegue (esto es normal si la URL es falsa/dry-run o no hay internet): {e}")
        # En caso de error de red, devolvemos 0 si el entorno permite fallar, pero 1 para el wrapper
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
