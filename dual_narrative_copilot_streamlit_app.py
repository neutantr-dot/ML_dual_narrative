import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import yaml  # Required for config loading
import csv
import uuid

# === Constants ===
DELIMITER = ","
VOICE_FIELDS = 4
BACKGROUND_FIELDS = 5
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
# COPILOT_CONFIG = "copilot_config.yaml" #using flask backend

#====# Block 2 Load headers from GitHub
# === Load Header Definitions ===
@st.cache_data
def load_headers():
    try:
        response = requests.get(HEADERS_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=",", quotechar='"', engine="python")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load headers.csv: {e}")
        return pd.DataFrame(columns=["Input_file", "Field", "Label"])

headers_df = load_headers()
if headers_df.empty:
    st.warning("⚠️ Header definitions are missing or failed to load.")
		
#====# Block 3: File upload and caching (.txt with round 1 and round 2 support)
# === File Uploads ===
st.sidebar.title("📁 Upload .txt Files")

voice_file = st.sidebar.file_uploader("Upload voice_input.txt", type="txt")
background_file = st.sidebar.file_uploader("Upload background.txt", type="txt")
storyline_file = st.sidebar.file_uploader("Upload storyline.txt", type="txt")

# === Cache file content in session state ===
def cache_file(name, uploaded_file):
    if uploaded_file:
        text = uploaded_file.getvalue().decode("utf-8")
        st.session_state[name + "_data"] = text
        st.session_state[name + "_obj"] = uploaded_file
    else:
        st.session_state.setdefault(name + "_data", "")
        st.session_state.setdefault(name + "_obj", None)

cache_file("voice_file", voice_file)
cache_file("background_file", background_file)
cache_file("storyline_file", storyline_file)

#====# Block 4: File parsing (.txt with round 1 and round 2 support, comma-delimited with quoted text)
# === Parse transposed .txt file into versioned blocks ===

def parse_transposed_file(file_text):
    if not file_text:
        return {}, [], ""
    reader = csv.reader(file_text.splitlines(), delimiter=",", quotechar='"')
    rows = list(reader)
    if not rows or len(rows) < 2:
        return {}, [], ""
    versions = rows[0]
    data_by_version = {version: [] for version in versions}
    for row in rows[1:]:
        for i, value in enumerate(row):
            if i < len(versions):
                data_by_version[versions[i]].append(value)
    full_string = " ".join([" ".join(data_by_version[v]) for v in versions])
    return data_by_version, versions, full_string

# === Parse and flatten ===
voice_blocks, voice_versions, voice_recursive_string = parse_transposed_file(st.session_state["voice_file_data"])
background_blocks, background_versions, background_recursive_string = parse_transposed_file(st.session_state["background_file_data"])

# === Validation (optional during testing) ===
st.write("Voice Versions:", voice_versions)
st.write("Voice Blocks:", voice_blocks)

# === Flatten all columns into a single recursive string ===
# def flatten_all_versions(file_text, delimiter="|"):
#     if not file_text:
#         return ""
#     rows = [line.split(delimiter) for line in file_text.splitlines()]
#     return " ".join([" ".join(row[1:]) for row in rows[1:]])
#
# voice_recursive_string = flatten_all_versions(st.session_state["voice_file_data"])
# background_recursive_string = flatten_all_versions(st.session_state["background_file_data"])

#====# Block 5: Appending (comma-delimited with quoted "text,text")

def append_column_to_transposed_file(file_text, new_column):
    rows = [line.split(",") for line in file_text.splitlines()] if file_text else []
    while len(rows) < len(new_column):
        rows.append([])
    for i, value in enumerate(new_column):
        rows[i].append(f'"{value}"')
    return "\n".join([",".join(row) for row in rows])

# === Prefill Mode Toggle ===
prefill_mode = st.sidebar.radio("Prefill Source", ["Latest (Column 1)", "Select Version"])

if prefill_mode == "Latest (Column 1)":
    selected_voice_version = voice_versions[0] if voice_versions else None
    selected_background_version = background_versions[0] if background_versions else None
else:
    selected_voice_version = st.selectbox("📅 Voice Input Version", voice_versions) if voice_versions else None
    selected_background_version = st.selectbox("📅 Background Version", background_versions) if background_versions else None

prefill_enabled = selected_voice_version is not None and selected_background_version is not None

#====# Block 6: Input Field Construction
st.subheader("🗣️ Describe Argument That Happened")
selected_voice_version = st.selectbox("📅 Voice Input Version", voice_versions) if voice_versions else None
voice_prefill = voice_blocks.get(selected_voice_version, [""] * VOICE_FIELDS) if prefill_enabled else [""] * VOICE_FIELDS

voice_inputs = []
for i in range(VOICE_FIELDS):
    label_row = headers_df[
        (headers_df["Input_file"] == "voice_input") &
        (headers_df["Field"] == f"input{i+1}")
    ]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Voice Input {i+1}"
    value = st.text_input(label_text, value=voice_prefill[i])
    voice_inputs.append(value)

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

#====# Block 7&8: Storyline Generation (.txt construct, Flask-compatible with actor and user_id)
# === Actor and User ID ===
actor = st.sidebar.text_input("🎭 Actor Name", value="default_actor")
user_id = st.sidebar.text_input("🆔 User ID", value="user_001")
# user_id = st.sidebar.text_input("🆔 User ID", value=str(uuid.uuid4())[:8])
								
FLASK_URL = "http://localhost:5000/generate"  # or your ngrok tunnel endpoint

if st.button("✨ Generate Dual Narrative Storyline"):
    payload = {
        "inputs": voice_inputs,
        "background": " ".join(background_inputs),
        "actor": actor,
        "user_id": user_id
    }

    try:
        response = requests.post(FLASK_URL, json=payload)
        if response.status_code == 200:
            result = response.json().get("result", "[No response]")
        else:
            result = f"⚠️ Error {response.status_code}: {response.text}"
    except Exception as e:
        result = f"⚠️ Request failed: {e}"

    st.subheader("📜 Generated Storyline")
    st.text_area("Scroll through your story:", value=result, height=400)

    # Cache for appending
    timestamp = datetime.now().strftime("%a %b %d, %Y (%H:%M)")
    st.session_state["new_voice_column"] = [timestamp] + voice_inputs
    st.session_state["new_background_column"] = [timestamp] + background_inputs
    st.session_state["new_storyline_column"] = [timestamp] + result.splitlines()
    st.session_state["story_generated"] = True
	
#====# Block 9: Download Buttons (prepend new column as column 1)

def prepend_column_to_transposed_file(file_text, new_column):
    rows = [line.split(",") for line in file_text.splitlines()] if file_text else []
    while len(rows) < len(new_column):
        rows.append([])
    for i, value in enumerate(new_column):
        rows[i].insert(1, f'"{value}"')  # insert after timestamp header
    return "\n".join([",".join(row) for row in rows])

if st.session_state.get("story_generated"):
    st.download_button("⬇️ Save Updated Voice Input",
        data=prepend_column_to_transposed_file(
            st.session_state["voice_file_data"], st.session_state["new_voice_column"]),
        file_name="voice_input.txt", mime="text/plain")

    st.download_button("⬇️ Save Updated Background",
        data=prepend_column_to_transposed_file(
            st.session_state["background_file_data"], st.session_state["new_background_column"]),
        file_name="background.txt", mime="text/plain")

    st.download_button("⬇️ Save New Storyline",
        data=prepend_column_to_transposed_file(
            st.session_state["storyline_file_data"], st.session_state["new_storyline_column"]),
        file_name="storyline.txt", mime="text/plain")










