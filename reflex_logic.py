from reflex_core import detect_reflex, apply_containment
from classification_engine import classify_actor_from_wheel
from reflex_manifest import get_reflex_manifest
from reflex_taxonomy import symbolic_reflex
import os
import csv

# === CSV Loader ===
def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# === Symbolic Geometry Enrichment ===
def enrich_with_geometry(wheel_domains, wheel_layers_path, polarity_drift_path):
    wheel_layers = load_csv(wheel_layers_path)
    polarity_drift = load_csv(polarity_drift_path)

    centre = wheel_domains.get("centre", "").lower()
    red = wheel_domains.get("red", "").lower()

    if centre in ["numb", "collapsed", "exhausted"]:
        return {
            "geometry_alert": "wellbeing collapse",
            "suggested_action": "pause and reset"
        }

    if red in ["dominant", "rigid"]:
        return {
            "geometry_alert": "control tension",
            "suggested_action": "soften stance"
        }

    return {
        "geometry_alert": "stable",
        "suggested_action": "continue"
    }

# === Reflex Bundle Processor ===
def process_reflex_bundle(actor, wheel_state, voice_input,
                          transmission_map_path, classification_path, taxonomy_path,
                          wheel_domains=None,
                          wheel_layers_path=None,
                          polarity_drift_path=None):
    """
    Full reflex logic pipeline:
    - Detect reflex from wheel state and voice input
    - Classify actor identity using symbolic CSV
    - Enrich with symbolic theme and repair path
    - Trigger symbolic pause if containment is required
    - Optionally enrich with wheel geometry overlays
    Returns a stitched bundle of reflex, classification, and narrative enrichment.
    """
    reflex = detect_reflex(wheel_state, voice_input, transmission_map_path)

    classification = classify_actor_from_wheel(
        actor=actor,
        wheel_state=wheel_state,
        reflex_type=reflex["reflex_type"],
        classification_path=classification_path
    )

    if classification["containment_required"]:
        reflex["narrative_branch"] = "symbolic_pause"
        reflex["containment_strategy"] += "\n⚠️ Containment required — escalation blocked."

    symbolic = symbolic_reflex(
        mismatch_type=reflex["reflex_type"],
        archetype=reflex["archetype_entry"],
        taxonomy_path=taxonomy_path
    )

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

        if wheel_layers_path and polarity_drift_path:
            geometry_overlay = enrich_with_geometry(
                wheel_domains,
                wheel_layers_path,
                polarity_drift_path
            )
            bundle.update(geometry_overlay)

    return bundle

# === Containment Strategy ===
def get_containment_strategy(wheel_state, voice_input, transmission_map_path, wheel_domains=None):
    strategy = apply_containment(wheel_state, voice_input, transmission_map_path)

    if wheel_domains:
        centre = wheel_domains.get("centre", "").lower()
        if centre in ["numb", "exhausted", "collapsed"]:
            strategy += "\n⚠️ Wellbeing collapse detected — recommend pause and emotional reset."

    return strategy

# === Reflex Manifest Preview ===
def preview_available_reflexes(transmission_map_path):
    return get_reflex_manifest(transmission_map_path)
