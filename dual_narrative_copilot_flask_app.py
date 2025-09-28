from flask import Flask, request, jsonify
from narrative_engine import generate_narrative
import yaml

# === Initialize Flask App ===
app = Flask(__name__)

# === Load Configuration ===
try:
    with open("copilot_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"⚠️ Failed to load config: {e}")
    config = {}

# === Emotional OS Endpoint ===
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)

        voice_inputs = data.get("voice_inputs", [])
        background_inputs = data.get("background_inputs", [])
        actor = data.get("actor", "User")
        user_id = data.get("user_id", "anonymous")

        result = generate_narrative(
            actor,
            user_id,
            " ".join(voice_inputs),
            " ".join(background_inputs),
            config
        )

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

# === Startup Echo ===
if __name__ == "__main__":
    print("🌀 Emotional OS (Flask) listening on /generate...")
    app.run(host="0.0.0.0", port=5000)
