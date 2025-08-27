import streamlit as st
import pandas as pd
import os
import io

# ML-style poem generator (placeholder)
def ml_generate_poem(text):
    return f"From memories and nature, a verse blooms: '{text[:30]}...'"

# Sidebar uploads
st.sidebar.header("Upload Previous Session Files")
uploaded_csv1 = st.sidebar.file_uploader("Upload CSV1.csv", type="csv")
uploaded_csv2 = st.sidebar.file_uploader("Upload CSV2.csv", type="csv")
uploaded_csv3 = st.sidebar.file_uploader("Upload CSV3.csv", type="csv")

# Load or initialize dataframes
df1 = pd.read_csv(uploaded_csv1) if uploaded_csv1 else pd.read_csv("CSV1.csv") if os.path.exists("CSV1.csv") else pd.DataFrame()
df2 = pd.read_csv(uploaded_csv2) if uploaded_csv2 else pd.read_csv("CSV2.csv") if os.path.exists("CSV2.csv") else pd.DataFrame()
df3 = pd.read_csv(uploaded_csv3) if uploaded_csv3 else pd.read_csv("CSV3.csv") if os.path.exists("CSV3.csv") else pd.DataFrame()

# App title
st.title("Poem Generator with Dual Input Sets")

# Input Set 1
st.header("Input Set 1")
input1_1 = st.text_input("Enter a thought about nature")
input1_2 = st.text_input("Describe a feeling you had today")
input1_3 = st.text_input("Mention a color that inspires you")
input1_4 = st.text_input("Write a short phrase about dreams")

# Input Set 2
st.header("Input Set 2")
input2_1 = st.text_input("Share a memory from childhood")
input2_2 = st.text_input("Name a place you want to visit")
input2_3 = st.text_input("Describe your favorite season")
input2_4 = st.text_input("Write a line about hope")

# Display previously generated poem line if available
if "poem_line" in st.session_state:
    st.subheader("Generated Poem Line")
    st.write(st.session_state["poem_line"])

# Generate button
if st.button("Generate Poem Line"):
    combined_input1 = " ".join([input1_1, input1_2, input1_3, input1_4])
    combined_input2 = " ".join([input2_1, input2_2, input2_3, input2_4])
    full_input = combined_input1 + " " + combined_input2

    poem_line = ml_generate_poem(full_input)
    st.session_state["poem_line"] = poem_line

    st.subheader("Generated Poem Line")
    st.write(poem_line)

    # Append to CSV1, CSV2, CSV3 as new columns
    session_id = f"Session_{len(df1.columns)+1}"
    df1[session_id] = [input1_1, input1_2, input1_3, input1_4]
    df2[session_id] = [input2_1, input2_2, input2_3, input2_4]
    df3[session_id] = [poem_line]

    # Save locally
    df1.to_csv("CSV1.csv", index=False)
    df2.to_csv("CSV2.csv", index=False)
    df3.to_csv("CSV3.csv", index=False)

    # Store in session state
    st.session_state["csv1"] = df1
    st.session_state["csv2"] = df2
    st.session_state["csv3"] = df3

# Download buttons
for label, key in zip(["CSV1", "CSV2", "CSV3"], ["csv1", "csv2", "csv3"]):
    if key in st.session_state:
        buffer = io.StringIO()
        st.session_state[key].to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(f"Download {label}", buffer.getvalue(), f"{label}.csv", "text/csv", key=f"download_{key}")
