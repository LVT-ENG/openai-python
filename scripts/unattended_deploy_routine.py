#!/usr/bin/env python3
"""
Unattended promotional content deployment routine.
This script monitors the 'promotions/' directory for new JSON files,
validates and deploys them using 'scripts/deploy_promotions.py',
and moves the processed files to 'promotions_processed/' or 'promotions_failed/'.
"""

import os
import sys
import time
import shutil
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROMOTIONS_DIR = os.path.join(BASE_DIR, "promotions")
PROCESSED_DIR = os.path.join(BASE_DIR, "promotions_processed")
FAILED_DIR = os.path.join(BASE_DIR, "promotions_failed")

def setup_directories() -> None:
    os.makedirs(PROMOTIONS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FAILED_DIR, exist_ok=True)

def process_file(filepath: str, dry_run: bool) -> bool:
    print(f"Processing: {filepath}")

    cmd = [sys.executable, os.path.join(BASE_DIR, "scripts", "deploy_promotions.py"), filepath]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, capture_output=False)

    filename = os.path.basename(filepath)
    if result.returncode == 0:
        print(f"Success: moving {filename} to {PROCESSED_DIR}")
        shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
        return True
    else:
        print(f"Failure: moving {filename} to {FAILED_DIR}")
        shutil.move(filepath, os.path.join(FAILED_DIR, filename))
        return False

def main() -> None:
    parser = argparse.ArgumentParser(description="Unattended deployment routine for promotions.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment without making HTTP requests.")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds.")
    args = parser.parse_args()

    setup_directories()

    print(f"Monitoring '{PROMOTIONS_DIR}' for new promotions (interval: {args.interval}s)...")
    if args.dry_run:
        print("Running in dry-run mode.")

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
        print("\nRoutine stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
