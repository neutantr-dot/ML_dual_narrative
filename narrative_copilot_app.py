import streamlit as st
import pandas as pd
from datetime import datetime
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

# --- Load Uploaded Files or Initialize ---
df_voice = pd.read_csv(uploaded_voice) if uploaded_voice else pd.DataFrame(index=range(len(voice_labels)))
df_background = pd.read_csv(uploaded_background) if uploaded_background else pd.DataFrame(index=range(len(background_labels)))
df_story = pd.read_csv(uploaded_story) if uploaded_story else pd.DataFrame(index=[0])

# --- Prefetch Logic ---
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

    # Insert new column at position 0 (first column)
    df_voice.insert(0, session_name, voice_inputs)
    df_background.insert(0, session_name, background_inputs)

    # Run ML engine
    inputs = {
        "voice_input": pd.DataFrame([[v] for v in voice_inputs]),
        "background": pd.DataFrame([[b] for b in background_inputs]),
        "clarification": "User clarification embedded in inputs"
    }
    story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")

    df_story.insert(0, session_name, [story_output])

    # Save updated CSVs
    df_voice.to_csv("voice_input.csv", index=False, encoding="utf-8")
    df_background.to_csv("background.csv", index=False, encoding="utf-8")
    df_story.to_csv("story_output.csv", index=False, encoding="utf-8")

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
















