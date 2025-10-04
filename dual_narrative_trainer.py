import os
from geometry_resolver import resolve_geometry_state

# === Trainer Injection Logic ===
def inject_trainer_stage(actor, wheel_domains, reflex_type, containment_strategy):
    """
    Determines if M3/F3 trainer stage should be injected based on symbolic collapse or blocked containment.
    Returns: stage_id, stage_name
    """
    overlay = resolve_geometry_state(
        wheel_domains=wheel_domains,
        layers_path=os.path.join("geometry", "wheel_layers.csv"),
        codex_path=os.path.join("geometry", "wheel_codex.csv"),
        drift_path=os.path.join("geometry", "polarity_drift.csv"),
        ml_instruction_path=os.path.join("engine_boot", "ml_instruction.csv")
    )

    geometry_alert = overlay.get("geometry_alert", "stable")
    suggested_action = overlay.get("suggested_action", "continue")

    if actor == "Male":
        if geometry_alert != "stable" or reflex_type == "transactional":
            return "7a", "Stranger Teaches We"
    elif actor == "Female":
        if containment_strategy == "default silence" or geometry_alert != "stable":
            return "7b", "Wisdom Mirrors Self"

    return None, None

# === Re-Centering Arc Logic ===
def inject_recentering_stage(actor, wheel_domains):
    """
    Determines if re-centering arc should be injected based on wheel collapse.
    Returns: stage_id, stage_name
    """
    centre = wheel_domains.get("centre", "").lower()
    if actor == "Male" and centre in ["collapsed", "blocked", "empty"]:
        return "8a", "Male Re-Centres"
    if actor == "Female" and centre in ["collapsed", "blocked", "empty"]:
        return "8b", "Female Re-Centres"
    return None, None
