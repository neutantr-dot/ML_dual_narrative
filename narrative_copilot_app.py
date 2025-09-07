import streamlit as st
import pandas as pd
from datetime import datetime
import io
from dispatcher import orchestrate_story  # Your ML engine

# --- Load Header Labels ---
headers_df = pd.read_csv("headers.csv", sep=";")
voice_labels = headers_df[headers_df["InputSet"] == 1].reset_index(drop=True)
background_labels = headers_df[headers_df["InputSet"] == 2].reset_index(drop=True)

# --- Sidebar Upload ---
st.sidebar.header("Upload Previous Session Files")
uploaded_voice = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
uploaded_background = st.sidebar.file_uploader("Upload background.csv", type="csv")
uploaded_story = st.sidebar.file_uploader("Upload story_output.csv", type="csv")

# --- Input Mode Toggle ---
st.sidebar.markdown("---")
input_mode = st.sidebar.radio("Input Mode", ["Start Fresh", "Edit Last Session"])

# --- Optional Reset Button ---
if st.sidebar.button("🔄 Reset Session"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.experimental_rerun()

# --- Load Uploaded Files into session_state ONCE ---
if uploaded_voice and "voice_input" not in st.session_state:
    st.session_state["voice_input"] = pd.read_csv(uploaded_voice, index_col=0)
if uploaded_background and "background" not in st.session_state:
    st.session_state["background"] = pd.read_csv(uploaded_background, index_col=0)
if uploaded_story and "story_output" not in st.session_state:
    st.session_state["story_output"] = pd.read_csv(uploaded_story)

# --- Initialize if not uploaded ---
if "voice_input" not in st.session_state:
    st.session_state["voice_input"] = pd.DataFrame(index=voice_labels["Field"])
if "background" not in st.session_state:
    st.session_state["background"] = pd.DataFrame(index=background_labels["Field"])
if "story_output" not in st.session_state:
    st.session_state["story_output"] = pd.DataFrame()

# --- Use session_state DataFrames ---
df_voice = st.session_state["voice_input"]
df_background = st.session_state["background"]
df_story = st.session_state["story_output"]

# --- Prefetch Logic (pull latest column) ---
latest_voice = (
    df_voice.iloc[:, -1].fillna("").astype(str).tolist()
    if input_mode == "Edit Last Session" and not df_voice.empty and df_voice.shape[1] > 0
    else [""] * len(voice_labels)
)

latest_background = (
    df_background.iloc[:, -1].fillna("").astype(str).tolist()
    if input_mode == "Edit Last Session" and not df_background.empty and df_background.shape[1] > 0
    else [""] * len(background_labels)
)

# --- App Title ---
st.title("🧠 Narrative Copilot")

# --- Voice Input Section ---
st.header("Clarify Your Voice Inputs")
voice_inputs = []
for i, row in voice_labels.iterrows():
    val = st.text_input(row["Label"], value=latest_voice[i], key=f"voice_{row['Field']}")
    voice_inputs.append(val)

# --- Background Input Section ---
st.header("Background Context")
background_inputs = []
for i, row in background_labels.iterrows():
    val = st.text_input(row["Label"], value=latest_background[i], key=f"background_{row['Field']}")
    background_inputs.append(val)

# --- Generate Button ---
if all(voice_inputs + background_inputs) and st.button("Generate Storyline"):
    session_name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Insert new session as column
    df_voice[session_name] = pd.Series(voice_inputs, index=voice_labels["Field"])
    df_background[session_name] = pd.Series(background_inputs, index=background_labels["Field"])

    # Run ML engine
    inputs = {
        "voice_input": pd.DataFrame([[v] for v in voice_inputs]),
        "background": pd.DataFrame([[b] for b in background_inputs]),
        "clarification": "User clarification embedded in inputs"
    }
    story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")

    # Append story output
    df_story[session_name] = pd.Series([story_output])

    # Update session_state
    st.session_state["voice_input"] = df_voice
    st.session_state["background"] = df_background
    st.session_state["story_output"] = df_story

    st.success("✅ Storyline generated successfully!")
    st.text_area("Generated Storyline", story_output, height=400)

# --- History Viewers ---
if not df_story.empty:
    st.subheader("🕰️ Browse Past Story Sessions")
    selected_col = st.selectbox("Select a session to view its storyline", df_story.columns)
    st.text_area("Storyline Preview", str(df_story[selected_col].iloc[0]), height=300)

if not df_voice.empty:
    st.subheader("📜 Browse Past Voice Inputs")
    selected_col = st.selectbox("Select a session from voice_input.csv", df_voice.columns)
    st.text_area("Voice Input", "\n".join(df_voice[selected_col].dropna().astype(str)), height=150)

if not df_background.empty:
    st.subheader("📘 Browse Past Background Inputs")
    selected_col = st.selectbox("Select a session from background.csv", df_background.columns)
    st.text_area("Background Input", "\n".join(df_background[selected_col].dropna().astype(str)), height=150)

# --- Download Buttons ---
buffer_voice = io.StringIO()
buffer_background = io.StringIO()
buffer_story = io.StringIO()

df_voice.to_csv(buffer_voice, encoding="utf-8")
df_background.to_csv(buffer_background, encoding="utf-8")
df_story.to_csv(buffer_story, index=False, encoding="utf-8")

buffer_voice.seek(0)
buffer_background.seek(0)
buffer_story.seek(0)

st.subheader("📥 Download Your Updated Files")
st.download_button("Download voice_input.csv", buffer_voice.getvalue(), "voice_input.csv", "text/csv", key="download_voice")
st.download_button("Download background.csv", buffer_background.getvalue(), "background.csv", "text/csv", key="download_background")
st.download_button("Download story_output.csv", buffer_story.getvalue(), "story_output.csv", "text/csv", key="download_story")



