import csv
import os
from geometry_resolver import resolve_geometry_state

# === CSV Loader ===
def load_csv(path):
    """
    Loads a CSV file and returns a list of dictionaries.
    """
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"⚠️ Failed to load CSV: {e}")
        return []

# === Actor Classification ===
def classify_actor_from_wheel(actor, actor_wheel_state, reflex_type, classification_path):
    """
    Classifies actor using actor_wheel_state and reflex_type.
    Returns: class_code, archetype_variant, containment_required, progressive
    """
    rows = load_csv(classification_path)

    # Normalize column name for backward compatibility
    for row in rows:
        if "wheel_state" in row:
            row["actor_wheel_state"] = row["wheel_state"]

    for row in rows:
        if (
            row.get("actor", "").strip().upper() == actor.strip().upper() and
            row.get("actor_wheel_state", "").strip().lower() == actor_wheel_state.strip().lower() and
            row.get("reflex_type", "").strip().lower() == reflex_type.strip().lower()
        ):
            return {
                "class_code": row.get("class_code", "N/A").strip(),
                "archetype_variant": row.get("archetype_variant", "unknown").strip(),
                "containment_required": row.get("containment_required", "FALSE").strip().upper() == "TRUE",
                "progressive": row.get("progressive", "FALSE").strip().upper() == "TRUE"
            }

    # Fallback if no match found
    return {
        "class_code": "N/A",
        "archetype_variant": "unknown",
        "containment_required": False,
        "progressive": False
    }

# === Classification Preview ===
def preview_classification(classification_path):
    """
    Prints a readable preview of archetype classification logic.
    Includes optional geometry overlay if wheel domains are present.
    """
    rows = load_csv(classification_path)
    if not rows:
        print("⚠️ No classification data found.")
        return

    for row in rows:
        if "wheel_state" in row:
            row["actor_wheel_state"] = row["wheel_state"]

    print("🧠 Archetype Classification Preview:")
    for row in rows:
        actor = row.get("actor", "N/A")
        reflex = row.get("reflex_type", "N/A")
        wheel = row.get("actor_wheel_state", "N/A")
        code = row.get("class_code", "N/A")
        variant = row.get("archetype_variant", "unknown")
        containment = row.get("containment_required", "FALSE")
        progressive = row.get("progressive", "FALSE")

        print(f"  • {actor} → {reflex} @ {wheel} → {code} ({variant}) | Containment: {containment} | Progressive: {progressive}")

        # Optional: Preview geometry overlay if wheel domains are available
        geometry_overlay = resolve_geometry_state(
            wheel_domains={
                "blue": row.get("blue", wheel),
                "red": row.get("red", wheel),
                "yellow": row.get("yellow", wheel),
                "green": row.get("green", wheel),
                "centre": row.get("centre", wheel)
            },
            layers_path=os.path.join("geometry", "wheel_layers.csv"),
            codex_path=os.path.join("geometry", "wheel_codex.csv"),
            drift_path=os.path.join("geometry", "polarity_drift.csv"),
            ml_instruction_path=os.path.join("engine_boot", "ml_instruction.csv")
        )

        print(f"     ↪ Geometry Alert: {geometry_overlay['geometry_alert']}")
        print(f"     ↪ Suggested Action: {geometry_overlay['suggested_action']}")
