import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Constants
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
DELIMITER = "|"
VOICE_BLOCK_SIZE = 5  # 1 version line + 4 input lines
BACKGROUND_BLOCK_SIZE = 6  # 1 version line + 5 input lines

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

# Parse uploaded input file into blocks
def parse_blocks(data, block_size):
    blocks = {}
    i = 0
    while i + block_size - 1 < len(data):
        version = data[i][0]
        inputs = [data[i + j][0] if len(data[i + j]) > 0 else "" for j in range(1, block_size)]
        blocks[version] = inputs
        i += block_size
    return blocks

# Parse uploaded input file
def parse_input_file(uploaded_file):
    if uploaded_file is None:
        return []
    content = uploaded_file.getvalue().decode("utf-8").splitlines()
    return [line.split(DELIMITER) for line in content]

# Append new row to file
def append_to_file(existing_file, new_row):
    if existing_file is None:
        return DELIMITER.join(new_row)
    content = existing_file.getvalue().decode("utf-8").splitlines()
    content.insert(1, DELIMITER.join(new_row))
    return "\n".join(content)

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

# Parse input files
voice_data = parse_input_file(voice_file)
background_data = parse_input_file(background_file)

# Parse blocks
voice_blocks = parse_blocks(voice_data, VOICE_BLOCK_SIZE)
background_blocks = parse_blocks(background_data, BACKGROUND_BLOCK_SIZE)

# Section 1: Argument
st.subheader("🗣️ Describe Argument That Happened")
voice_versions = list(voice_blocks.keys())
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
background_versions = list(background_blocks.keys())
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

    # Prepare new rows
    timestamp = datetime.now().strftime("%a %b %d, %Y (%H:%M)")
    new_voice_row = [timestamp] + voice_inputs
    new_background_row = [timestamp] + background_inputs
    new_storyline_row = [timestamp] + storyline

    # Download buttons
    st.download_button("⬇️ Save Updated Voice Input", data=append_to_file(voice_file, new_voice_row),
                       file_name="voice_input.txt", mime="text/plain")
    st.download_button("⬇️ Save Updated Background", data=append_to_file(background_file, new_background_row),
                       file_name="background.txt", mime="text/plain")
    st.download_button("⬇️ Save New Storyline", data=append_to_file(storyline_file, new_storyline_row),
                       file_name="storyline.txt", mime="text/plain")

























 



