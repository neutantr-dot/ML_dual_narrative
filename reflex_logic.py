from reflex_core import detect_reflex, apply_containment, classify_actor
from reflex_manifest import get_reflex_manifest
from reflex_taxonomy import symbolic_reflex

def process_reflex_bundle(actor, wheel_state, voice_input,
                          transmission_map_path, classification_path, taxonomy_path):
    """
    Full reflex logic pipeline:
    - Detect reflex from wheel state and voice input
    - Classify actor identity
    - Enrich with symbolic theme and repair path
    Returns a stitched bundle of reflex, classification, and narrative enrichment.
    """
    # Detect reflex from transmission map
    reflex = detect_reflex(wheel_state, voice_input, transmission_map_path)

    # Classify actor based on emotional context
    class_code = classify_actor(
        actor=actor,
        wheel_state=wheel_state,
        reflex_type=reflex["reflex_type"],
        archetype_entry=reflex["archetype_entry"],
        classification_path=classification_path
    )

    # Enrich with symbolic theme from taxonomy
    symbolic = symbolic_reflex(
        mismatch_type=reflex["reflex_type"],
        archetype=reflex["archetype_entry"],
        taxonomy_path=taxonomy_path
    )

    # Stitch full bundle
    return {
        "wheel_state": wheel_state,
        "reflex_type": reflex["reflex_type"],
        "archetype_entry": reflex["archetype_entry"],
        "containment_strategy": reflex["containment_strategy"],
        "narrative_branch": reflex["narrative_branch"],
        "somatic_protocol": reflex["somatic_protocol"],
        "class_code": class_code,
        "symbolic_theme": symbolic["symbolic_theme"],
        "emotional_cost": symbolic["emotional_cost"],
        "repair_path": symbolic["repair_path"]
    }

def preview_available_reflexes(transmission_map_path):
    """
    Returns a manifest of available reflexes grouped by wheel state.
    Useful for UI guidance or actor training.
    """
    return get_reflex_manifest(transmission_map_path)

def get_containment_strategy(wheel_state, voice_input, transmission_map_path):
    """
    Returns the containment strategy for a given wheel state and voice input.
    """
    return apply_containment(wheel_state, voice_input, transmission_map_path)
