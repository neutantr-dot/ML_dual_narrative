import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# Constants
HEADERS_URL = "https://raw.githubusercontent.com/neutantr-dot/ML_dual_narrative/main/headers.csv"
DELIMITER = "|"

# Load headers from GitHub
@st.cache_data
def load_headers():
    try:
        response = requests.get(HEADERS_URL)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), sep=DELIMITER, engine="python", quotechar='"', on_bad_lines='skip')
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        st.error(f"⚠️ Could not load headers.csv: {e}")
        return pd.DataFrame(columns=["Input_file", "Field", "Label"])

# Parse uploaded input file
def parse_input_file(uploaded_file):
    if uploaded_file is None:
        return []
    content = uploaded_file.getvalue().decode("utf-8").splitlines()
    return [line.split(DELIMITER) for line in content]

# Ensure prefill is safe and skips first row
def safe_prefill(data, expected_fields):
    if len(data) > 1:
        row = data[1]  # Skip date/version row
        return (row + [""] * expected_fields)[:expected_fields]
    return [""] * expected_fields

# Append new row to file
def append_to_file(existing_file, new_row):
    if existing_file is None:
        return DELIMITER.join(new_row)
    content = existing_file.getvalue().decode("utf-8").splitlines()
    content.insert(1, DELIMITER.join(new_row))  # Insert after header
    return "\n".join(content)

# Streamlit UI
st.set_page_config(page_title="Dual Narrative Co-Pilot", layout="wide")
st.sidebar.title("📁 Upload & Controls")

# Upload files
voice_file = st.sidebar.file_uploader("Upload voice_input.txt", type="txt")
background_file = st.sidebar.file_uploader("Upload background.txt", type="txt")
storyline_file = st.sidebar.file_uploader("Upload storyline.txt", type="txt")

# Toggle for prefill
prefill = st.sidebar.toggle("Prefill from uploaded files", value=False)

# Load headers
headers_df = load_headers()

st.title("🧠 Dual Narrative Co-Pilot Storytelling")

# Parse input files
voice_data = parse_input_file(voice_file)
background_data = parse_input_file(background













 



