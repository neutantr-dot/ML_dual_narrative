import csv
import json

# Load CSV as list of dicts
def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# Load emotional grammar JSON
def load_grammar(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

# Detect reflex from wheel state and voice input
def detect_reflex(wheel_state, voice_input, reflex_logic_path):
    reflex_logic = load_csv(reflex_logic_path)
    for row in reflex_logic:
        if row["wheel_state"] == wheel_state and row["trigger"] in voice_input:
            return {
                "reflex_type": row["reflex_type"],
                "archetype_entry": row["archetype_entry"],
                "containment_strategy": row["intervention"]
            }
    return {
        "reflex_type": "none",
        "archetype_entry": "none",
        "containment_strategy": "default silence"
    }

# Get transmission axis and narrative branch
def get_transmission_map(wheel_state, transmission_map_path):
    transmission_map = load_csv(transmission_map_path)
    for row in transmission_map:
        if row["wheel_state"] == wheel_state:
            return {
                "transmission_axis": row["transmission_axis"],
                "narrative_branch": row["narrative_branch"],
                "somatic_protocol": row["somatic_protocol"]
            }
    return {
        "transmission_axis": "unknown",
        "narrative_branch": "default",
        "somatic_protocol": "pause and breathe"
    }

# Apply containment strategy and somatic protocol
def apply_containment(wheel_state, narrative, reflex_logic_path, transmission_map_path, containment_protocol_path, somatic_protocol_path):
    reflex = detect_reflex(wheel_state, narrative, reflex_logic_path)
    transmission = get_transmission_map(wheel_state, transmission_map_path)
    containment_protocol = load_csv(containment_protocol_path)
    somatic_protocol = load_csv(somatic_protocol_path)

    # Find containment text
    containment_text = next(
        (row["strategy"] for row in containment_protocol if row["archetype"] == reflex["archetype_entry"]),
        "Hold silence, no fixing"
    )

    # Find somatic cue
    somatic_text = next(
        (row["protocol"] for row in somatic_protocol if row["cue"] == transmission["somatic_protocol"]),
        "Breathe and soften spine"
    )

    # Compose updated narrative
    updated_narrative = f"{narrative}\n\n[Reflex Triggered: {reflex['reflex_type']} → {reflex['archetype_entry']}]\nContainment: {containment_text}\nSomatic Cue: {somatic_text}\nNarrative Branch: {transmission['narrative_branch']}"
    return updated_narrative
