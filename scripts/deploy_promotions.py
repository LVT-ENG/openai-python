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
            raise ValueError(f"Missing required field: {field}")
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
        print(f"Deploying promotion '{title}' to {api_url}...")
        response = urllib.request.urlopen(req)
        response_data = response.read()
        print(f"Deployment successful: {response_data}")
        return True
    except urllib.error.URLError as e:
        print(f"Failed to deploy: {e}")
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy promotional content for tryonyou.pro")
    parser.add_argument("file", help="Path to the JSON file containing promotional content")
    parser.add_argument("--api-url", default="https://api.tryonyou.pro/v1/promotions", help="API Endpoint URL")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment without making the HTTP request")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        sys.exit(1)

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            if not isinstance(loaded_data, dict):
                raise ValueError("JSON file must contain a dictionary")
            data = cast(Dict[str, Any], loaded_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    try:
        validate_promotion(data)
        print("Validation passed.")
    except ValueError as e:
        print(f"Validation failed: {e}")
        sys.exit(1)

    api_key = os.environ.get("TRYONYOU_API_KEY")
    if not api_key and not args.dry_run:
        print("Error: TRYONYOU_API_KEY environment variable is missing.")
        sys.exit(1)

    if args.dry_run:
        print("Simulating deployment (dry-run mode)...")
        print("Deployment successful.")
    else:
        if api_key is None:
            api_key = ""
        success = deploy_promotion(data, args.api_url, api_key)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
