import csv
import os

# === CSV Loader ===
def load_csv(path):
    try:
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except Exception as e:
        print(f"⚠️ Failed to load CSV: {e}")
        return []

# === Geometry Resolver ===
def resolve_geometry_state(wheel_domains, layers_path, codex_path, drift_path, ml_instruction_path):
    constraint_path = os.path.join("emotional_geometry_layers", "emotional_constraint_matrix.csv")

    layers = load_csv(layers_path)
    codex = load_csv(codex_path)
    drift = load_csv(drift_path)
    constraints = load_csv(constraint_path)
    ml_rules = load_csv(ml_instruction_path)

    overlay = {
        "geometry_alert": "stable",
        "suggested_action": "continue",
        "layer_conflict": [],
        "tension_axis": [],
        "collapsed_roles": [],
        "perception_mismatch": [],
        "ml_flags": [],
        "constraint_matrix_hits": []
    }

    # === Layer-based conflict detection
    for row in layers:
        if row["color"].lower() in wheel_domains.values():
            if row.get("actor_impact"):
                overlay["layer_conflict"].append(row["actor_impact"])
            if row.get("tension_axis"):
                overlay["tension_axis"].append(row["tension_axis"])

    # === Codex-based collapse and mismatch
    for row in codex:
        if row.get("containment_gate", "").lower() == "blocked":
            overlay["collapsed_roles"].append(row.get("actor_role"))
        if row.get("perceived_by_partner", "").lower() == "no":
            overlay["perception_mismatch"].append(row.get("notes"))

    # === Drift detection
    for row in drift:
        if row.get("color") in wheel_domains.values():
            overlay["tension_axis"].append(row.get("drift_axis"))

    # === Constraint matrix hits
    for row in constraints:
        axis = row.get("color_axis", "")
        if axis:
            c1, c2 = axis.split("-")
            if c1 in wheel_domains.values() or c2 in wheel_domains.values():
                overlay["constraint_matrix_hits"].append(row["description"])
                overlay["geometry_alert"] = row["description"]
                overlay["suggested_action"] = row["modulation_gate"]

    # === ML instruction triggers
    for rule in ml_rules:
        if rule.get("trigger_color") in wheel_domains.values():
            overlay["ml_flags"].append(rule.get("symbolic_flag"))
            if rule.get("suggested_action"):
                overlay["suggested_action"] = rule["suggested_action"]
            if rule.get("geometry_alert"):
                overlay["geometry_alert"] = rule["geometry_alert"]

    return overlay
