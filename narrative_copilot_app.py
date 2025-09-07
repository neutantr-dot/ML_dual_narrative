import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Constants
DELIMITER = "|"
VOICE_FIELDS = 4
BACKGROUND_FIELDS = 5
STORYLINE_LINES = 20
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"

# Load headers from GitHub
@st.cache_data
def load_headers():
    try:
        response = requests.get(HEADERS_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=DELIMITER, engine="python", quotechar='"', on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load headers.csv: {e}")
        return pd.DataFrame(columns=["Input_file", "Field", "Label"])

# Cache uploaded file contents and objects in session state
def cache_file(name, uploaded_file):
    if uploaded_file:
        st.session_state[name + "_data"] = uploaded_file.getvalue().decode("utf-8")
        st.session_state[name + "_obj"] = uploaded_file
    else:
        st.session_state.setdefault(name + "_data", "")
        st.session_state.setdefault(name + "_obj", None)

# Parse transposed input file
def parse_transposed_file(file_text):
    if not file_text:
        return {}, []
    rows = [line.split(DELIMITER) for line in file_text.splitlines()]
    if not rows or len(rows) < 2:
        return {}, []
    versions = rows[0]
    data_by_version = {version: [] for version in versions}
    for row in rows[1:]:
        for i, value in enumerate(row):
            if i < len(versions):
                data_by_version[versions[i]].append(value)
    return data_by_version, versions

# Generate version label with (1), (2), etc.
def generate_version_label(existing_versions):
    today = datetime.now().strftime("%a %b %d, %Y")
    count = sum(1 for v in existing_versions if v.startswith(today))
    return f"{today} ({count + 1})"

# Insert new column at the beginning of transposed file
def insert_column_to_transposed_file(file_text, new_column):
    rows = [line.split(DELIMITER) for line in file_text.splitlines()] if file_text else []
    while len(rows) < len(new_column):
        rows.append([])
    for i, value in enumerate(new_column):
        rows[i].insert(0, value)
    return "\n".join([DELIMITER.join(row) for row in rows])

# Streamlit UI
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.sidebar.title("📁 Upload Files")

# Upload files
voice_file = st.sidebar.file_uploader("Upload voice_input.txt", type="txt")
background_file = st.sidebar.file_uploader("Upload background.txt", type="txt")
storyline_file = st.sidebar.file_uploader("Upload storyline.txt", type="txt")

# Cache uploaded files
cache_file("voice_file", voice_file)
cache_file("background_file", background_file)
cache_file("storyline_file", storyline_file)

# Toggle for prefill
prefill_enabled = st.sidebar.toggle("Enable Prefill", value=False)

# Load headers
headers_df = load_headers()

st.title("🧠 Dual Narrative Co-Pilot Storytelling")

# Parse transposed files
voice_blocks, voice_versions = parse_transposed_file(st.session_state["voice_file_data"])
background_blocks, background_versions = parse_transposed_file(st.session_state["background_file_data"])
storyline_versions = parse_transposed_file(st.session_state["storyline_file_data"])[1]

# Section 1: Argument
st.subheader("🗣️ Describe Argument That Happened")
selected_voice_version = st.selectbox("📅 Voice Input Version", voice_versions) if voice_versions else None
voice_prefill = voice_blocks.get(selected_voice_version, [""] * VOICE_FIELDS) if prefill_enabled else [""] * VOICE_FIELDS

voice_inputs = []
for i in range(VOICE_FIELDS):
    label_row = headers_df[
        (headers_df["Input_file"] == "voic_input") &
        (headers_df["Field"] == f"input{i+1}")
    ]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Voice Input {i+1}"
    value = st.text_input(label_text, value=voice_prefill[i])
    voice_inputs.append(value)

# Section 2: Background
st.subheader("🌄 Describe Your Background")
selected_background_version = st.selectbox("📅 Background Version", background_versions) if background_versions else None
background_prefill = background_blocks.get(selected_background_version, [""] * BACKGROUND_FIELDS) if prefill_enabled else [""] * BACKGROUND_FIELDS

background_inputs = []
for i in range(BACKGROUND_FIELDS):
    label_row = headers_df[
        (headers_df["Input_file"] == "background") &
        (headers_df["Field"] == f"input{i+1}")
    ]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Background Input {i+1}"
    value = st.text_input(label_text, value=background_prefill[i])
    background_inputs.append(value)

# Generate storyline
if st.button("✨ Generate Dual Narrative Storyline"):
    storyline = [
        "This is a placeholder for your dual narrative.",
        "It will reflect both the argument and your background.",
        "Imagine a story that weaves emotional tension with personal history.",
        "Each line adds depth, empathy, and perspective.",
    ] + [f"Story line {i+1}" for i in range(STORYLINE_LINES)]

    st.subheader("📜 Generated Storyline")
    st.text_area("Scroll through your story:", value="\n".join(storyline), height=400)

    # Prepare new columns and store in session state
    st.session_state["new_voice_column"] = [generate_version_label(voice_versions)] + voice_inputs
    st.session_state["new_background_column"] = [generate_version_label(background_versions)] + background_inputs
    st.session_state["new_storyline_column"] = [generate_version_label(storyline_versions)] + storyline
    st.session_state["story_generated"] = True

# Persistent download buttons
if st.session_state.get("story_generated"):
    st.download_button("⬇️ Save Updated Voice Input",
        data=insert_column_to_transposed_file(
            st.session_state["voice_file_data"], st.session_state["new_voice_column"]),
        file_name="voice_input.txt", mime="text/plain")

    st.download_button("⬇️ Save Updated Background",
        data=insert_column_to_transposed_file(
            st.session_state["background_file_data"], st.session_state["new_background_column"]),
        file_name="background.txt", mime="text/plain")

    st.download_button("⬇️ Save New Storyline",
        data=insert_column_to_transposed_file(
            st.session_state["storyline_file_data"], st.session_state["new_storyline_column"]),
        file_name="storyline.txt", mime="text/plain")



























 



