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

# --- Initialize or Load DataFrames into session_state ---
if "voice_input" not in st.session_state:
    if uploaded_voice:
        st.session_state["voice_input"] = pd.read_csv(uploaded_voice)
    else:
        st.session_state["voice_input"] = pd.DataFrame(index=range(len(voice_labels)))

if "background" not in st.session_state:
    if uploaded_background:
        st.session_state["background"] = pd.read_csv(uploaded_background)
    else:
        st.session_state["background"] = pd.DataFrame(index=range(len(background_labels)))

if "story_output" not in st.session_state:
    if uploaded_story:
        st.session_state["story_output"] = pd.read_csv(uploaded_story)
    else:
        st.session_state["story_output"] = pd.DataFrame(index=[0])

df_voice = st.session_state["voice_input"]
df_background = st.session_state["background"]
df_story = st.session_state["story_output"]

# --- Prefetch Logic (from first column) ---
latest_voice = df_voice.iloc[:, 0].fillna("").astype(str).tolist() if input_mode == "Edit Last Session" and not df_voice.empty else [""] * len(voice_labels)
latest_background = df_background.iloc[:, 0].fillna("").astype(str).tolist() if input_mode == "Edit Last Session" and not df_background.empty else [""] * len(background_labels)

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
    session_date = datetime.now().strftime("%a, %b %d, %Y")
    session_name = f"Session {session_date}"

    # Ensure correct shape before inserting
    if df_voice.shape[0] != len(voice_inputs):
        df_voice = pd.DataFrame(index=range(len(voice_inputs)))
    df_voice.insert(0, session_name, voice_inputs)

    if df_background.shape[0] != len(background_inputs):
        df_background = pd.DataFrame(index=range(len(background_inputs)))
    df_background.insert(0, session_name, background_inputs)

    if df_story.shape[0] != 1:
        df_story = pd.DataFrame(index=[0])

    # Run ML engine
    inputs = {
        "voice_input": pd.DataFrame([[v] for v in voice_inputs]),
        "background": pd.DataFrame([[b] for b in background_inputs]),
        "clarification": "User clarification embedded in inputs"
    }
    story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")
    df_story.insert(0, session_name, [story_output])

    # Update session state
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

st.session_state["voice_input"].to_csv(buffer_voice, index=False, encoding="utf-8")
st.session_state["background"].to_csv(buffer_background, index=False, encoding="utf-8")
st.session_state["story_output"].to_csv(buffer_story, index=False, encoding="utf-8")

buffer_voice.seek(0)
buffer_background.seek(0)
buffer_story.seek(0)

st.subheader("📥 Download Your Updated Files")
st.download_button("Download voice_input.csv", buffer_voice.getvalue(), "voice_input.csv", "text/csv", key="download_voice")
st.download_button("Download background.csv", buffer_background.getvalue(), "background.csv", "text/csv", key="download_background")
st.download_button("Download story_output.csv", buffer_story.getvalue(), "story_output.csv", "text/csv", key="download_story")
