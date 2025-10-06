import datetime
import csv
import json
from classification_engine import classify_actor_from_wheel

# === Configuration ===
MODEL_CONFIG = {
    "name": "openai-gpt4",
    "temperature": 0.7,
    "max_tokens": 800,
    "system_prompt": "You are a storytelling assistant."
}

CLASSIFICATION_CONFIG = {
    "enabled": True,
    "output_file": "classification.csv",
    "fallback_label": "N/A",
    "user_tracking": True,
    "session_label_format": "%a %b %d, %Y (%H:%M)",
    "label_prefix": "Generated on",
    "classification_path": "classification/archetype_classification.csv"
}

STORYLINE_CONFIG = {
    "lines": 20,
    "format": "dual narrative",
    "include_classification": True,
    "classification_labels": ["F0", "F1", "F2", "F3", "M0", "M1", "M2", "M3", "N/A"]
}

LOGGING_CONFIG = {
    "enabled": True,
    "log_file": "copilot_log.txt",
    "log_level": "info",
    "anonymize": True
}

# === Session Label Generator ===
def generate_session_label():
    now = datetime.datetime.now()
    return now.strftime(CLASSIFICATION_CONFIG["session_label_format"])

# === Classification Output Writer ===
def write_classification_output(actor, actor_wheel_state, reflex_type, result):
    if not CLASSIFICATION_CONFIG["enabled"]:
        return

    timestamp = generate_session_label()
    label = f"{CLASSIFICATION_CONFIG['label_prefix']} {timestamp}"
    row = [
        label,
        actor,
        actor_wheel_state,
        reflex_type,
        result["class_code"],
        result["archetype_variant"],
        "TRUE" if result["containment_required"] else "FALSE",
        "TRUE" if result["progressive"] else "FALSE"
    ]

    try:
        with open(CLASSIFICATION_CONFIG["output_file"], "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    except Exception as e:
        print(f"⚠️ Failed to write classification output: {e}")

# === Classification Wrapper ===
def classify_and_embed(actor, actor_wheel_state, reflex_type):
    result = classify_actor_from_wheel(
        actor,
        actor_wheel_state,
        reflex_type,
        CLASSIFICATION_CONFIG["classification_path"]
    )

    if STORYLINE_CONFIG["include_classification"]:
        embed = {
            "class_code": result["class_code"],
            "archetype_variant": result["archetype_variant"],
            "containment_required": result["containment_required"],
            "progressive": result["progressive"]
        }
    else:
        embed = {}

    write_classification_output(actor, actor_wheel_state, reflex_type, result)
    return embed

# === Story Generator ===
def generate_story(actor, actor_wheel_state, reflex_type, input_text):
    classification_data = classify_and_embed(actor, actor_wheel_state, reflex_type)

    prompt = f"{MODEL_CONFIG['system_prompt']}\n\nInput: {input_text}\n\n"
    prompt += f"Classification: {classification_data['class_code']} ({classification_data['archetype_variant']})\n"
    prompt += f"Containment Required: {classification_data['containment_required']}\n"
    prompt += f"Progressive: {classification_data['progressive']}\n"
    prompt += f"Generate a {STORYLINE_CONFIG['format']} with {STORYLINE_CONFIG['lines']} lines."

    # Placeholder for actual OpenAI call
    story_output = f"[Generated story for {actor} @ {actor_wheel_state} → {classification_data['class_code']}]"

    if LOGGING_CONFIG["enabled"]:
        log_entry = {
            "timestamp": generate_session_label(),
            "actor": actor,
            "actor_wheel_state": actor_wheel_state,
            "reflex_type": reflex_type,
            "classification": classification_data,
            "story": story_output
        }
        try:
            with open(LOGGING_CONFIG["log_file"], "a", encoding='utf-8') as log:
                log.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"⚠️ Logging failed: {e}")

    return story_output
