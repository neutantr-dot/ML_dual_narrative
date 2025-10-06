import csv
import os
from classification_engine import classify_actor_from_wheel
from geometry_resolver import resolve_geometry_state

# === CSV Loader ===
def load_csv(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"⚠️ Failed to load CSV: {e}")
        return []

# === Reflex Detection ===
def detect_reflex(reflex_wheel_state, voice_input, transmission_map_path):
    transmission_map = load_csv(transmission_map_path)
    for row in transmission_map:
        reflex_state = row.get("reflex_wheel_state", "").strip().lower()
        trigger = row.get("trigger", "").strip().lower()
        if trigger and trigger in voice_input.lower() and reflex_state == reflex_wheel_state.strip().lower():
            return {
                "reflex_type": row.get("reflex_type", "neutral"),
                "archetype_entry": row.get("archetype_entry", "M1"),
                "containment_strategy": row.get("containment_strategy", "No containment strategy found."),
                "narrative_branch": row.get("narrative_branch", "default"),
                "somatic_protocol": row.get("somatic_protocol", "none")
            }

    # Debug trace for unmatched reflex
    print(f"⚠️ No reflex match for reflex_wheel_state='{reflex_wheel_state}' and input='{voice_input}'")

    return {
        "reflex_type": "neutral",
        "archetype_entry": "M1",
        "containment_strategy": "No containment strategy found.",
        "narrative_branch": "default",
        "somatic_protocol": "none"
    }

# === Containment Strategy ===
def apply_containment(reflex_wheel_state, voice_input, transmission_map_path):
    transmission_map = load_csv(transmission_map_path)
    for row in transmission_map:
        reflex_state = row.get("reflex_wheel_state", "").strip().lower()
        trigger = row.get("trigger", "").strip().lower()
        if trigger and trigger in voice_input.lower() and reflex_state == reflex_wheel_state.strip().lower():
            return row.get("containment_strategy", "No containment strategy found.")
    return "No containment strategy found."

# === Actor Classification ===
def classify_actor(actor, actor_wheel_state, reflex_type, classification_path):
    return classify_actor_from_wheel(actor, actor_wheel_state, reflex_type, classification_path)

# === Reflex Bundle Constructor ===
def process_reflex_bundle(actor, actor_wheel_state, reflex_wheel_state, voice_input,
                          transmission_map_path, classification_path, taxonomy_path,
                          wheel_domains, wheel_layers_path, polarity_drift_path):
    reflex = detect_reflex(reflex_wheel_state, voice_input, transmission_map_path)
    classification = classify_actor(actor, actor_wheel_state, reflex["reflex_type"], classification_path)

    geometry_overlay = resolve_geometry_state(
        wheel_domains=wheel_domains,
        layers_path=wheel_layers_path,
        codex_path=os.path.join(os.path.dirname(wheel_layers_path), "wheel_codex.csv"),
        drift_path=polarity_drift_path,
        ml_instruction_path=os.path.join("engine_boot", "ml_instruction.csv")
    )

    bundle = {
        "actor_wheel_state": actor_wheel_state,
        "reflex_wheel_state": reflex_wheel_state,
        "reflex_type": reflex["reflex_type"],
        "archetype_entry": reflex["archetype_entry"],
        "containment_strategy": reflex["containment_strategy"],
        "narrative_branch": reflex["narrative_branch"],
        "somatic_protocol": reflex["somatic_protocol"],
        "wheel_domains": wheel_domains,
        "class_code": classification.get("class_code", "N/A"),
        "archetype_variant": classification.get("archetype_variant", "unknown"),
        "containment_required": classification.get("containment_required", False),
        "progressive": classification.get("progressive", False)
    }

    bundle.update(geometry_overlay)
    return bundle

# === Fallback Reflex Bundle ===
def default_reflex_bundle():
    return {
        "reflex_type": "none",
        "archetype_entry": "none",
        "containment_strategy": "default silence",
        "narrative_branch": "neutral",
        "somatic_protocol": "breath_and_stillness"
    }








