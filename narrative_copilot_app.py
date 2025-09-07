import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Constants
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
DELIMITER = "|"

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

# Parse transposed input file
def parse_transposed_file(uploaded_file):
    if uploaded_file is None:
        return {}, []
    content = uploaded_file.getvalue().decode("utf-8").splitlines()
    rows = [line.split(DELIMITER) for line in content]
    if not rows or len(rows) < 2:
        return {}, []
    versions = rows[0]
    data_by_version = {version: [] for version in versions}
    for row in rows[1:]:
        for i, value in enumerate(row):
            if i < len(versions):
                data_by_version[versions[i]].append(value)
    return data_by_version, versions

# Append new column to transposed file
def append_column_to_transposed_file(existing_file, new_column):
    lines = []
    if existing_file is not None:
        lines = existing_file.getvalue().decode("utf-8").splitlines()
        rows = [line.split(DELIMITER) for line in lines]
    else:
        rows = []

    # Ensure enough rows exist
    while len(rows) < len(new_column):
        rows.append([])

    # Append new column
    for i, value in enumerate(new_column):
        rows[i].append(value)

    # Reconstruct file
    return "\n".join([DELIMITER.join(row) for row in rows])

# Streamlit UI
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.sidebar.title("📁 Upload Files")

# Upload files
voice_file = st.sidebar.file_uploader("Upload voice_input.txt", type="txt")
background_file = st.sidebar.file_uploader("Upload background.txt", type="txt")
storyline_file = st.sidebar.file_uploader("Upload storyline.txt", type="txt")

# Toggle for prefill
prefill_enabled = st.sidebar.toggle("Enable Prefill", value=False)

# Load headers
headers_df = load_headers()

st.title("🧠 Dual Narrative Co-Pilot Storytelling")

# Parse transposed files
voice_blocks, voice_versions = parse_transposed_file(voice_file)
background_blocks, background_versions = parse_transposed_file(background_file)

# Section 1: Argument
st.subheader("🗣️ Describe Argument That Happened")
selected_voice_version = st.selectbox("📅 Voice Input Version", voice_versions) if voice_versions else None
voice_prefill = voice_blocks.get(selected_voice_version, [""] * 4) if prefill_enabled else [""] * 4

voice_inputs = []
for i in range(4):
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
background_prefill = background_blocks.get(selected_background_version, [""] * 5) if prefill_enabled else [""] * 5

background_inputs = []
for i in range(5):
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
    ] + [f"Story line {i+1}" for i in range(16)]

    st.subheader("📜 Generated Storyline")
    st.text_area("Scroll through your story:", value="\n".join(storyline), height=400)

    # Prepare new columns
    timestamp = datetime.now().strftime("%a %b %d, %Y (%H:%M)")
    new_voice_column = [timestamp] + voice_inputs
    new_background_column = [timestamp] + background_inputs
    new_storyline_column = [timestamp] + storyline

    # Download buttons
    st.download_button("⬇️ Save Updated Voice Input",
        data=append_column_to_transposed_file(voice_file, new_voice_column),
        file_name="voice_input.txt", mime="text/plain")

    st.download_button("⬇️ Save Updated Background",
        data=append_column_to_transposed_file(background_file, new_background_column),
        file_name="background.txt", mime="text/plain")

    st.download_button("⬇️ Save New Storyline",
        data=append_column_to_transposed_file(storyline_file, new_storyline_column),
        file_name="storyline.txt", mime="text/plain")


























 



