import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime
import yaml
import csv
import uuid

# === Constants ===
DELIMITER = ","
VOICE_FIELDS = 4
BACKGROUND_FIELDS = 5
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
CLASSIFICATION_LOG_PATH = "classification_copilot_0210.csv"
TRANSMISSION_MAP_PATH = "transmission_map.csv"

# === Endpoint Configuration ===
DEFAULT_FLASK_URL = "http://localhost:5000/generate"
NGROK_FLASK_URL = "https://9f6413e4376e.ngrok-free.app"
flask_mode = st.sidebar.radio("Flask Mode", ["Local", "Ngrok"])
FLASK_URL = NGROK_FLASK_URL if flask_mode == "Ngrok" else DEFAULT_FLASK_URL

try:
    status_check = requests.get(FLASK_URL.replace("/generate", "/status")).json()
    st.sidebar.success(f"Flask server live: {status_check['url']}")
except Exception as e:
    st.sidebar.error(f"Flask unreachable: {e}")

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

# === File Uploads ===
st.sidebar.title("📁 Upload .txt Files")
voice_file = st.sidebar.file_uploader("Upload voice_input.txt", type="txt")
background_file = st.sidebar.file_uploader("Upload background.txt", type="txt")
storyline_file = st.sidebar.file_uploader("Upload storyline.txt", type="txt")

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

# === Transposed File Parser ===
def parse_transposed_file(file_text):
    if not file_text:
        return {}, [], ""
    reader = csv.reader(file_text.splitlines(), delimiter=",", quotechar='"')
    rows = list(reader)
    if not rows or len(rows) < 2:
        return {}, [], ""
    versions = rows[0]
    blocks = {version: [] for version in versions}
    for row in rows[1:]:
        for i, value in enumerate(row):
            if i < len(versions):
                blocks[versions[i]].append(value.strip())
    full_string = " ".join([" ".join(blocks[v]) for v in versions])
    return blocks, versions, full_string

voice_blocks, voice_versions, voice_recursive_string = parse_transposed_file(st.session_state["voice_file_data"])
background_blocks, background_versions, background_recursive_string = parse_transposed_file(st.session_state["background_file_data"])

# === Prefill Mode Toggle ===
prefill_mode = st.sidebar.radio("Prefill Source", ["Latest (Column 1)", "Select Version"])
selected_voice_version = voice_versions[0] if prefill_mode == "Latest (Column 1)" and voice_versions else st.selectbox("📅 Voice Input Version", voice_versions)
selected_background_version = background_versions[0] if prefill_mode == "Latest (Column 1)" and background_versions else st.selectbox("📅 Background Version", background_versions)
prefill_enabled = selected_voice_version and selected_background_version

# === Input Field Construction
st.subheader("🗣️ Describe Argument That Happened")
voice_prefill = voice_blocks.get(selected_voice_version, [""] * VOICE_FIELDS) if prefill_enabled else [""] * VOICE_FIELDS
voice_inputs = []
for i in range(VOICE_FIELDS):
    label_row = headers_df[(headers_df["Input_file"] == "voice_input") & (headers_df["Field"] == f"input{i+1}")]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Voice Input {i+1}"
    value = st.text_input(label_text, value=voice_prefill[i])
    voice_inputs.append(value)

st.subheader("🌄 Describe Your Background")
background_prefill = background_blocks.get(selected_background_version, [""] * BACKGROUND_FIELDS) if prefill_enabled else [""] * BACKGROUND_FIELDS
background_inputs = []
for i in range(BACKGROUND_FIELDS):
    label_row = headers_df[(headers_df["Input_file"] == "background") & (headers_df["Field"] == f"input{i+1}")]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Background Input {i+1}"
    value = st.text_input(label_text, value=background_prefill[i])
    background_inputs.append(value)

# === Actor and User ID
actor = st.sidebar.text_input("🎭 Actor Name", value="default_actor")
user_id = st.sidebar.text_input("🆔 User ID", value="user_001")

# === Symbolic Overlay Toggle (for testing)
# === TESTING BLOCK: Symbolic Overlay Toggle ===
show_overlay = st.sidebar.checkbox("🌀 Show Symbolic Overlay", value=True)

# === Generate Storyline
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

    # === TESTING BLOCK: Classification Preview ===
    if "Classification:" in result:
        classification_line = [line for line in result.splitlines() if "Classification:" in line]
        if classification_line:
            st.success(f"🧠 Classification Preview → {classification_line[0].replace('Classification:', '').strip()}")

    # === Cache for appending
    timestamp = datetime.now().strftime("%a %b %d, %Y (%H:%M)")
    st.session_state["new_voice_column"] = [timestamp] + voice_inputs
    st.session_state["new_background_column"] = [timestamp] + background_inputs
    st.session_state["new_storyline_column"] = [timestamp] + result.splitlines()
    st.session_state["story_generated"] = True

# === Download Buttons
def prepend_column_to_transposed_file(file_text, new_column):
    rows = [line.split(",") for line in file_text.splitlines()] if file_text else []
    while len(rows) < len(new_column):
        rows.append([])
    for i, value in enumerate(new_column):
        rows[i].insert(1, f'"{value}"')
    return "\n".join([",".join(row) for row in rows])

if st.session_state.get("story_generated"):
    st.download_button("⬇️ Save Updated Voice Input",
        data=prepend_column_to_transposed_file(st.session_state["voice_file_data"], st.session_state["new_voice_column"]),
        file_name="voice_input.txt", mime="text/plain")

    st.download_button("⬇️ Save Updated Background",
        data=prepend_column_to_transposed_file(st.session_state["background_file_data"], st.session_state["new_background_column"]),
        file_name="background.txt", mime="text/plain")

    st.download_button("⬇️ Save New Storyline",
        data=prepend_column_to_transposed_file(st.session_state["storyline_file_data"], st.session_state["new_storyline_column"]),
        file_name="storyline.txt", mime="text/plain")

# === TESTING BLOCK: Session Log Viewer ===
if st.sidebar.checkbox("📂 View Session Log"):
    try:
        log_df = pd.read_csv(CLASSIFICATION_LOG_PATH)
        st.subheader("📊 Session Log")
        st.dataframe(log_df)
    except Exception as e:
        st.error(f"⚠️ Failed to load session log: {e}")

# === TESTING BLOCK: Reflex Manifest Preview ===
if st.sidebar.checkbox("🧠 Preview Reflex Manifest"):
    try:
        manifest_df = pd.read_csv(TRANSMISSION_MAP_PATH)










