import csv

def load_csv(path):
    """Loads a CSV file and returns a list of dictionaries."""
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def detect_reflex(wheel_state, voice_input, transmission_map_path):
    """
    Detects reflex based on wheel state and voice input.
    Returns a semantic bundle: reflex_type, archetype_entry, containment_strategy, narrative_branch, somatic_protocol.
    """
    try:
        transmission_map = load_csv(transmission_map_path)
        voice_text = " ".join(voice_input).lower()

        for row in transmission_map:
            if all(key in row for key in [
                "wheel_state", "reflex_type", "archetype_entry",
                "containment_strategy", "narrative_branch", "somatic_protocol"
            ]):
                if row["wheel_state"].strip().lower() == wheel_state.strip().lower() and \
                   row["reflex_type"].strip().lower() in voice_text:
                    return {
                        "reflex_type": row["reflex_type"],
                        "archetype_entry": row["archetype_entry"],
                        "containment_strategy": row["containment_strategy"],
                        "narrative_branch": row["narrative_branch"],
                        "somatic_protocol": row["somatic_protocol"]
                    }
    except Exception as e:
        print(f"⚠️ Reflex detection failed: {e}")

    return default_reflex_bundle()

def apply_containment(wheel_state, voice_input, transmission_map_path):
    """
    Applies containment strategy based on detected reflex.
    Returns the containment strategy string.
    """
    reflex = detect_reflex(wheel_state, voice_input, transmission_map_path)
    return reflex.get("containment_strategy", "default silence")

def classify_actor(actor, wheel_state, reflex_type, archetype_entry, classification_path):
    """
    Classifies actor identity based on emotional context.
    Returns a class code (e.g. M1, F2, etc.).
    """
    try:
        classification_data = load_csv(classification_path)
        for row in classification_data:
            if all(key in row for key in [
                "actor", "wheel_state", "reflex_type", "archetype_entry", "class_code"
            ]):
                if (
                    row["actor"].strip().lower() == actor.strip().lower() and
                    row["wheel_state"].strip().lower() == wheel_state.strip().lower() and
                    row["reflex_type"].strip().lower() == reflex_type.strip().lower() and
                    row["archetype_entry"].strip().lower() == archetype_entry.strip().lower()
                ):
                    return row["class_code"]
    except Exception as e:
        print(f"⚠️ Actor classification failed: {e}")

    return "M0"  # fallback classification

def default_reflex_bundle():
    """Returns fallback reflex bundle when no match is found."""
    return {
        "reflex_type": "none",
        "archetype_entry": "none",
        "containment_strategy": "default silence",
        "narrative_branch": "neutral",
        "somatic_protocol": "breath_and_stillness"
    }