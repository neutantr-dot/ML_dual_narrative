import requests
import csv
import os
from datetime import datetime

# GitHub raw URL for classification.csv
GITHUB_RAW_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/classification.csv"

# Allowed classification labels
ALLOWED_LABELS = ["F1", "F2", "F3", "M1", "M2", "M3", "N/A"]

# Default header if GitHub fetch fails
DEFAULT_HEADER = ["F1", "F2", "F3", "M1", "M2", "M3", "1=naieve", "2=in the know", "3=in transition"]

def validate_classification(label):
    """Ensures the label is valid; returns 'N/A' if not."""
    return label if label in ALLOWED_LABELS else "N/A"

def fetch_classification_csv():
    """Fetches classification.csv from GitHub or returns default header."""
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()
        lines = response.text.splitlines()
        return [line.strip().split(",") for line in lines]
    except Exception:
        print("⚠️ Could not fetch from GitHub. Using default header.")
        return [DEFAULT_HEADER]

def generate_session_label(existing_rows):
    """Generates a session label like 'Mon Sep 08, 2025 (3)'."""
    today = datetime.now().strftime("%a %b %d, %Y")
    count = sum(1 for row in existing_rows[1:] if row and row[0].startswith(today))
    return f"{today} ({count + 1})"

def append_classification_row(session_label, user_id, raw_label, local_path="classification.csv"):
    """Appends a new classification row to the local file."""
    rows = fetch_classification_csv()
    validated_label = validate_classification(raw_label)
    new_row = [session_label, user_id, validated_label]

    # If file doesn't exist locally, write header first
    if not os.path.exists(local_path):
        with open(local_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(DEFAULT_HEADER)

    # Append new row
    with open(local_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(new_row)

    print(f"✅ Classification saved: {new_row}")

# Example usage
if __name__ == "__main__":
    existing_rows = fetch_classification_csv()
    session_label = generate_session_label(existing_rows)
    user_id = "user 1"
    raw_label = "M3"  # Replace with actual output from your copilot

    append_classification_row(session_label, user_id, raw_label)


