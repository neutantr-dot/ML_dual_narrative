import csv

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


def classify_actor_from_wheel(actor, wheel_state, reflex_type, classification_path):
    """
    Classifies actor using wheel_state and reflex_type.
    Returns: class_code, archetype_variant, containment_required, progressive
    """
    rows = load_csv(classification_path)
    for row in rows:
        if (
            row.get("actor", "").strip().upper() == actor.strip().upper() and
            row.get("wheel_state", "").strip().lower() == wheel_state.strip().lower() and
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
        "class_code": "0",
        "archetype_variant": "unmapped",
        "containment_required": False,
        "progressive": False
    }

def preview_classification(classification_path):
    """
    Prints a readable preview of archetype classification logic.
    """
    rows = load_csv(classification_path)
    if not rows:
        print("⚠️ No classification data found.")
        return

    print("🧠 Archetype Classification Preview:")
    for row in rows:
        actor = row.get("actor", "N/A")
        reflex = row.get("reflex_type", "N/A")
        wheel = row.get("wheel_state", "N/A")
        code = row.get("class_code", "N/A")
        variant = row.get("archetype_variant", "unknown")
        containment = row.get("containment_required", "FALSE")
        progressive = row.get("progressive", "FALSE")
        print(f"  • {actor} → {reflex} @ {wheel} → {code} ({variant}) | Containment: {containment} | Progressive: {progressive}")

