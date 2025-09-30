import csv

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_reflex_manifest(transmission_map_path):
    manifest = {}
    rows = load_csv(transmission_map_path)
    for row in rows:
        wheel = row.get("wheel_state", "neutral")
        reflex = row.get("reflex_type", "unspecified")
        if wheel not in manifest:
            manifest[wheel] = []
        manifest[wheel].append(reflex)
    return manifest

def preview_manifest(manifest):
    """
    Prints a readable preview of the reflex manifest.
    """
    print("🧠 Reflex Manifest by Wheel State:")
    for wheel_state, reflexes in manifest.items():
        print(f"  • {wheel_state.capitalize()}:")
        for reflex in reflexes:
            print(f"     - {reflex}")
