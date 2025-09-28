import os
import yaml
import json
import csv
from datetime import datetime
from reflex_logic import process_reflex_bundle, get_containment_strategy

# Optional: Only used if generative AI is enabled
try:
    import openai
except ImportError:
    openai = None

# === Utility Loaders ===
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

# === Wheel State Detection ===
def detect_wheel_state(voice_input, background, wheel_codex_path):
    codex = load_csv(wheel_codex_path)
    for row in codex:
        if row["notes"] in voice_input or row["rupture_trigger"] in background:
            return row["color"]
    return "neutral"

# === Tone Modulation ===
def modulate_tone(wheel_state, grammar):
    if wheel_state in grammar:
        tone = grammar[wheel_state].get("tone", "neutral")
        reframe = grammar[wheel_state].get("reframe", "No reframe available.")
        return f"[Tone: {tone}]\n{reframe}"
    return "[Tone: neutral]\nNo emotional modulation applied."

# === Classification Logging ===
def log_classification(user_id, actor, class_code, log_path):
    timestamp = datetime.now().strftime("%a %b %d %Y (%H:%M)")
    with open(log_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, user_id, actor, class_code])

# === Main Narrative Engine ===
def generate_narrative(actor, user_id, voice_input, background, config):
    use_generative = config["runtime"].get("use_generative_ai", False)
    line_count = config["runtime"].get("story_line_count", 20)

    if use_generative and openai:
        # === Generative AI Path ===
        prompt = (
            f"You are a storytelling assistant.\n\n"
            f"Voice Input:\n{voice_input}\n\n"
            f"Background:\n{background}\n\n"
            f"Generate a dual narrative story in {line_count} lines.\n"
            f"Return the story first, then the classification label on a new line prefixed with 'Classification:'"
        )

        openai.api_key = config.get("openai_api_key", "your-api-key")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a storytelling assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=min(1500, line_count * 50)
            )
            output = response["choices"][0]["message"]["content"]
            lines = output.splitlines()

            if lines and "Classification:" in lines[-1]:
                classification = lines[-1].replace("Classification:", "").strip()
                narrative = "\n".join(lines[:-1])
            else:
                classification = config["defaults"].get("fallback_archetype", "none")
                narrative = "\n".join(lines)

        except Exception as e:
            narrative = f"[Error] Failed to generate story: {e}"
            classification = config["defaults"].get("fallback_archetype", "none")

    else:
        # === Modular Reflex Path ===
        grammar = load_grammar(config["grammar"]["emotional_grammar"])
        modules = config["paths"]["modules"]

        wheel_state = detect_wheel_state(
            voice_input,
            background,
            os.path.join(modules["geometry"], "wheel_codex.csv")
        )

        # Tone modulation
        narrative = modulate_tone(wheel_state, grammar)

        # Reflex bundle
        reflex_bundle = process_reflex_bundle(
            actor=actor,
            wheel_state=wheel_state,
            voice_input=voice_input,
            transmission_map_path=os.path.join(modules["geometry"], "transmission_map.csv"),
            classification_path=os.path.join(modules["reflex"], "classification.csv"),
            taxonomy_path=os.path.join(modules["reflex"], "reflex_taxonomy.csv")
        )

        # Containment strategy
        containment = get_containment_strategy(
            wheel_state,
            voice_input,
            os.path.join(modules["geometry"], "transmission_map.csv")
        )

        # Stitch narrative
        narrative += f"\n\n[Containment Strategy]\n{containment}"

        classification = reflex_bundle["class_code"]

    # === Logging ===
    log_classification(
        user_id=user_id,
        actor=actor,
        class_code=classification,
        log_path=os.path.join(config["paths"]["modules"]["reflex"], "classification.csv")
    )

    return f"[{actor} Narrative]\n{narrative}\n\n[Classification]\nActor: {actor}\nClassification: {classification}"
