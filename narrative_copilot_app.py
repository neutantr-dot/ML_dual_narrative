import streamlit as st
import pandas as pd
import io
from datetime import datetime
from dispatcher import orchestrate_story  # Your ML engine

# --- Page Setup ---
st.set_page_config(page_title="Narrative Copilot", layout="wide")
st.title("🧠 Narrative Copilot")

# --- Load Header Labels from uploaded headers.csv ---
try:
    header_df = pd.read_csv("headers.csv", sep=";")
    header_labels = {
        "voice_input": header_df[header_df["InputSet"] == 1]["Label"].tolist(),
        "background": header_df[header_df["InputSet"] == 2]["Label"].tolist()
    }
except Exception as e:
    st.error("⚠️ Failed to load headers.csv.")
    header_labels = {"voice_input": [], "background": []}

# --- Upload Section ---
st.sidebar.header("Upload Your Inputs")
uploaded_files = st.sidebar.file_uploader(
    "Upload 2 CSV files: voice_input.csv and background.csv",
    type="csv",
    accept_multiple_files=True
)

# --- Clarification Input ---
st.subheader("Clarify Your Voice Inputs")
clarification = st.text_area(
    "Add any clarifying notes, emotional tone, or narrative intent you'd like the story to reflect",
    placeholder="e.g., Make the story emotionally layered and reflective..."
)

# --- Parse Uploaded Files ---
inputs = {}
missing_keys = []
EXPECTED_FILES = ["voice_input", "background"]

if uploaded_files:
    for file in uploaded_files:
        key = file.name.replace(".csv", "")
        df = pd.read_csv(file, header=None)
        inputs[key] = df

    for key in EXPECTED_FILES:
        if key not in inputs:
            missing_keys.append(key)

    if missing_keys:
        st.warning(f"Missing required files: {', '.join(missing_keys)}")
else:
    st.info("Please upload both voice_input.csv and background.csv to proceed.")

# --- Versioning Helper ---
def get_session_label(existing_df):
    today = datetime.now().strftime("%b %d, %Y")
    version = 1
    if existing_df is not None and not existing_df.empty:
        version = sum([1 for col in existing_df.columns if today in col]) + 1
    return f"Session {today} (v{version})"

# --- Generate Story ---
if st.button("Generate Storyline") and not missing_keys:
    inputs["clarification"] = clarification
    story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")

    if "story_output" not in st.session_state:
        st.session_state["story_output"] = pd.DataFrame()

    session_label = get_session_label(st.session_state["story_output"])

    # Insert timestamped column into each input
    for key in EXPECTED_FILES:
        df = inputs[key]
        new_col = pd.Series(df.iloc[:, 0].tolist(), name=session_label)
        updated_df = pd.concat([df, new_col], axis=1)
        inputs[key] = updated_df

    # Save story output
    story_df = pd.DataFrame([story_output], columns=[session_label])
    st.session_state["story_output"] = pd.concat([st.session_state["story_output"], story_df], axis=1)

    st.success("✅ Storyline generated successfully!")
    st.text_area("Generated Storyline", story_output, height=400)

# --- Display Inputs with Row Labels ---
st.subheader("📋 Input Previews")
for key in EXPECTED_FILES:
    if key in inputs:
        st.markdown(f"**{key.replace('_', ' ').title()}**")
        labels = header_labels.get(key, [])
        df = inputs[key]
        for i in range(len(df)):
            label = labels[i] if i < len(labels) else f"Row {i+1}"
            st.caption(f"{label}: {df.iloc[i, 0]}")

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
