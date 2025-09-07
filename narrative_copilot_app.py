import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Constants
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
NGROK_API_URL = "https://your-ngrok-url.ngrok.io/generate_story"  # Replace with your actual ngrok endpoint
DATEVERSION = "Sun, Sept 7, 2025"

# Load headers from GitHub
@st.cache_data
def load_headers():
    return pd.read_csv(HEADERS_URL, delimiter="|", header=None)

# Load uploaded CSVs
def load_csv(file, delimiter="|"):
    return pd.read_csv(file, delimiter=delimiter, index_col=0)

# Append new column to left
def append_column(df, new_data, col_name):
    df.insert(0, col_name, new_data)
    return df

# UI Layout
st.set_page_config(page_title="Dual Narrative Generator", layout="wide")
st.title("🧠 ML Dual Narrative Generator")

# Sidebar
st.sidebar.header("📁 File Uploads")
voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
bg_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
story_file = st.sidebar.file_uploader("Upload story_line.csv", type="csv")

mode = st.sidebar.radio("Start Mode", ["Fresh Start", "Fetch Last Used"])

# Load headers
headers_df = load_headers()
voice_labels = headers_df.iloc[:4, 0].tolist()
bg_labels = headers_df.iloc[4:, 0].tolist()

# Voice Input Section
st.subheader("🎙️ Voice Input")
voice_inputs = [""] * 4
if voice_file:
    voice_df = load_csv(voice_file)
    if mode == "Fetch Last Used":
        voice_inputs = voice_df.iloc[:, 0].tolist()

new_voice = []
for i, label in enumerate(voice_labels):
    val = st.text_input(label, value=voice_inputs[i] if i < len(voice_inputs) else "")
    new_voice.append(val)

# Background Input Section
st.subheader("🌍 Background Input")
bg_inputs = [""] * 5
if bg_file:
    bg_df = load_csv(bg_file)
    if mode == "Fetch Last Used":
        bg_inputs = bg_df.iloc[:, 0].tolist()

new_bg = []
for i, label in enumerate(bg_labels):
    val = st.text_input(label, value=bg_inputs[i] if i < len(bg_inputs) else "")
    new_bg.append(val)

# Submit to ML model
if st.button("Generate Story"):
    payload = {
        "voice_input": new_voice,
        "background_input": new_bg
    }
    try:
        response = requests.post(NGROK_API_URL, json=payload)
        response.raise_for_status()
        story_text = response.json().get("story", "")
        st.success("✅ Story Generated")
        st.text_area("📖 Story Output", story_text, height=300)

        # Append to story file
        if story_file:
            story_df = load_csv(story_file)
        else:
            story_df = pd.DataFrame()

        story_df = append_column(story_df, [story_text], DATEVERSION)
        st.download_button("⬇️ Download Updated Story File", story_df.to_csv(sep="|"), file_name="story_line.csv")

        # Append to input files
        if voice_file:
            voice_df = load_csv(voice_file)
            voice_df = append_column(voice_df, new_voice, DATEVERSION)
            st.download_button("⬇️ Download Updated Voice File", voice_df.to_csv(sep="|"), file_name="voice_input.csv")

        if bg_file:
            bg_df = load_csv(bg_file)
            bg_df = append_column(bg_df, new_bg, DATEVERSION)
            st.download_button("⬇️ Download Updated Background File", bg_df.to_csv(sep="|"), file_name="background.csv")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to generate story: {e}")










 



