import streamlit as st
import pandas as pd
import io
from datetime import datetime
from dispatcher import orchestrate_story  # Your ML engine

# --- Ordinal Date Formatter ---
def format_session_date():
    now = datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return now.strftime(f"%a %b {day}{suffix}, %Y")

# --- Page Setup ---
st.set_page_config(page_title="Narrative Copilot", layout="wide")
st.title("🧠 Narrative Copilot")

# --- Load Header Labels ---
try:
    header_df = pd.read_csv("headers.csv", sep=";")
    voice_labels = header_df[header_df["InputSet"] == 1]["Label"].tolist()
    background_labels = header_df[header_df["InputSet"] == 2]["Label"].tolist()
except Exception as e:
    st.error("⚠️ Failed to load headers.csv.")
    voice_labels, background_labels = [], []

# --- Sidebar Upload ---
st.sidebar.header("Upload Previous Session Files")
uploaded_files = st.sidebar.file_uploader(
    "Upload voice_input.csv and background.csv",
    type="csv",
    accept_multiple_files=True
)
prefill_toggle = st.sidebar.checkbox("Prefill with uploaded session")

# --- Parse Uploaded Files ---
inputs = {}
EXPECTED_FILES = ["voice_input", "background"]
for file in uploaded_files or []:
    key = file.name.replace(".csv", "").replace(" (2)", "").replace(" (3)", "")
    df = pd.read_csv(file, header=None)
    inputs[key] = df

# --- Input Sections ---
st.subheader("Clarify Your Voice Inputs")
voice_inputs = []
for i, label in enumerate(voice_labels):
    default = inputs.get("voice_input").iloc[i + 1, 0] if prefill_toggle and "voice_input" in inputs else ""
    voice_inputs.append(st.text_area(label, value=default, key=f"voice_{i}"))

st.subheader("Background Context")
background_inputs = []
for i, label in enumerate(background_labels):
    default = inputs.get("background").iloc[i + 1, 0] if prefill_toggle and "background" in inputs else ""
    background_inputs.append(st.text_area(label, value=default, key=f"background_{i}"))

# --- Generate Story ---
if st.button("Generate Storyline"):
    session_date = format_session_date()
    def count_existing(df, base_date):
        return sum([1 for col in df.columns if str(col).startswith(f"Session {base_date}")])
    base_date = session_date
    count_voice = count_existing(inputs.get("voice_input", pd.DataFrame()), base_date) + 1
    count_bg = count_existing(inputs.get("background", pd.DataFrame()), base_date) + 1
    count_story = count_existing(st.session_state.get("story_output", pd.DataFrame()), base_date) + 1

    label_voice = f"Session {base_date} ({count_voice})"
    label_bg = f"Session {base_date} ({count_bg})"
    label_story = f"Session {base_date} ({count_story})"

    # Build new columns
    voice_column = pd.Series([session_date] + voice_inputs, name=label_voice)
    background_column = pd.Series([session_date] + background_inputs, name=label_bg)

    # Append to inputs
    for key, new_col in zip(EXPECTED_FILES, [voice_column, background_column]):
        df = inputs.get(key, pd.DataFrame())
        if df.empty:
            df = pd.DataFrame({new_col.name: new_col})
        else:
            df = pd.concat([df, new_col], axis=1)
        inputs[key] = df

    # Run ML engine
    inputs["clarification"] = "User clarification embedded in inputs"
    story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")

    # Append story output
    if "story_output" not in st.session_state:
        st.session_state["story_output"] = pd.DataFrame(index=[0])
    story_col = pd.Series([story_output], name=label_story)
    st.session_state["story_output"] = pd.concat([st.session_state["story_output"], story_col], axis=1)

    st.success("✅ Storyline generated successfully!")
    st.text_area("Generated Storyline", story_output, height=400, key="story_output_area")

# --- Download Buttons ---
st.subheader("📁 Download Your Files")
for key in EXPECTED_FILES:
    if key in inputs:
        buffer = io.StringIO()
        inputs[key].to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        st.download_button(
            label=f"Download {key}.csv",
            data=buffer.getvalue(),
            file_name=f"{key}.csv",
            mime="text/csv",
            key=f"download_{key}"
        )

# --- Download Story Output ---
if "story_output" in st.session_state and not st.session_state["story_output"].empty:
    buffer = io.StringIO()
    st.session_state["story_output"].to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="Download Story Output",
        data=buffer.getvalue(),
        file_name="story_output.csv",
        mime="text/csv",
        key="download_story"
    )

# --- Session History Viewer ---
st.subheader("🕰️ Browse Past Story Sessions")
if "story_output" in st.session_state and not st.session_state["story_output"].empty:
    selected_col = st.selectbox(
        "Select a session to view its storyline",
        st.session_state["story_output"].columns[::-1]
    )
    st.text_area("Storyline Preview", st.session_state["story_output"][selected_col].iloc[0], height=300)




