import streamlit as st
import pandas as pd

st.set_page_config(page_title="Voice & Background Prefill", layout="wide")
st.title("🧠 ML Input Manager with Prefill from Uploaded Files")

# Initialize session state
for key in ["voice_workfile", "background_workfile"]:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame()

# Sidebar: Upload files
st.sidebar.header("📁 Upload CSV Files")
voice_file = st.sidebar.file_uploader("Upload voice_input.csv", type="csv")
background_file = st.sidebar.file_uploader("Upload background.csv", type="csv")

# Load uploaded files
def load_csv(file):
    return pd.read_csv(file) if file else pd.DataFrame()

voice_df = load_csv(voice_file)
background_df = load_csv(background_file)

# Extract prefill options from first column
voice_dates = voice_df.iloc[:, 0].dropna().unique().tolist() if not voice_df.empty else []
background_dates = background_df.iloc[:, 0].dropna().unique().tolist() if not background_df.empty else []

prefill_options = sorted(set(voice_dates + background_dates))

# Sidebar: Prefill dropdown
selected_date = st.sidebar.selectbox("Select dateversion to prefill", [""] + prefill_options)

# Process uploaded files and update workfiles
def update_workfile(new_df, workfile_key, selected_date):
    if not new_df.empty and selected_date:
        # Insert selected dateversion as first column
        new_df.insert(0, "dateversion", selected_date)

        # Shift existing columns in memory
        if not st.session_state[workfile_key].empty:
            st.session_state[workfile_key].insert(0, "dateversion", selected_date)

        # Append new row
        st.session_state[workfile_key] = pd.concat(
            [st.session_state[workfile_key], new_df], ignore_index=True
        )

# Update workfiles
update_workfile(voice_df, "voice_workfile", selected_date)
update_workfile(background_df, "background_workfile", selected_date)

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

 



