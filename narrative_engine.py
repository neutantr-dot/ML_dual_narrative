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
        if row.get("notes", "") in voice_input or row.get("rupture_trigger", "") in background:
            return row.get("color", "neutral")
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

# === Input Flattening ===
def flatten_inputs(inputs):
    return " ".join([i.strip() for i in inputs if i])

# === Default Classifier ===
def classify_user(inputs, actor):
    # Future: Add symbolic triggers for M2/M3 and F2/F3
    return "F1" if actor.upper() == "F" else "M1"

# === Narrative Construction ===
def build_story(inputs, classification):
    input1, input2, input3, input4 = inputs[:4]
    wheel_inputs = inputs[4:]

    return f"""
🧍 What you said: "{input1}"
💭 What you thought: "{input2}"
🧑‍🤝‍🧑 What your partner said: "{input3}"
📍 Context: "{input4}"

🌀 Emotional Background:
- Blue (action): {wheel_inputs[0]}
- Red (control): {wheel_inputs[1]}
- Green (emotion): {wheel_inputs[2]}
- Yellow (expression): {wheel_inputs[3]}
- Centre (wellbeing): {wheel_inputs[4]}

🔍 Classification: {classification}
""".strip()

# === Main Narrative Engine ===
def generate_narrative(inputs, actor, user_id, background="", config={}):
    if len(inputs) != 9:
        return "❌ Error: Expected 9 inputs."

    use_generative = config.get("runtime", {}).get("use_generative_ai", False)
    line_count = config.get("runtime", {}).get("story_line_count", 20)
    voice_input = flatten_inputs(inputs[:4])
    background_input = flatten_inputs(inputs[4:])

    if use_generative and openai:
        # === Generative AI Path ===
        prompt = (
            f"You are a storytelling assistant.\n\n"
            f"Voice Input:\n{voice_input}\n\n"
            f"Background:\n{background_input}\n\n"
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
                classification = config.get("defaults", {}).get("fallback_archetype", "none")
                narrative = "\n".join(lines)

        except Exception as e:
            narrative = f"[Error] Failed to generate story: {e}"
            classification = config.get("defaults", {}).get("fallback_archetype", "none")

    else:
        # === Modular Reflex Path ===
        grammar = load_grammar(config["grammar"]["emotional_grammar"])
        modules = config["paths"]["modules"]

        wheel_state = detect_wheel_state(
            voice_input,
            background_input,
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
            classification_path="classification.csv",
            taxonomy_path=os.path.join(modules["reflex"], "7_reflex_taxonomy.csv")
        )

        # Containment strategy
        containment = get_containment_strategy(
            wheel_state,
            voice_input,
            os.path.join(modules["geometry"], "transmission_map.csv")
        )

        # Stitch narrative
        narrative += f"\n\n[Containment Strategy]\n{containment}"

        classification = reflex_bundle.get("class_code", config.get("defaults", {}).get("fallback_archetype", "none"))

    # === Logging ===
    log_classification(
        user_id=user_id,
        actor=actor,
        class_code=classification,
        log_path="classification.csv"
    )

    # === Final Output ===
    story_block = build_story(inputs, classification)
    return f"[{actor} Narrative]\n{story_block}\n\n{narrative}\n\n[Classification]\nActor: {actor}\nClassification: {classification}"
