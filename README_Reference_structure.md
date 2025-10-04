Absolutely, Neu — here’s a clean, structured **Technical Glossary** for your emotional OS, covering all `.py` functions with parameters and their linked `.csv` usage. This gives you a modular map of how the system thinks, routes, and repairs.

---

## 🧠 Technical Glossary: Emotional OS Functions & CSV Integration

### 🔹 `narrative_engine.py`
**Role:** Orchestrates input parsing, wheel detection, reflex routing, and narrative output.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `generate_narrative` | `inputs`, `actor`, `user_id`, `background`, `config` | Main entry point for storyline generation | `wheel_codex.csv`, `transmission_map.csv`, `wheel_layers.csv`, `polarity_drift.csv`, `classification.csv`, `7_reflex_taxonomy.csv`, `emotional_grammar.json` |
| `detect_wheel_state` | `voice_input`, `background`, `wheel_codex_path` | Detects emotional wheel state from input | `wheel_codex.csv` |
| `modulate_tone` | `wheel_state`, `grammar`, `archetype_variant`, `geometry_alert` | Applies emotional tone and reframe | `emotional_grammar.json` |
| `flatten_inputs` | `inputs` | Joins input fields into a single string | — |
| `build_story` | `inputs`, `classification` | Formats narrative output | — |
| `log_classification` | `user_id`, `actor`, `class_code`, `log_path` | Writes classification to log | `classification.csv` |

---

### 🔹 `reflex_logic.py`
**Role:** Reflex routing, symbolic enrichment, session logging.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `process_reflex_bundle` | `actor`, `wheel_state`, `voice_input`, `transmission_map_path`, `classification_path`, `taxonomy_path`, `wheel_domains`, `wheel_layers_path`, `polarity_drift_path` | Constructs reflex bundle with symbolic and geometric overlays | `transmission_map.csv`, `archetype_classification.csv`, `7_reflex_taxonomy.csv`, `wheel_layers.csv`, `polarity_drift.csv` |
| `get_containment_strategy` | `wheel_state`, `voice_input`, `transmission_map_path`, `wheel_domains` | Returns symbolic containment strategy | `transmission_map.csv`, `somatic_protocol.csv`, `linguistic_reframe_map.csv` |
| `preview_available_reflexes` | `transmission_map_path` | Lists reflex types per wheel state | `transmission_map.csv` |

---

### 🔹 `reflex_core.py`
**Role:** Low-level reflex detection and bundle construction.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `detect_reflex` | `wheel_state`, `voice_input`, `transmission_map_path` | Matches trigger to reflex type | `transmission_map.csv` |
| `apply_containment` | `wheel_state`, `voice_input`, `transmission_map_path` | Returns containment strategy | `transmission_map.csv` |
| `classify_actor` | `actor`, `wheel_state`, `reflex_type`, `classification_path` | Returns archetype classification | `archetype_classification.csv` |
| `process_reflex_bundle` | same as above | Full reflex + geometry + classification bundle | multiple CSVs |
| `default_reflex_bundle` | — | Fallback bundle | — |

---

### 🔹 `classification_engine.py`
**Role:** Archetype classification logic.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `classify_actor_from_wheel` | `actor`, `actor_wheel_state`, `reflex_type`, `classification_path` | Returns class code, variant, containment flag | `archetype_classification.csv` |
| `preview_classification` | `classification_path` | Prints classification logic | `archetype_classification.csv` |

---

### 🔹 `classification.py`
**Role:** Logging and embedding classification into narrative.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `generate_session_label` | — | Timestamp for logging | — |
| `write_classification_output` | `actor`, `wheel_state`, `reflex_type`, `result` | Writes classification to file | `classification.csv` |
| `classify_and_embed` | `actor`, `wheel_state`, `reflex_type` | Returns classification bundle | `archetype_classification.csv` |
| `generate_story` | `actor`, `wheel_state`, `reflex_type`, `input_text` | Generates story output | — |

---

### 🔹 `geometry_resolver.py`
**Role:** Resolves emotional geometry and constraint hits.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `resolve_geometry_state` | `wheel_domains`, `layers_path`, `codex_path`, `drift_path`, `ml_instruction_path` | Returns geometry alert, suggested action, overlays | `wheel_layers.csv`, `wheel_codex.csv`, `polarity_drift.csv`, `emotional_constraint_matrix.csv`, `ml_instruction.csv` |

---

### 🔹 `dual_narrative_trainer.py`
**Role:** Trainer and recentering stage injection.

| Function | Parameters | Description | CSVs Used |
|---------|------------|-------------|-----------|
| `inject_trainer_stage` | `actor`, `wheel_domains`, `reflex_type`, `containment_strategy` | Injects M3/F3 trainer stage | `wheel_layers.csv`, `wheel_codex.csv`, `polarity_drift.csv`, `ml_instruction.csv` |
| `inject_recentering_stage` | `actor`, `wheel_domains` | Injects M1/F1 recentering arc | — |

---

## 📄 CSV File Roles (Grouped by Layer)

### 🧩 Emotional Geometry
- `wheel_codex.csv`: defines wheel states, polarity shifts, rupture triggers
- `wheel_layers.csv`: maps internal/external/background flow
- `polarity_drift.csv`: tracks gear-lock, inversion, symbolic collapse
- `emotional_constraint_matrix.csv`: defines recursion gates and modulation logic

### 🔁 Reflex & Containment
- `transmission_map.csv`: maps wheel state to reflex, archetype, containment
- `containment_protocol.csv`: archetype-specific containment strategies
- `somatic_protocol.csv`: biomechanical regulation techniques
- `linguistic_reframe_map.csv`: phrasing logic for polarity restoration

### 🧠 Classification & Taxonomy
- `archetype_classification.csv`: maps actor, wheel state, reflex to archetype
- `classification.csv`: runtime log of actor, reflex, archetype, containment
- `7_reflex_taxonomy.csv`: symbolic themes, emotional cost, repair paths

### 🌀 Narrative & Expectation
- `5_cross_map_matrix.csv`: links female voice to male expectation mismatch
- `3_male_expectation_map.csv`: defines male blind spots and emotional triggers
- `2_female_voice_wheel.csv`: maps female inner voice to reflex and archetype
- `1_core_framework.csv`: defines rupture contexts and we-protocol stages
- `story_line_arc.csv`: narrative progression map

---

Let me know if you want this exported as a markdown reference sheet or embedded into your documentation. You’ve now got a full symbolic API for your emotional OS.
