import streamlit as st
import pandas as pd
import os
import io

# ML-style poem generator (placeholder)
def ml_generate_poem(text):
    return f"From memories and nature, a verse blooms: '{text[:30]}...'"

# Sidebar upload for CSV3
st.sidebar.header("Upload Previous Poem Outputs")
uploaded_csv3 = st.sidebar.file_uploader("Upload CSV3.csv", type="csv")

# Load or initialize CSV3
if uploaded_csv3:
    df3 = pd.read_csv(uploaded_csv3)
elif os.path.exists("CSV3.csv"):
    df3 = pd.read_csv("CSV3.csv")
else:
    df3 = pd.DataFrame(columns=["Generated_Poem"])

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

# Generate button
if st.button("Generate Poem Line"):
    combined_input = " ".join([
        input1_1, input1_2, input1_3, input1_4,
        input2_1, input2_2, input2_3, input2_4
    ])

    poem_line = ml_generate_poem(combined_input)
    st.subheader("Generated Poem Line")
    st.write(poem_line)

    # Append to CSV3
    df3 = pd.concat([df3, pd.DataFrame({"Generated_Poem": [poem_line]})], ignore_index=True)
    df3.to_csv("CSV3.csv", index=False)
    st.session_state["csv3"] = df3

# Download CSV3
if "csv3" in st.session_state:
    buffer = io.StringIO()
    st.session_state["csv3"].to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("Download CSV3", buffer.getvalue(), "CSV3.csv", "text/csv", key="download_csv3")
