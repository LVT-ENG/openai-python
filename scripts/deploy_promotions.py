#!/usr/bin/env python3
"""
Deploy a single promotion from a JSON file.
Usage: scripts/deploy_promotions.py <filepath> [--dry-run]
"""

import os
import sys
import json
import argparse
import urllib.error
import urllib.request
from typing import Any, Dict, cast


def validate_promotion(data: Dict[str, Any]) -> None:
    required_fields = ["title", "description", "discount_code", "valid_until"]
    for field in required_fields:
        if field not in data:
            print(f"Validation Error: Missing required field '{field}'")
            sys.exit(1)


def deploy_promotion(data: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        print("Dry-run mode: Validation passed. Simulating deployment...")
        print("Dry-run deployment successful.")
        sys.exit(0)

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key:
        print("Deployment Error: TRYONYOU_API_KEY environment variable is not set.")
        sys.exit(1)

    api_url = "https://api.tryonyou.pro/v1/promotions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    req = urllib.request.Request(api_url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    try:
        title = data.get("title", "No Title")
        print(f"Deploying promotion '{title}' to {api_url}...")
        response = urllib.request.urlopen(req)
        response_data = response.read()

        try:
            response_text = response_data.decode("utf-8")
        except UnicodeDecodeError:
            response_text = str(response_data)

        print(f"Deployment successful: {response_text}")
        sys.exit(0)
    except urllib.error.URLError as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy a promotion from a JSON file.")
    parser.add_argument("filepath", help="Path to the JSON promotion file.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment without HTTP request.")
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print(f"Error: File '{args.filepath}' does not exist.")
        sys.exit(1)

    try:
        with open(args.filepath, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
            if not isinstance(loaded_data, dict):
                print("Error: JSON file must contain a dictionary object.")
                sys.exit(1)
            data = cast(Dict[str, Any], loaded_data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    validate_promotion(data)
    deploy_promotion(data, args.dry_run)


if __name__ == "__main__":
    main()
