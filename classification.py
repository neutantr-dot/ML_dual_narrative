import requests
import csv
import os
from datetime import datetime

# GitHub raw URL for classification.csv
GITHUB_RAW_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/classification.csv"

def fetch_classification_csv():
    """Fetches classification.csv from GitHub and returns it as a list of rows."""
    response = requests.get(GITHUB_RAW_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
    return [line.strip().split(",") for line in lines]

def generate_session_label(existing_rows):
    """Generates a session label like 'Sun Sep 07, 2025 (3)' based on today's date and count."""
    today = datetime.now().strftime("%a %b %d, %Y")
    count = sum(1 for row in existing_rows[1:] if row and row[0].startswith(today))
    return f"{today} ({count + 1})"

def append_classification_row(session_label, user_id, classification, local_path="classification.csv"):
    """Appends a new classification row to the local file, preserving the header."""
    rows = fetch_classification_csv()

    # Compose new row
    new_row = [session_label, user_id, classification]

    # Append to rows
    rows.append(new_row)

    # Save locally
    with open(local_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"✅ New classification appended: {new_row}")

# Example usage
if __name__ == "__main__":
    existing_rows = fetch_classification_csv()
    session_label = generate_session_label(existing_rows)
    user_id = "user 1"
    classification = "M3"

    append_classification_row(session_label, user_id, classification)

