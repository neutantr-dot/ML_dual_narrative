import csv

# === CSV Loader ===
def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# === Reflex Detection ===
def detect_reflex(wheel_state, voice_input, transmission_map_path):
    """
    Detects symbolic reflex from transmission map.
    Returns reflex_type, archetype_entry, containment_strategy, narrative_branch, somatic_protocol.
    """
    transmission_map = load_csv(transmission_map_path)
    for row in transmission_map:
        if row.get("trigger") in voice_input and row.get("wheel_state") == wheel_state:
            return {
                "reflex_type": row.get("reflex_type", "neutral"),
                "archetype_entry": row.get("archetype_entry", "M1"),
                "containment_strategy": row.get("containment", "No containment strategy found."),
                "narrative_branch": row.get("narrative_branch", "default"),
                "somatic_protocol": row.get("somatic_protocol", "none")
            }
    return {
        "reflex_type": "neutral",
        "archetype_entry": "M1",
        "containment_strategy": "No containment strategy found.",
        "narrative_branch": "default",
        "somatic_protocol": "none"
    }

# === Containment Strategy ===
def apply_containment(wheel_state, voice_input, transmission_map_path):
    """
    Returns symbolic containment strategy based on wheel state and voice input.
    """
    transmission_map = load_csv(transmission_map_path)
    for row in transmission_map:
        if row.get("trigger") in voice_input and row.get("wheel_state") == wheel_state:
            return row.get("containment", "No containment strategy found.")
    return "No containment strategy found."

# === Actor Classification ===
from classification_engine import classify_actor_from_wheel

# === Actor Classification ===
def classify_actor(actor, wheel_state, reflex_type, classification_path):
    """
    Uses CSV-driven classification engine to return symbolic bundle.
    """
    return classify_actor_from_wheel(actor, wheel_state, reflex_type, classification_path)

def default_reflex_bundle():
    """Returns fallback reflex bundle when no match is found."""
    return {
        "reflex_type": "none",
        "archetype_entry": "none",
        "containment_strategy": "default silence",
        "narrative_branch": "neutral",
        "somatic_protocol": "breath_and_stillness"
    }



