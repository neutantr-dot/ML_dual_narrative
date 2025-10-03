import csv

def load_csv(path):
    """Loads a CSV file and returns a list of dictionaries."""
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def symbolic_reflex(mismatch_type, archetype, taxonomy_path):
    """
    Maps mismatch type and archetype to symbolic theme, emotional cost, and repair path.
    Returns a dictionary with narrative enrichment.
    """
    try:
        taxonomy = load_csv(taxonomy_path)
        for row in taxonomy:
            if all(key in row for key in [
                "Mismatch_Type", "Reflex_Archetype", "Symbolic_Theme",
                "Emotional_Cost", "Repair_Path"
            ]):
                if row["Mismatch_Type"].strip().lower() == mismatch_type.strip().lower() and \
                   row["Reflex_Archetype"].strip().lower() == archetype.strip().lower():
                    return {
                        "symbolic_theme": row["Symbolic_Theme"],
                        "emotional_cost": row["Emotional_Cost"],
                        "repair_path": row["Repair_Path"]
                    }
    except Exception as e:
        print(f"⚠️ Symbolic reflex mapping failed: {e}")

    return {
        "symbolic_theme": "unspecified rupture",
        "emotional_cost": "ambiguous tension",
        "repair_path": "presence and breath"
    }
