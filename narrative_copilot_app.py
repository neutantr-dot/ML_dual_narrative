import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Constants
GITHUB_HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
DELIMITER = "|"

# Load headers from GitHub
@st.cache_data
def load_headers():
    try:
        response = requests.get(GITHUB_HEADERS_URL)
        response.raise_for_status()
        headers_df = pd.read_csv(StringIO(response.text))
        return headers_df.iloc[0].tolist()
    except Exception as e:
        st.warning("Failed to load headers from GitHub.")
        return ["inner_voice", "self_voice", "partner_voice", "location",
                "work_related", "money_time_related", "ambition_related",
                "feeling_related", "overall_wellbeing"]

# Sidebar
st.sidebar.title("🧭 Navigation")
fresh_start = st.sidebar.toggle("Fresh Start", value=True)
voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
story_file = st.sidebar.file_uploader("Upload story_line.csv", type="csv")

# Load headers
headers = load_headers()

# Prefill logic
voice_inputs = [""] * 4
background_inputs = [""] * 5

if not fresh_start and voice_file and background_file:
    voice_df = pd.read_csv(voice_file, delimiter=DELIMITER, header=None)
    background_df = pd.read_csv(background_file, delimiter=DELIMITER, header=None)
    voice_inputs = voice_df.iloc[1:5, 0].tolist()
    background_inputs = background_df.iloc[1:6, 0].tolist()

# Main UI
st.title("🎙️ ML Dual Narrative Generator")

st.subheader("Voice Inputs")
voice_inputs[0] = st.text_input(headers[0], value=voice_inputs[0])
voice_inputs[1] = st.text_input(headers[1], value=voice_inputs[1])
voice_inputs[2] = st.text_input(headers[2], value=voice_inputs[2])
voice_inputs[3] = st.text_input(headers[3], value=voice_inputs[3])

st.subheader("Background Inputs")
background_inputs[0] = st.text_input(headers[4], value=background_inputs[0])
background_inputs[1] = st.text_input(headers[5], value=background_inputs[1])
background_inputs[2] = st.text_input(headers[6], value=background_inputs[2])
background_inputs[3] = st.text_input(headers[7], value=background_inputs[3])
background_inputs[4] = st.text_input(headers[8], value=background_inputs[4])

# Generate story
def generate_story(voice, background):
    # Placeholder ML logic
    return f"On {datetime.now().strftime('%a, %b %d, %Y')}, a story unfolds:\n" + \
           f"Inner thoughts: {voice[0]}. Self-reflection: {voice[1]}. " + \
           f"Partner's voice: {voice[2]}. Location: {voice[3]}. " + \
           f"Work: {background[0]}, Money/Time: {background[1]}, " + \
           f"Ambition: {background[2]}, Feelings: {background[3]}, " + \
           f"Well-being: {background[4]}."

if st.button("Generate Story"):
    story = generate_story(voice_inputs, background_inputs)
    st.subheader("📘 Generated Story")
    st.text_area("Story Output", story, height=300)

    # Prepare output file
    output_df = pd.DataFrame([[datetime.now().strftime('%a, %b %d, %Y'), story]])
    st.download_button("Download story_line.csv", output_df.to_csv(sep=DELIMITER, index=False), "story_line.csv")

    # Append logic for input files
    voice_appended = pd.DataFrame([[datetime.now().strftime('%a, %b %d, %Y')] + voice_inputs])
    background_appended = pd.DataFrame([[datetime.now().strftime('%a, %b %d, %Y')] + background_inputs])

    st.download_button("Download updated voice_input.csv", voice_appended.to_csv(sep=DELIMITER, index=False), "voice_input.csv")
    st.download_button("Download updated background.csv", background_appended.to_csv(sep=DELIMITER, index=False), "background.csv")







 



