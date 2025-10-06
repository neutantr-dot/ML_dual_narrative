import os
import yaml
import json
import csv
from datetime import datetime
from reflex_logic import process_reflex_bundle, get_containment_strategy
from classification import classify_and_embed
from geometry_resolver import resolve_geometry_state
from dual_narrative_trainer import inject_trainer_stage, inject_recentering_stage

# === Optional: Generative AI ===
try:
    import openai
except ImportError:
    openai = None

# === Loaders ===
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

def load_transmission_profile(path="classification_transmission_map.csv"):
    rows = load_csv(path)
    return {row["code"]: row for row in rows}

# === Wheel State Detection ===
def detect_wheel_state(voice_input, background, wheel_codex_path):
    codex = load_csv(wheel_codex_path)
    for row in codex:
        if row.get("notes", "") in voice_input or row.get("rupture_trigger", "") in background:
            return row.get("color", "neutral")
    return "neutral"

# === Tone Modulation ===
def modulate_tone(wheel_state, grammar, archetype_variant=None, geometry_alert=None):
    tone_prefix = f"[Archetype: {archetype_variant}]" if archetype_variant else ""
    alert_prefix = f"\n[Symbolic Overlay]\nAlert: {geometry_alert}" if geometry_alert and geometry_alert != "stable" else ""
    if wheel_state in grammar:
        tone = grammar[wheel_state].get("tone", "neutral")
        reframe = grammar[wheel_state].get("reframe", "No reframe available.")
        return f"{tone_prefix}\n[Tone: {tone}]{alert_prefix}\n{reframe}"
    return f"{tone_prefix}\n[Tone: neutral]{alert_prefix}\nNo emotional modulation applied."

# === Classification Logging ===
def log_classification(user_id, actor, class_code, log_path):
    timestamp = datetime.now().strftime("%a %b %d %Y (%H:%M)")
    with open(log_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, user_id, actor, class_code])

# === Input Flattening ===
def flatten_inputs(inputs):
    return " ".join([i.strip() for i in inputs if i])

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
        grammar = load_grammar(config["emotional_grammar"]["path"])
        modules = config["paths"]["modules"]

        reflex_wheel_state = detect_wheel_state(
            voice_input,
            background_input,
            os.path.join(modules["geometry"], "wheel_codex.csv")
        )

        actor_wheel_state = inputs[8]

        wheel_domains = {
            "blue": inputs[4],
            "red": inputs[5],
            "yellow": inputs[6],
            "green": inputs[7],
            "centre": inputs[8]
        }

        reflex_bundle = process_reflex_bundle(
            actor=actor,
            actor_wheel_state=actor_wheel_state,
            reflex_wheel_state=reflex_wheel_state,
            voice_input=voice_input,
            transmission_map_path=os.path.join(modules["geometry"], "transmission_map.csv"),
            classification_path=os.path.join(modules["classification"], "archetype_classification.csv"),
            taxonomy_path=os.path.join(modules["reflex"], "7_reflex_taxonomy.csv"),
            wheel_domains=wheel_domains,
            wheel_layers_path=os.path.join(modules["geometry"], "wheel_layers.csv"),
            polarity_drift_path=os.path.join(modules["geometry"], "polarity_drift.csv")
        )

        geometry_overlay = resolve_geometry_state(
            wheel_domains=wheel_domains,
            layers_path=os.path.join(modules["geometry"], "wheel_layers.csv"),
            codex_path=os.path.join(modules["geometry"], "wheel_codex.csv"),
            drift_path=os.path.join(modules["geometry"], "polarity_drift.csv"),
            ml_instruction_path=os.path.join(modules["engine_boot"], "ml_instruction.csv")
        )

        reflex_bundle.update(geometry_overlay)

        classification_data = classify_and_embed(
            actor=actor,
            actor_wheel_state=actor_wheel_state,
            reflex_type=reflex_bundle["reflex_type"]
        )

        classification = classification_data.get("class_code", config.get("defaults", {}).get("fallback_archetype", "none"))
        variant = classification_data.get("archetype_variant", "unknown")
        geometry_alert = reflex_bundle.get("geometry_alert", None)
        containment_strategy = reflex_bundle.get("containment_strategy", "default silence")
        reflex_type = reflex_bundle.get("reflex_type", "neutral")

        trainer_stage_id, trainer_stage_name = inject_trainer_stage(actor, wheel_domains, reflex_type, containment_strategy)
        recentre_stage_id, recentre_stage_name = inject_recentering_stage(actor, wheel_domains)

        transmission_map = load_transmission_profile()
        transmission = transmission_map.get(classification, {})

        narrative = modulate_tone(reflex_wheel_state, grammar, archetype_variant=variant, geometry_alert=geometry_alert)

        narrative += (
            f"\n\n[Transmission Profile]"
            f"\nDirection: {transmission.get('direction', 'unspecified')}"
            f"\nMode: {transmission.get('mode', 'unspecified')}"
            f"\nDescription: {transmission.get('description', 'unspecified')}"
        )

        containment = get_containment_strategy(
            reflex_wheel_state,
            voice_input,
            os.path.join(modules["geometry"], "transmission_map.csv"),
            wheel_domains=wheel_domains
        )

        narrative += f"\n\n[Containment Strategy]\n{containment}"

        if transmission.get("mode") == "tantra spectacle":
            narrative += "\n\n[Suggested Action]\nNo action suggested — spectacle path not supported."
        elif "suggested_action" in reflex_bundle:
            narrative += f"\n\n[Suggested Action]\n{reflex_bundle['suggested_action']}"

    return narrative


