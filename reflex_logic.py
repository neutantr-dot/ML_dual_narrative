from reflex_core import detect_reflex, apply_containment
from classification_engine import classify_actor_from_wheel
from reflex_manifest import get_reflex_manifest
from reflex_taxonomy import symbolic_reflex

# === Reflex Bundle Processor ===
def process_reflex_bundle(actor, wheel_state, voice_input,
                          transmission_map_path, classification_path, taxonomy_path,
                          wheel_domains=None):
    """
    Full reflex logic pipeline:
    - Detect reflex from wheel state and voice input
    - Classify actor identity using symbolic CSV
    - Enrich with symbolic theme and repair path
    - Trigger symbolic pause if containment is required
    - Optionally include wheel domain context
    Returns a stitched bundle of reflex, classification, and narrative enrichment.
    """
    # Detect reflex from transmission map
    reflex = detect_reflex(wheel_state, voice_input, transmission_map_path)

    # Classify actor using CSV-driven symbolic engine
    classification = classify_actor_from_wheel(
        actor=actor,
        wheel_state=wheel_state,
        reflex_type=reflex["reflex_type"],
        classification_path=classification_path
    )

    # Trigger symbolic pause if containment is required
    if classification["containment_required"]:
        reflex["narrative_branch"] = "symbolic_pause"
        reflex["containment_strategy"] += "\n⚠️ Containment required — escalation blocked."

    # Enrich with symbolic theme from taxonomy
    symbolic = symbolic_reflex(
        mismatch_type=reflex["reflex_type"],
        archetype=reflex["archetype_entry"],
        taxonomy_path=taxonomy_path
    )

    # Stitch full bundle
    bundle = {
        "wheel_state": wheel_state,
        "reflex_type": reflex["reflex_type"],
        "archetype_entry": reflex["archetype_entry"],
        "containment_strategy": reflex["containment_strategy"],
        "narrative_branch": reflex["narrative_branch"],
        "somatic_protocol": reflex["somatic_protocol"],
        "class_code": classification["class_code"],
        "archetype_variant": classification["archetype_variant"],
        "containment_required": classification["containment_required"],
        "progressive": classification["progressive"],
        "symbolic_theme": symbolic["symbolic_theme"],
        "emotional_cost": symbolic["emotional_cost"],
        "repair_path": symbolic["repair_path"]
    }

    if wheel_domains:
        bundle["wheel_domains"] = wheel_domains

    return bundle


# === Containment Strategy ===
def get_containment_strategy(wheel_state, voice_input, transmission_map_path, wheel_domains=None):
    """
    Returns the containment strategy for a given wheel state and voice input.
    Adds symbolic warning if wheel_centre indicates wellbeing collapse.
    """
    strategy = apply_containment(wheel_state, voice_input, transmission_map_path)

    if wheel_domains:
        centre = wheel_domains.get("centre", "").lower()
        if centre in ["numb", "exhausted", "collapsed"]:
            strategy += "\n⚠️ Wellbeing collapse detected — recommend pause and emotional reset."

    return strategy


# === Reflex Manifest Preview ===
def preview_available_reflexes(transmission_map_path):
    """
    Returns a manifest of available reflexes grouped by wheel state.
    Useful for UI guidance or actor training.
    """
    return get_reflex_manifest(transmission_map_path)
