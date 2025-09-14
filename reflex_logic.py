import json
import random

with open("Emotional_grammar.json") as f:
    grammar = json.load(f)

def reflex_trigger(stimulus):
    emotion_map = {
        "threat": "fear",
        "loss": "sadness",
        "praise": "joy",
        "betrayal": "anger",
        "connection": "trust"
    }
    emotion = emotion_map.get(stimulus, "anticipation")
    intensity = random.choice(grammar["modifiers"]["intensity"])
    direction = random.choice(grammar["modifiers"]["direction"])
    return {
        "emotion": emotion,
        "intensity": intensity,
        "direction": direction
    }

# Example
if __name__ == "__main__":
    print(reflex_trigger("praise"))
