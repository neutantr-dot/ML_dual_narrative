import streamlit as st
import pandas as pd
import os

# Poetic response function
def generate_response(user_input):
    return f"I'm feeling inspired by your words: '{user_input}'. Here's a poetic thought: 'Stars whisper secrets to the night.'"

# CSV file names
csv1_file = "CSV1.csv"
csv2_file = "CSV2.csv"

# Load or initialize CSVs
df1 = pd.read_csv(csv1_file) if os.path.exists(csv1_file) else pd.DataFrame()
df2 = pd.read_csv(csv2_file) if os.path.exists(csv2_file) else pd.DataFrame()

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

    df1.to_csv(csv1_file, index=False)
    df2.to_csv(csv2_file, index=False)

    st.success("Inputs saved and responses generated!")

