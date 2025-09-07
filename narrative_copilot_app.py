import streamlit as st
import pandas as pd

st.set_page_config(page_title="Voice & Background Uploader", layout="wide")

st.title("🧠 ML Input Manager")

# Initialize session state for persistent workfiles
for key in ["voice_workfile", "background_workfile"]:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame()

# Sidebar: Upload files
st.sidebar.header("📁 Upload CSV Files")
voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")

# Sidebar: Dateversion input
new_date = st.sidebar.text_input("Enter new dateversion (e.g. Sun, Sept 7, 2025 (1))")

# Function to process uploaded file and update workfile
def process_upload(file, workfile_key):
    if file:
        new_df = pd.read_csv(file)
        if new_date:
            # Insert new dateversion as first column
            new_df.insert(0, "dateversion", new_date)

            # Shift existing columns in memory
            if not st.session_state[workfile_key].empty:
                st.session_state[workfile_key].insert(0, "dateversion", new_date)

            # Append new row
            st.session_state[workfile_key] = pd.concat(
                [st.session_state[workfile_key], new_df], ignore_index=True
            )

# Process uploads
process_upload(voice_file, "voice_workfile")
process_upload(background_file, "background_workfile")

# Display and download updated workfiles
st.subheader("📤 Updated Files")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### voice_input.csv")
    st.dataframe(st.session_state.voice_workfile)
    st.download_button(
        "Download voice_input.csv",
        st.session_state.voice_workfile.to_csv(index=False).encode("utf-8"),
        file_name="voice_input.csv"
    )

with col2:
    st.markdown("### background.csv")
    st.dataframe(st.session_state.background_workfile)
    st.download_button(
        "Download background.csv",
        st.session_state.background_workfile.to_csv(index=False).encode("utf-8"),
        file_name="background.csv"
    )




