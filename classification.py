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

def generate_session_label(existing_labels):
    """Generates a session label like 'Sun Sep 07, 2025 (3)' based on today's date and count."""
    today = datetime.now().strftime("%a %b %d, %Y")
    count = sum(1 for label in existing_labels if label.startswith(today))
    return f"{today} ({count + 1})"

def insert_classification_column(new_entry, local_path="classification.csv"):
    """Inserts a new classification entry as the first column in row 1 onward. Row 0 (header) remains untouched."""
    rows = fetch_classification_csv()

    # Ensure header row exists
    if not rows:
        header = ["F1", "F2", "F3", "M1", "M2", "M3", "1=naieve", "2=in the know", "3=in transition"]
        rows = [header, [new_entry]]
    else:
        # Insert new entry as first column in row 1 onward
        for i in range(len(rows)):
            if i == 0:
                continue  # Leave header untouched
            elif i == 1:
                rows[i].insert(0, new_entry)
            else:
                rows[i].insert(0, "")

    # Save locally
    with open(local_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"✅ New classification inserted: {new_entry}")

# Example usage
if __name__ == "__main__":
    # Fetch existing labels from row 1
    existing_rows = fetch_classification_csv()
    existing_labels = existing_rows[1] if len(existing_rows) > 1 else []

    # Generate session label
    session_label = generate_session_label(existing_labels)

    # Define user and classification result
    user_id = "user 1"
    classification = "M3"

    # Compose entry
    new_entry = f"{session_label}, {user_id}, {classification}"

    # Insert into classification.csv
    insert_classification_column(new_entry)
