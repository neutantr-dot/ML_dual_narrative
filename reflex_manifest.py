import csv
from collections import defaultdict

def load_csv(path):
    """Loads a CSV file and returns a list of dictionaries."""
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_reflex_manifest(transmission_map_path):
    """
    Builds a manifest of reflexes grouped by wheel state.
    Returns a dictionary: {wheel_state: [reflex_type, ...]}
    """
    manifest = defaultdict(list)
    try:
        rows = load_csv(transmission_map_path)
        for row in rows:
            wheel = row.get("wheel_state", "").strip().lower()
            reflex = row.get("reflex_type", "").strip()
            if wheel and reflex and reflex not in manifest[wheel]:
                manifest[wheel].append(reflex)
    except Exception as e:
        print(f"⚠️ Manifest generation failed: {e}")
    return dict(manifest)

def preview_manifest(manifest):
    """
    Prints a readable preview of the reflex manifest.
    """
    print("🧠 Reflex Manifest by Wheel State:")
    for wheel_state, reflexes in manifest.items():
        print(f"  • {wheel_state.capitalize()}:")
        for reflex in reflexes:
            print(f"     - {reflex}")