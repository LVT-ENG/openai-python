#!/bin/bash

# Default to promotion_example.json if no argument is provided
PROMO_FILE="${1:-promotion_example.json}"

if [ ! -f "$PROMO_FILE" ]; then
    echo "Error: Promotional content file '$PROMO_FILE' not found."
    exit 1
fi

# Check if API key is provided for unattended deployment
if [ -z "$TRYONYOU_API_KEY" ]; then
    echo "Warning: TRYONYOU_API_KEY environment variable is not set."
    echo "Running deployment in dry-run mode for validation..."
    DRY_RUN="--dry-run"
else
    echo "TRYONYOU_API_KEY is set. Proceeding with production deployment..."
    DRY_RUN=""
fi

# Execute the deployment script
echo "Executing deployment..."
python3 scripts/deploy_promotions.py "$PROMO_FILE" $DRY_RUN

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Routine completed successfully."
else
    echo "Routine failed with exit code $EXIT_CODE."
    exit $EXIT_CODE
fi
