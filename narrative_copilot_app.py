import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import io

# Load headers from GitHub
headers_url = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
headers_response = requests.get(headers_url)
headers_df = pd.read_csv(io.StringIO(headers_response.text), delimiter="|", header=None)

# Sidebar
st.sidebar.title("📂 File Upload")
voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
story_file = st.sidebar.file_uploader("Upload story_line.csv", type="csv")

session_mode = st.sidebar.radio("Session Mode", ["🆕 Fresh Start", "📜 Fetch Last"])

# Main UI
st.title("🧠 Dual Narrative ML Story Generator")

# Input Fields
st.subheader("🎙️ Voice Input")
voice_inputs = {}
voice_labels = ["Inner Voice", "Self Voice", "Partner Voice", "Location"]
for label in voice_labels:
    voice_inputs[label] = st.text_input(label)

st.subheader("🌐 Background Input")
background_inputs = {}
background_labels = ["Work Related", "Money/Time Related", "Ambition/Free Time", "Feeling Related", "Overall Well-being"]
for label in background_labels:
    background_inputs[label] = st.text_input(label)

# Generate Story
if st.button("✨ Generate Story"):
    dateversion = datetime.now().strftime("%a, %b %d, %Y (1)")
    
    # Combine inputs
    input_data = {**voice_inputs, **background_inputs}
    input_df = pd.DataFrame([input_data])
    input_df.insert(0, "DateVersion", dateversion)

    # Placeholder ML story generation
    story_text = f"On {dateversion}, a narrative unfolds where {voice_inputs['Inner Voice']} meets ambition and {background_inputs['Feeling Related']} in the heart of {voice_inputs['Location']}."
    story_df = pd.DataFrame([[dateversion, story_text]], columns=["DateVersion", "Story"])

    # Display story
    st.subheader("📖 Generated Story")
    st.write(story_text)

    # Append history (shift columns right)
    if voice_file:
        old_voice_df = pd.read_csv(voice_file, delimiter="|", header=None)
        voice_history = pd.concat([input_df, old_voice_df], axis=1)
        st.download_button("⬇️ Download Updated Voice Input", voice_history.to_csv(sep="|", index=False), "updated_voice_input.csv")

    if background_file:
        old_background_df = pd.read_csv(background_file, delimiter="|", header=None)
        background_history = pd.concat([input_df, old_background_df], axis=1)
        st.download_button("⬇️ Download Updated Background Input", background_history.to_csv(sep="|", index=False), "updated_background.csv")

    if story_file:
        old_story_df = pd.read_csv(story_file, delimiter="|", header=None)
        story_history = pd.concat([story_df, old_story_df], axis=1)
        st.download_button("⬇️ Download Updated Story Output", story_history.to_csv(sep="|", index=False), "updated_story_line.csv")





 



