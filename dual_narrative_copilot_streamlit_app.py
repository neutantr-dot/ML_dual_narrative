import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# === Constants ===
FLASK_URL = "https://49cbb7bc0425.ngrok-free.app/generate"
VOICE_FIELDS = 4
BACKGROUND_FIELDS = 5
DELIMITER = ","

# === File Uploads ===
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.sidebar.title("📁 Upload Files")

voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
storyline_file = st.sidebar.file_uploader("Upload storyline.csv", type="csv")

# === Parse CSVs and extract first column ===
def extract_first_column(file_obj, expected_fields):
    if not file_obj:
        return [""] * expected_fields
    try:
        df = pd.read_csv(file_obj, sep=DELIMITER, quotechar='"', engine="python", header=None)
        first_col = df.iloc[1:expected_fields+1, 0].fillna("").tolist()
        return first_col
    except Exception as e:
        st.warning(f"⚠️ Could not parse CSV: {e}")
        return [""] * expected_fields

voice_inputs = extract_first_column(voice_file, VOICE_FIELDS)
background_inputs = extract_first_column(background_file, BACKGROUND_FIELDS)

# === Input Fields ===
st.title("🧠 Dual Narrative Emotional OS")

st.subheader("🗣️ Voice Input (Conflict)")
for i in range(VOICE_FIELDS):
    voice_inputs[i] = st.text_input(f"Voice Input {i+1}", value=voice_inputs[i], key=f"voice_{i}")

st.subheader("🌄 Background Input (Wheel Context)")
for i in range(BACKGROUND_FIELDS):
    background_inputs[i] = st.text_input(f"Background Input {i+1}", value=background_inputs[i], key=f"background_{i}")

# === Generate Narrative ===
if "story_generated" not in st.session_state:
    st.session_state.story_generated = False

if st.button("✨ Generate Dual Narrative"):
    payload = {
        "voice_inputs": voice_inputs,
        "background_inputs": background_inputs,
        "actor": "Partner",
        "user_id": "owner"
    }

    try:
        response = requests.post(FLASK_URL, json=payload)
        if response.status_code == 200:
            result = response.json().get("result", "[No response]")
            st.session_state.story_generated = True
            st.session_state.story_text = result
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Failed to connect to Flask backend: {e}")

# === Show Storyline if generated ===
if st.session_state.story_generated:
    st.subheader("📜 Generated Storyline")
    st.text_area("Scroll through your story:", value=st.session_state.story_text, height=400)







