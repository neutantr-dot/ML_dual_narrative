
import streamlit as st
import pandas as pd
import os
import io

# Poetic response function
def generate_response(user_input):
    return f"I'm feeling inspired by your words: '{user_input}'. Here's a poetic thought: 'Stars whisper secrets to the night.'"

# Sidebar upload
st.sidebar.header("Upload Previous Session Files")
uploaded_csv1 = st.sidebar.file_uploader("Upload CSV1.csv", type="csv")
uploaded_csv2 = st.sidebar.file_uploader("Upload CSV2.csv", type="csv")

# Load uploaded or fallback to local
df1 = pd.read_csv(uploaded_csv1) if uploaded_csv1 else pd.read_csv("CSV1.csv") if os.path.exists("CSV1.csv") else pd.DataFrame()
df2 = pd.read_csv(uploaded_csv2) if uploaded_csv2 else pd.read_csv("CSV2.csv") if os.path.exists("CSV2.csv") else pd.DataFrame()
df3 = pd.read_csv("CSV3.csv") if os.path.exists("CSV3.csv") else pd.DataFrame(columns=["Poem1", "Poem2"])

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
if st.button("Generate Poetic Responses"):
    combined_input1 = " ".join([input1_1, input1_2, input1_3, input1_4])
    combined_input2 = " ".join([input2_1, input2_2, input2_3, input2_4])

    response1 = generate_response(combined_input1)
    response2 = generate_response(combined_input2)

    st.subheader("Poetic Response from Input Set 1")
    st.write(response1)

    st.subheader("Poetic Response from Input Set 2")
    st.write(response2)

    # Append new session as a column
    new_col1 = pd.Series([input1_1, input1_2, input1_3, input1_4], name=f"Session_{len(df1.columns)+1}")
    new_col2 = pd.Series([input2_1, input2_2, input2_3, input2_4], name=f"Session_{len(df2.columns)+1}")

    df1 = pd.concat([df1, new_col1], axis=1)
    df2 = pd.concat([df2, new_col2], axis=1)

    # Append poems to CSV3
    df3.loc[len(df3)] = [response1, response2]

    # Save all CSVs
    df1.to_csv("CSV1.csv", index=False)
    df2.to_csv("CSV2.csv", index=False)
    df3.to_csv("CSV3.csv", index=False)

    st.success("Inputs and poems saved successfully!")

# Prepare in-memory download buffers
csv1_buffer = io.StringIO()
csv2_buffer = io.StringIO()
csv3_buffer = io.StringIO()
df1.to_csv(csv1_buffer, index=False)
df2.to_csv(csv2_buffer, index=False)
df3.to_csv(csv3_buffer, index=False)

# Download buttons
st.download_button("Download CSV1", csv1_buffer.getvalue(), "CSV1.csv", "text/csv", key="download_csv1")
st.download_button("Download CSV2", csv2_buffer.getvalue(), "CSV2.csv", "text/csv", key="download_csv2")
st.download_button("Download CSV3 (Poems)", csv3_buffer.getvalue(), "CSV3.csv", "text/csv", key="download_csv3")
