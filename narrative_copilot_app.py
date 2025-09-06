import streamlit as st
import pandas as pd
import io
from datetime import datetime
from dispatcher import orchestrate_story  # Your ML engine

# --- Initialize Session ---
if "initialized" not in st.session_state:
    st.session_state.clear()
    st.session_state["initialized"] = True

# --- Load Header Labels ---
headers_df = pd.read_csv("headers.csv", sep=";")
voice_labels = headers_df[headers_df["InputSet"] == 1].reset_index(drop=True)
background_labels = headers_df[headers_df["InputSet"] == 2].reset_index(drop=True)

# --- Sidebar Upload ---
st.sidebar.header("Upload Previous Session Files")
uploaded_voice = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
uploaded_background = st.sidebar.file_uploader("Upload background.csv", type="csv")
uploaded_story = st.sidebar.file_uploader("Upload story_output.csv", type="csv")

# --- Load Uploaded or Fallback ---
df_voice = pd.read_csv(uploaded_voice) if uploaded_voice else pd.DataFrame()
df_background = pd.read_csv(uploaded_background) if uploaded_background else pd.DataFrame()
df_story = pd.read_csv(uploaded_story) if uploaded_story else pd.DataFrame(index=[0])

# --- Input Mode Toggle ---
st.sidebar.markdown("---")
input_mode = st.sidebar.radio("Input Mode", ["Start Fresh", "Edit Last Session"])

# --- Prefill Logic ---
if input_mode == "Edit Last Session" and not df_voice.empty and not df_background.empty:
    if not df_voice.empty and df_voice.shape[0] >= len(voice_labels):
        latest_voice = df_voice.iloc[:, -1].fillna("").tolist()
    if not df_background.empty and df_background.shape[0] >= len(background_labels):
        latest_background = df_background.iloc[:, -1].fillna("").tolist()
else:
    latest_voice = [""] * len(voice_labels)
    latest_background = [""] * len(background_labels)

# --- App Title ---
st.title("🧠 Narrative Copilot")

# --- Voice Input Section ---
st.header("Clarify Your Voice Inputs")
voice_inputs = []
for i, row in voice_labels.iterrows():
    default_val = latest_voice[i] if i < len(latest_voice) else ""
    val = st.text_input(row["Label"], value=default_val, key=row["Field"])
    voice_inputs.append(val)

# --- Background Input Section ---
st.header("Background Context")
background_inputs = []
for i, row in background_labels.iterrows():
    default_val = latest_background[i] if i < len(latest_background) else ""
    val = st.text_input(row["Label"], value=default_val, key=row["Field"])
    background_inputs.append(val)

# --- Generate Button ---
inputs_filled = all(voice_inputs + background_inputs)

if inputs_filled:
    if st.button("Generate Storyline"):
        session_date = datetime.now().strftime("%a, %b %d, %Y")

        def count_existing(df, base_date):
            return sum([1 for col in df.columns if str(col).startswith(f"Session {base_date}")])

        count_voice = count_existing(df_voice, session_date) + 1
        count_background = count_existing(df_background, session_date) + 1
        count_story = count_existing(df_story, session_date) + 1

        col_voice = f"Session {session_date} ({count_voice})"
        col_background = f"Session {session_date} ({count_background})"
        col_story = f"Session {session_date} ({count_story})"

        # Append new columns
        new_voice = pd.Series(voice_inputs, name=col_voice)
        new_background = pd.Series(background_inputs, name=col_background)

        df_voice = pd.concat([df_voice, new_voice], axis=1)
        df_background = pd.concat([df_background, new_background], axis=1)

        # Run ML engine
        inputs = {
            "voice_input": pd.DataFrame([[v] for v in voice_inputs]),
            "background": pd.DataFrame([[b] for b in background_inputs]),
            "clarification": "User clarification embedded in inputs"
        }
        story_output = orchestrate_story(inputs, config_path="copilot_config.yaml")

        new_story = pd.Series([story_output], name=col_story)
        df_story = pd.concat([df_story, new_story], axis=1)

        # Save updated CSVs
        df_voice.to_csv("voice_input.csv", index=False, encoding="utf-8")
        df_background.to_csv("background.csv", index=False, encoding="utf-8")
        df_story.to_csv("story_output.csv", index=False, encoding="utf-8")

        # Store in session
        st.session_state["voice_input"] = df_voice
        st.session_state["background"] = df_background
        st.session_state["story_output"] = df_story

        st.success("✅ Storyline generated successfully!")
        st.text_area("Generated Storyline", story_output, height=400)

# --- History Viewers ---
if not df_story.empty:
    st.subheader("🕰️ Browse Past Story Sessions")
    selected_col = st.selectbox("Select a session to view its storyline", df_story.columns[::-1])
    st.text_area("Storyline Preview", df_story[selected_col].iloc[0], height=300)

if not df_voice.empty:
    st.subheader("📜 Browse Past Voice Inputs")
    selected_col = st.selectbox("Select a session from voice_input.csv", df_voice.columns[::-1])
    st.text_area("Voice Input", "\n".join(df_voice[selected_col].dropna().astype(str)), height=150)

if not df_background.empty:
    st.subheader("📘 Browse Past Background Inputs")
    selected_col = st.selectbox("Select a session from background.csv", df_background.columns[::-1])
    st.text_area("Background Input", "\n".join(df_background[selected_col].dropna().astype(str)), height=150)

# --- Download Buttons ---
if "voice_input" in st.session_state and "background" in st.session_state and "story_output" in st.session_state:
    buffer_voice = io.StringIO()
    buffer_background = io.StringIO()
    buffer_story = io.StringIO()
    st.session_state["voice_input"].to_csv(buffer_voice, index=False)
    st.session_state["background"].to_csv(buffer_background, index=False)
    st.session_state["story_output"].to_csv(buffer_story, index=False)
    buffer_voice.seek(0)
    buffer_background.seek(0)
    buffer_story.seek(0)

    st.download_button("Download voice_input.csv", buffer_voice.getvalue(), "voice_input.csv", "text/csv", key="download_voice")
    st.download_button("Download background.csv", buffer_background.getvalue(), "background.csv", "text/csv", key="download_background")
    st.download_button("Download story_output.csv", buffer_story.getvalue(), "story_output.csv", "text/csv", key="download_story")





