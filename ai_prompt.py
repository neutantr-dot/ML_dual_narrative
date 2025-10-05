# ai_prompt.py

def enrich_with_prompt(narrative, actor="", user_id="", user_request=""):
    """
    Constrains enrichment to storyline-based interaction.
    """
    if not user_request or "story" not in user_request.lower():
        return "[AI Prompt] Please interact with the storyline. General topics are not supported."

    # Example: expand, shift location, change perspective
    enriched = (
        f"[AI Prompt Response]\n"
        f"You asked: {user_request}\n\n"
        f"Based on the narrative, here's a symbolic expansion:\n"
        f"In the new location, emotional dynamics shift. The actor's desire for autonomy becomes spatial — the kitchen becomes a refuge, a place of silence and control."
    )

    return enriched
