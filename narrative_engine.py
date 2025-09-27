import os
import yaml
import json
import csv
from reflex_logic import detect_reflex, apply_containment, classify_actor
from datetime import datetime

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_grammar(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def read_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def write_text(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def detect_wheel_state(voice_input, background, wheel_codex_path):
    codex = load_csv(wheel_codex_path)
    for row in codex:
        if row["notes"] in voice_input or row["rupture_trigger"] in background:
            return row["color"]
    return "neutral"

def modulate_tone(wheel_state, grammar):
    if wheel_state in grammar:
        tone = grammar[wheel_state]["tone"]
        reframe = grammar[wheel_state]["reframe"]
        return f"[Tone: {tone}]\n{reframe}"
    return "[Tone: neutral]\nNo emotional modulation applied."

def log_classification(user_id, actor, class_code, log_path):
    timestamp = datetime.now().strftime("%a %b %d %Y (%H:%M)")
    with open(log_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, user_id, actor, class_code])

def generate_narrative(actor, user_id, voice_input, background, config):
    grammar = load_grammar(config["grammar"]["emotional_grammar"])
    modules = config["paths"]["modules"]

    wheel_state = detect_wheel_state(
        voice_input,
        background,
        os.path.join(modules["geometry"], "wheel_codex.csv")
    )

    narrative = modulate_tone(wheel_state, grammar)

    narrative = apply_containment(
        wheel_state,
        narrative,
        os.path.join(modules["reflex"], "6_reflex_logic.csv"),
        os.path.join(modules["geometry"], "transmission_map.csv"),
        os.path.join(modules["geometry"], "containment_protocol.csv"),
        os.path.join(modules["geometry"], "somatic_protocol.csv")
    )

    reflex = detect_reflex(
        wheel_state,
        voice_input,
        os.path.join(modules["reflex"], "6_reflex_logic.csv")
    )

    class_code = classify_actor(
        actor,
        wheel_state,
        reflex["reflex_type"],
        reflex["archetype_entry"],
        os.path.join(modules["reflex"], "classification.csv")
    )

    log_classification(
        user_id=user_id,
        actor=actor,
        class_code=class_code,
        log_path=os.path.join(modules["reflex"], "classification.csv")
    )

    return f"[{actor} Narrative]\n{narrative}\n\n[Classification]\nActor: {actor}\nClassification: {class_code}"
