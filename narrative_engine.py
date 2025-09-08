import openai
import yaml
import json
import logging

# Load config
def load_config(path="copilot_config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

# Setup logging
if config.get("logging", {}).get("enabled", False):
    logging.basicConfig(
        filename=config["logging"]["log_file"],
        level=getattr(logging, config["logging"]["log_level"].upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

# Load emotional grammar map
def load_emotional_grammar(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        logging.warning("Emotional grammar map not found or invalid.")
        return {}

# Apply reflex logic (placeholder)
def apply_reflex_logic(story_lines, mode="archetype_shift"):
    # Placeholder logic — no transformation yet
    logging.info(f"Reflex logic applied: mode={mode}")
    return story_lines

# Generate storyline using OpenAI
def generate_storyline(voice_inputs, background_inputs, config_path="copilot_config.yaml"):
    config = load_config(config_path)
    grammar_map = load_emotional_grammar(config["emotional_grammar"]["path"]) if config["emotional_grammar"]["enabled"] else {}

    prompt = (
        f"{config['model']['system_prompt']}\n\n"
        "Voice Inputs:\n" + "\n".join(voice_inputs) + "\n\n"
        "Background Inputs:\n" + "\n".join(background_inputs) + "\n\n"
        f"Generate a {config['storyline']['format']} story in {config['storyline']['lines']} lines.\n"
    )

    if config["storyline"]["include_classification"]:
        labels = ", ".join(config["storyline"]["classification_labels"])
        prompt += f"\nClassify the story using one of the following labels: {labels}.\nReturn the story first, then the classification label on a new line prefixed with 'Classification:'"

    try:
        openai.api_key = config["model"].get("api_key")  # Or use env/secrets
        response = openai.ChatCompletion.create(
            model=config["model"]["name"],
            messages=[
                {"role": "system", "content": config["model"]["system_prompt"]},
                {"role": "user", "content": prompt}
            ],
            temperature=config["model"]["temperature"],
            max_tokens=config["model"]["max_tokens"]
        )
        output = response["choices"][0]["message"]["content"]
        lines = output.splitlines()

        # Extract classification
        classification = lines[-1].replace("Classification:", "").strip() if config["storyline"]["include_classification"] else "N/A"
        story_lines = lines[:-1] if config["storyline"]["include_classification"] else lines

        # Apply reflex logic if enabled
        if config["reflex_logic"]["enabled"]:
            story_lines = apply_reflex_logic(story_lines, config["reflex_logic"]["mode"])

        logging.info(f"Story generated with classification: {classification}")
        return story_lines, classification

    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return ["⚠️ Error generating story."], config["classification"]["fallback_label"]
