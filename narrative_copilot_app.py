import streamlit as st
import pandas as pd
import io
from datetime import datetime
from dispatcher import orchestrate_story  # Your ML engine

# --- Page Setup ---
st.set_page_config(page_title="Narrative Copilot", layout="wide")
st.title("🧠 Narrative Copilot")

# --- Load Header Labels from headers.csv ---
try:
    header_df = pd.read_csv("headers.csv", sep=";")
    voice_labels = header_df[header_df["InputSet"] == 1]["Label"].tolist()
    background_labels = header_df[header_df["InputSet"] == 2]["Label"].tolist()
except Exception as e:
    st.error("⚠️ Failed to load headers.csv.")
    voice_labels, background_labels = [], []

# --- Sidebar: Upload + Prefill Toggle ---
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

if uploaded_files:
    for file in uploaded_files:
        key = file.name.replace(".csv", "")
        df = pd.read_csv(file, header=None)
        inputs[key] = df

# --- Voice Input Section ---
st.subheader("Clarify Your Voice Inputs")
voice_inputs = []
for i, label in enumerate(voice_labels):
    default_value = ""
    if prefill_toggle and "voice_input" in inputs and i < len(inputs["voice_input"]):
        default_value = inputs["voice_input"].iloc[i, 0]
    voice_inputs.append(st.text_area(label, value=default_value, key=f"voice_{i}"))

# --- Background Input Section ---
st.subheader("Background Context")
background_inputs = []
for i, label in enumerate(background_labels):
    default_value = ""
    if prefill_toggle and "background" in inputs and i < len(inputs["background"]):
        default_value = inputs["background"].iloc[i, 0]
    background_inputs.append(st.text_area(label, value=default_value, key=f"background_{i}"))

# --- Versioning Helper ---
def get_session_label(existing_df):
    today = datetime.now().strftime("%a, %b %d (%-I)")
    version = 1
    if existing_df is not None and not existing_df.empty:
        version = sum([1 for col in existing_df.columns if today in col]) + 1
    return f"{today} (v{version})"

# --- Generate Story ---
if st.button("Generate Storyline"):
    inputs["voice_input"] = pd.DataFrame([[v] for v in voice_inputs])
    inputs["background"] = pd.DataFrame([[b] for b in background_inputs])
    inputs["clarification"] = "User clarification embedded in inputs"

    story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")

    if "story_output" not in st.session_state:
        st.session_state["story_output"] = pd.DataFrame()

    session_label = get_session_label(st.session_state["story_output"])

    # Append session column to each input
    for key in EXPECTED_FILES:
        df = inputs[key]
        if df.shape[1] == 1:
            df.columns = ["Initial"]
        df[session_label] = pd.Series(df.iloc[:, 0].tolist())
        inputs[key] = df

    # Save story output
    story_df = pd.DataFrame([story_output], columns=[session_label])
    st.session_state["story_output"] = pd.concat([st.session_state["story_output"], story_df], axis=1)

    st.success("✅ Storyline generated successfully!")
    st.text_area("Generated Storyline", story_output, height=400)

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
    st.markdown("**Story Output**")
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
