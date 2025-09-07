import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 📥 Load headers from GitHub
headers_url = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
headers_df = pd.read_csv(headers_url)
voice_headers = headers_df.iloc[1:5, 0].tolist()
background_headers = headers_df.iloc[6:11, 0].tolist()

# 📤 Sidebar
st.sidebar.title("📂 Upload Files")
voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")
output_file = st.sidebar.file_uploader("Upload output.csv", type="csv")

toggle = st.sidebar.radio("Session Mode", ["🔄 Fresh Start", "📦 Fetch Last"])

# 🧠 Load Data
if voice_file and background_file:
    voice_df = pd.read_csv(voice_file)
    background_df = pd.read_csv(background_file)
    output_df = pd.read_csv(output_file) if output_file else pd.DataFrame()

    # 🗓️ Dateversion
    today = datetime.now().strftime("%a, %b %d, %Y (1)")
    st.markdown(f"### 📅 Dateversion: `{today}`")

    # 🎙️ Voice Input Fields
    st.subheader("🎧 Voice Input")
    voice_inputs = {}
    for i, header in enumerate(voice_headers):
        voice_inputs[header] = st.text_input(f"{header}", value=voice_df.iloc[0, i+1] if toggle == "📦 Fetch Last" else "")

    # 🧩 Background Fields
    st.subheader("🧠 Background Input")
    background_inputs = {}
    for i, header in enumerate(background_headers):
        background_inputs[header] = st.text_input(f"{header}", value=background_df.iloc[0, i+1] if toggle == "📦 Fetch Last" else "")

    # 🧬 ML Story Generation (Placeholder logic)
    st.subheader("📖 Generated Story")
    if st.button("Generate Story"):
        story = f"On {today}, you reflected on your inner world and external context. Your inner voice said '{voice_inputs[voice_headers[0]]}', while your partner voice echoed '{voice_inputs[voice_headers[2]]}'. You were located at '{voice_inputs[voice_headers[3]]}', contemplating work, money, and ambition. You felt '{background_inputs[background_headers[3]]}', and your overall well-being was '{background_inputs[background_headers[4]]}'."
        st.text_area("Your Story", story, height=200)

        # 📊 Append and shift history
        new_voice_row = [today] + list(voice_inputs.values())
        new_background_row = [today] + list(background_inputs.values())
        new_output_row = [today, story]

        voice_df.loc[len(voice_df)] = new_voice_row
        background_df.loc[len(background_df)] = new_background_row
        output_df.loc[len(output_df)] = new_output_row

        # 📥 Download buttons
        st.download_button("⬇️ Download Updated Voice Input", voice_df.to_csv(index=False), "updated_voice_input.csv")
        st.download_button("⬇️ Download Updated Background", background_df.to_csv(index=False), "updated_background.csv")
        st.download_button("⬇️ Download Generated Output", output_df.to_csv(index=False), "generated_output.csv")

else:
    st.warning("Please upload all three files to begin.")



 



