import streamlit as st
import pandas as pd
import io
import requests
from datetime import datetime
from io import StringIO

# === Constants ===
FLASK_URL = "https://49cbb7bc0425.ngrok-free.app/generate"
VOICE_FIELDS = 4
BACKGROUND_FIELDS = 5
DELIMITER = ","
EXPECTED_FILES = ["voice_input", "background"]

# === Load header labels ===
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"

@st.cache_data
def load_headers():
    try:
        response = requests.get(HEADERS_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=DELIMITER, quotechar='"', engine="python")
        return df
    except Exception as e:
        st.warning(f"⚠️ Could not load headers.csv: {e}")
        return pd.DataFrame(columns=["Input_file", "Field", "Label"])

headers_df = load_headers()
voice_labels = headers_df[headers_df["Input_file"] == "voice_input"]["Label"].tolist()
background_labels = headers_df[headers_df["Input_file"] == "background"]["Label"].tolist()

# === Page Setup ===
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.title("🧠 Dual Narrative Emotional OS")

# === Sidebar Uploads ===
st.sidebar.title("📁 Upload Previous Session Files")
uploaded_files = st.sidebar.file_uploader("Upload voice_input.csv and background.csv", type="csv", accept_multiple_files=True)
prefill_toggle = st.sidebar.checkbox("Prefill with uploaded session")

# === Parse Uploaded Files ===
inputs = {}
if uploaded_files:
    for file in uploaded_files:
        key = file.name.replace(".csv", "").replace(" (2)", "").replace(" (3)", "")
        df = pd.read_csv(file, header=None)
        inputs[key] = df

# === Input Fields ===
st.subheader("🗣️ Voice Input (Conflict)")
voice_inputs = []
for i, label in enumerate(voice_labels):
    default_value = ""
    if prefill_toggle and "voice_input" in inputs and i + 1 < len(inputs["voice_input"]):
        default_value = inputs["voice_input"].iloc[i + 1, 0]
    voice_inputs.append(st.text_area(label, value=default_value, key=f"voice_{i}"))

st.subheader("🌄 Background Input (Wheel Context)")
background_inputs = []
for i, label in enumerate(background_labels):
    default_value = ""
    if prefill_toggle and "background" in inputs and i + 1 < len(inputs["background"]):
        default_value = inputs["background"].iloc[i + 1, 0]
    background_inputs.append(st.text_area(label, value=default_value, key=f"background_{i}"))

# === Generate Narrative ===
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
            st.subheader("📜 Generated Storyline")
            st.text_area("Scroll through your story:", value=result, height=400)

            # === Build new columns ===
            session_label = datetime.now().strftime("%a %b %d, %Y (%H:%M)")
            voice_column = [session_label] + voice_inputs
            background_column = [session_label] + background_inputs

            # === Append to inputs ===
            for key, column_data in zip(EXPECTED_FILES, [voice_column, background_column]):
                if key in inputs and not inputs[key].empty:
                    if inputs[key].shape[1] == 1:
                        inputs[key].columns = ["Initial"]
                    inputs[key][session_label] = pd.Series(column_data)
                else:
                    df = pd.DataFrame(column_data)
                    df.columns = ["Initial"]
                    df[session_label] = pd.Series(column_data)
                    inputs[key] = df

            # === Save storyline ===
            if "story_output" not in st.session_state:
                st.session_state["story_output"] = pd.DataFrame()
            story_df = pd.DataFrame([result], columns=[session_label])
            st.session_state["story_output"] = pd.concat([st.session_state["story_output"], story_df], axis=1)

        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"⚠️ Failed to connect to Flask backend: {e}")

# === Download Buttons ===
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

if "story_output" in st.session_state and not st.session_state["story_output"].empty:
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

# === Session History Viewer ===
st.subheader("🕰️ Browse Past Story Sessions")
if "story_output" in st.session_state and not st.session_state["story_output"].empty:
    selected_col = st.selectbox(
        "Select a session to view its storyline",
        st.session_state["story_output"].columns[::-1]
    )
    st.text_area("Storyline Preview", st.session_state["story_output"][selected_col].iloc[0], height=300)






