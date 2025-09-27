import os
import yaml
import json
import csv
from reflex_logic import detect_reflex, apply_containment

# Load YAML config
def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Load emotional grammar
def load_grammar(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load CSV as list of dicts
def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

# Read input text
def read_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

# Write output text
def write_text(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Detect wheel state from input using wheel_codex.csv
def detect_wheel_state(voice_input, background, wheel_codex_path):
    codex = load_csv(wheel_codex_path)
    for row in codex:
        if row["notes"] in voice_input or row["rupture_trigger"] in background:
            return row["color"]
    return "neutral"

# Modulate tone using emotional grammar
def modulate_tone(wheel_state, grammar):
    if wheel_state in grammar:
        tone = grammar[wheel_state]["tone"]
        reframe = grammar[wheel_state]["reframe"]
        return f"[Tone: {tone}]\n{reframe}"
    return "[Tone: neutral]\nNo emotional modulation applied."

# Main engine orchestration
def run_engine():
    config = load_config("copilot_config.yaml")
    grammar = load_grammar("emotional_grammar.json")

    # Paths
    input_path = config["paths"]["input"]
    output_path = config["paths"]["output"]
    modules = config["paths"]["modules"]

    # Read input
    voice_input = read_text(os.path.join(input_path, "voice_input.txt"))
    background = read_text(os.path.join(input_path, "background.txt"))

    # Detect wheel state
    wheel_state = detect_wheel_state(
        voice_input,
        background,
        os.path.join(modules["geometry"], "wheel_codex.csv")
    )

    # Modulate tone
    narrative = modulate_tone(wheel_state, grammar)

    # Apply reflex logic and containment
    narrative = apply_containment(
        wheel_state,
        narrative,
        os.path.join(modules["reflex"], "6_reflex_logic.csv"),
        os.path.join(modules["geometry"], "transmission_map.csv"),
        os.path.join(modules["geometry"], "containment_protocol.csv"),
        os.path.join(modules["geometry"], "somatic_protocol.csv")
    )

    # Write output
    write_text(output_path, narrative)
    print(f"Narrative generated for wheel state: {wheel_state}")

# Entry point
if __name__ == "__main__":
    run_engine()
