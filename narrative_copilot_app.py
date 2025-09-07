import streamlit as st
import pandas as pd

# Load headers
headers_url = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
headers_df = pd.read_csv(headers_url, sep="|")

# Sidebar toggles
start_fresh = st.sidebar.checkbox("Start Fresh")
prefill = st.sidebar.checkbox("Prefill from input files")

# Upload files
voice_file = st.sidebar.file_uploader("Upload voice_input.txt")
background_file = st.sidebar.file_uploader("Upload background.txt")
story_file = st.sidebar.file_uploader("Upload storyline.txt (optional)")

# Main input fields
for _, row in headers_df.iterrows():
    label = row["Label"]
    field_key = f"{row['Input_file']}_{row['Field']}"
    default_value = ""  # Add logic to prefill from uploaded files
    st.text_input(label, value=default_value, key=field_key)

# Generate story button
if st.button("Generate Dual Narrative"):
    # Call ML model here
    st.text_area("Generated Storyline", "Your story will appear here...", height=400)

# Download buttons
st.button("Append Inputs to File")
st.button("Append Storyline to File")









 



