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

# === header.csv upload ===
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"

@st.cache_data
def load_headers():
    try:
        response = requests.get(HEADERS_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=DELIMITER, quotechar='"', engine="python")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load headers.csv: {e}")
        return pd.DataFrame(columns=["Input_file", "Field", "Label"])

headers_df = load_headers()

# === File Uploads ===
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.sidebar.title("📁 Upload Files")

voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
storyline_file = st.sidebar.file_uploader("Upload storyline.csv", type="csv")

def load_full_dataframe(file_obj):
    try:
        return pd.read_csv(file_obj, sep=DELIMITER, quotechar='"', engine="python")
    except:
        return pd.DataFrame()

# === Initialize session memory from uploaded files ===
if "voice_df" not in st.session_state:
    st.session_state.voice_df = load_full_dataframe(voice_file)

if "background_df" not in st.session_state:
    st.session_state.background_df = load_full_dataframe(background_file)

if "storyline_df" not in st.session_state:
    st.session_state.storyline_df = load_full_dataframe(storyline_file)

def parse_csv_file(file_obj, expected_fields):
    if not file_obj:
        return [""] * expected_fields, []
    try:
        df = pd.read_csv(file_obj, sep=DELIMITER, quotechar='"', engine="python")
        versions = list(df.columns)
        latest = df[versions[-1]].fillna("").tolist()
        return latest[:expected_fields], versions
    except Exception as e:
        st.warning(f"⚠️ Could not parse CSV: {e}")
        return [""] * expected_fields, []

voice_inputs, voice_versions = parse_csv_file(voice_file, VOICE_FIELDS)
background_inputs, background_versions = parse_csv_file(background_file, BACKGROUND_FIELDS)
storyline_text = storyline_file.getvalue().decode("utf-8") if storyline_file else ""

# === Input Fields ===
st.title("🧠 Dual Narrative Emotional OS")

st.subheader("🗣️ Voice Input (Conflict)")
for i in range(VOICE_FIELDS):
    label_row = headers_df[
        (headers_df["Input_file"] == "voice_input") &
        (headers_df["Field"] == f"input{i+1}")
    ]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Voice Input {i+1}"
    voice_inputs[i] = st.text_input(label_text, value=voice_inputs[i])

st.subheader("🌄 Background Input (Wheel Context)")
for i in range(BACKGROUND_FIELDS):
    label_row = headers_df[
        (headers_df["Input_file"] == "background") &
        (headers_df["Field"] == f"input{i+1}")
    ]
    label_text = label_row["Label"].values[0] if not label_row.empty else f"Background Input {i+1}"
    background_inputs[i] = st.text_input(label_text, value=background_inputs[i])

# Hardcoded for testing phase
actor = "Partner"
user_id = "owner"

# === Generate Narrative ===
if st.button("✨ Generate Dual Narrative"):
    payload = {
        "voice_inputs": voice_inputs,
        "background_inputs": background_inputs,
        "actor": actor,
        "user_id": user_id
    }

    try:
        response = requests.post(FLASK_URL, json=payload)
        if response.status_code == 200:
            result = response.json().get("result", "[No response]")
            st.subheader("📜 Generated Storyline")
            st.text_area("Scroll through your story:", value=result, height=400)

            timestamp = datetime.now().strftime("%a %b %d, %Y (%H:%M)")
            new_voice_column = [timestamp] + voice_inputs
            new_background_column = [timestamp] + background_inputs
            new_storyline_column = [timestamp] + result.splitlines()

            def append_column(df, new_column):
                required_rows = len(new_column) - 1
                if df.empty:
                    df = pd.DataFrame(index=range(required_rows))
                elif len(df) < required_rows:
                    for _ in range(required_rows - len(df)):
                        df.loc[len(df)] = ["" for _ in range(len(df.columns))]
                df[timestamp] = new_column[1:]
                return df

            st.session_state.voice_df = append_column(st.session_state.voice_df, new_voice_column)
            st.session_state.background_df = append_column(st.session_state.background_df, new_background_column)
            st.session_state.storyline_df = append_column(st.session_state.storyline_df, new_storyline_column)

            st.session_state.updated_voice = st.session_state.voice_df.to_csv(index=False, sep=DELIMITER, quotechar='"')
            st.session_state.updated_background = st.session_state.background_df.to_csv(index=False, sep=DELIMITER, quotechar='"')
            st.session_state.updated_storyline = st.session_state.storyline_df.to_csv(index=False, sep=DELIMITER, quotechar='"')

        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Failed to connect to Flask backend: {e}")

# === Persistent Download Buttons ===
if "updated_voice" in st.session_state:
    st.download_button("⬇️ Save Updated Voice Input", data=st.session_state.updated_voice, file_name="voice_input.csv", mime="text/csv")

if "updated_background" in st.session_state:
    st.download_button("⬇️ Save Updated Background", data=st.session_state.updated_background, file_name="background.csv", mime="text/csv")

if "updated_storyline" in st.session_state:
    st.download_button("⬇️ Save New Storyline", data=st.session_state.updated_storyline, file_name="storyline.csv", mime="text/csv")




