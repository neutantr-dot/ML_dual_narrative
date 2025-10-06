from reflex_core import detect_reflex, apply_containment
from classification_engine import classify_actor_from_wheel
from reflex_manifest import get_reflex_manifest
from reflex_taxonomy import symbolic_reflex
import os
import csv
import datetime
import uuid

# === Logging Hook ===
def log_event(message, log_path="copilot_log.txt"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - INFO - {message}\n")

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
def process_reflex_bundle(actor, actor_wheel_state, reflex_wheel_state, voice_input,
                          transmission_map_path, classification_path, taxonomy_path,
                          wheel_domains=None,
                          wheel_layers_path=None,
                          polarity_drift_path=None,
                          session_log_path="classification_copilot_0210.csv"):
    reflex = detect_reflex(reflex_wheel_state, voice_input, transmission_map_path)

    classification = classify_actor_from_wheel(
        actor,
        actor_wheel_state,
        reflex["reflex_type"],
        classification_path
    ) or {
        "class_code": "N/A",
        "archetype_variant": "Unknown",
        "containment_required": False,
        "progressive": False
    }

    if classification["containment_required"]:
        reflex["narrative_branch"] = "symbolic_pause"
        reflex["containment_strategy"] += "\n⚠️ Containment required — escalation blocked."

    symbolic = symbolic_reflex(
        mismatch_type=reflex["reflex_type"],
        archetype=reflex["archetype_entry"],
        taxonomy_path=taxonomy_path
    ) or {
        "symbolic_theme": "Unmapped",
        "emotional_cost": "Unknown",
        "repair_path": "Default containment"
    }

    bundle = {
        "actor_wheel_state": actor_wheel_state,
        "reflex_wheel_state": reflex_wheel_state,
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

    # === Geometry Overlay ===
    if wheel_domains:
        bundle["wheel_domains"] = wheel_domains
        if wheel_layers_path and polarity_drift_path:
            geometry_overlay = enrich_with_geometry(
                wheel_domains,
                wheel_layers_path,
                polarity_drift_path
            )
            bundle.update(geometry_overlay)

    # === Session Logging ===
    timestamp = datetime.datetime.now().strftime("%a %b %d, %Y (%H:%M)")
    session_id = str(uuid.uuid4())[:8]

    with open(session_log_path, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow([
                "timestamp", "session_id", "actor", "actor_wheel_state", "reflex_wheel_state",
                "reflex_type", "class_code", "archetype_variant",
                "containment_required", "progressive"
            ])
        writer.writerow([
            timestamp, session_id, actor, actor_wheel_state, reflex_wheel_state,
            reflex["reflex_type"], classification["class_code"],
            classification["archetype_variant"],
            classification["containment_required"],
            classification["progressive"]
        ])

    log_event(f"Reflex bundle generated for actor: {actor}, classification: {classification['class_code']}")

    return bundle

# === Containment Strategy ===
def get_containment_strategy(reflex_wheel_state, voice_input, transmission_map_path, wheel_domains=None):
    strategy = apply_containment(reflex_wheel_state, voice_input, transmission_map_path)

    if wheel_domains:
        centre = wheel_domains.get("centre", "").lower()
        if centre in ["numb", "exhausted", "collapsed"]:
            strategy += "\n⚠️ Wellbeing collapse detected — recommend pause and emotional reset."

    return strategy

# === Reflex Manifest Preview ===
def preview_available_reflexes(transmission_map_path):
    return get_reflex_manifest(transmission_map_path)

