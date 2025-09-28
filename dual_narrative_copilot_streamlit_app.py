import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# === Constants ===
FLASK_URL = "https://bbb6463372d3.ngrok-free.app/generate"  # Replace with your live ngrok URL
VOICE_FIELDS = 4
BACKGROUND_FIELDS = 5
DELIMITER = ","

# === File Uploads ===
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.sidebar.title("📁 Upload Files")

voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
storyline_file = st.sidebar.file_uploader("Upload storyline.csv", type="csv")

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
    voice_inputs[i] = st.text_input(f"Voice Input {i+1}", value=voice_inputs[i])

st.subheader("🌄 Background Input (Wheel Context)")
for i in range(BACKGROUND_FIELDS):
    background_inputs[i] = st.text_input(f"Background Input {i+1}", value=background_inputs[i])

actor = st.selectbox("🎭 Actor Perspective", ["User", "Partner"])
user_id = st.text_input("🆔 Session ID", value="session_001")

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

            def append_column_csv(original_file, new_column):
                try:
                    df = pd.read_csv(original_file, sep=DELIMITER, quotechar='"', engine="python")
                except:
                    df = pd.DataFrame()
                while len(df) < len(new_column) - 1:
                    df.loc[len(df)] = ["" for _ in range(len(df.columns))]
                df[timestamp] = new_column[1:]
                return df.to_csv(index=False, sep=DELIMITER, quotechar='"')

            updated_voice = append_column_csv(voice_file, new_voice_column) if voice_file else ""
            updated_background = append_column_csv(background_file, new_background_column) if background_file else ""

            storyline_df = pd.DataFrame()
            storyline_df[timestamp] = new_storyline_column[1:]
            updated_storyline = storyline_df.to_csv(index=False, sep=DELIMITER, quotechar='"')

            st.download_button("⬇️ Save Updated Voice Input", data=updated_voice, file_name="voice_input.csv", mime="text/csv")
            st.download_button("⬇️ Save Updated Background", data=updated_background, file_name="background.csv", mime="text/csv")
            st.download_button("⬇️ Save New Storyline", data=updated_storyline, file_name="storyline.csv", mime="text/csv")

        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Failed to connect to Flask backend: {e}")

