import csv
import os
from geometry_resolver import resolve_geometry_state

# === CSV Loader ===
def load_csv(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"?? Failed to load CSV: {e}")
        return []

# === Manifest Builder ===
def get_reflex_manifest(transmission_map_path):
    manifest = {}
    rows = load_csv(transmission_map_path)

    # Normalize column name for backward compatibility
    for row in rows:
        if "wheel_state" in row:
            row["reflex_wheel_state"] = row["wheel_state"]

        wheel = row.get("reflex_wheel_state", "neutral")
        reflex = row.get("reflex_type", "unspecified")

        if wheel not in manifest:
            manifest[wheel] = []
        manifest[wheel].append(reflex)

    return manifest

# === Manifest Preview with Geometry Overlay ===
def preview_manifest(manifest, modules={}):
    """
    Prints a readable preview of the reflex manifest with symbolic overlays.
    """
    print("?? Reflex Manifest by Wheel State:")
    for wheel_state, reflexes in manifest.items():
        print(f"  ?? {wheel_state.capitalize()}:")
        for reflex in reflexes:
            print(f"     - {reflex}")

        # Inject geometry overlay preview
        overlay = resolve_geometry_state(
            wheel_domains={
                "blue": wheel_state,
                "red": wheel_state,
                "yellow": wheel_state,
                "green": wheel_state,
                "centre": wheel_state
            },
            layers_path=os.path.join(modules.get("geometry", ""), "wheel_layers.csv"),
            codex_path=os.path.join(modules.get("geometry", ""), "wheel_codex.csv"),
            drift_path=os.path.join(modules.get("geometry", ""), "polarity_drift.csv"),
            ml_instruction_path=os.path.join(modules.get("engine_boot", ""), "ml_instruction.csv")
        )

        print(f"     ? Geometry Alert: {overlay['geometry_alert']}")
        print(f"     ? Suggested Action: {overlay['suggested_action']}")



