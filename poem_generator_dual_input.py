import streamlit as st
import pandas as pd
import os
import io

# --- Poem generation placeholder (ML model simulation) ---
def generate_response(user_input):
    return f"I'm feeling inspired by your words: '{user_input}'. Here's a poetic thought: 'Stars whisper secrets to the night.'"

def ml_generate_poem(text):
    return f"From memories and nature, a verse blooms: '{text[:30]}...'"


# --- Sidebar Uploads ---
st.sidebar.header("Upload Previous Session Files")
uploaded_csv1 = st.sidebar.file_uploader("Upload CSV1.csv", type="csv")
uploaded_csv2 = st.sidebar.file_uploader("Upload CSV2.csv", type="csv")
uploaded_csv3 = st.sidebar.file_uploader("Upload CSV3.csv", type="csv")

# --- Load or initialize dataframes ---
df1 = pd.read_csv(uploaded_csv1) if uploaded_csv1 else pd.read_csv("CSV1.csv") if os.path.exists("CSV1.csv") else pd.DataFrame()
df2 = pd.read_csv(uploaded_csv2) if uploaded_csv2 else pd.read_csv("CSV2.csv") if os.path.exists("CSV2.csv") else pd.DataFrame()
df3 = pd.read_csv(uploaded_csv3) if uploaded_csv3 else pd.read_csv("CSV3.csv") if os.path.exists("CSV3.csv") else pd.DataFrame(columns=["Generated_Poem"])

# --- App UI ---
st.title("Poem Generator with Dual Input Sets and ML Output")

# Input Set 1
st.header("Input Set 1")
input1_1 = st.text_input("Enter a thought about nature", key="input1_1")
input1_2 = st.text_input("Describe a feeling you had today", key="input1_2")
input1_3 = st.text_input("Mention a color that inspires you", key="input1_3")
input1_4 = st.text_input("Write a short phrase about dreams", key="input1_4")

# Input Set 2
st.header("Input Set 2")
input2_1 = st.text_input("Share a memory from childhood", key="input2_1")
input2_2 = st.text_input("Name a place you want to visit", key="input2_2")
input2_3 = st.text_input("Describe your favorite season", key="input2_3")
input2_4 = st.text_input("Write a line about hope", key="input2_4")

# --- Generate Button ---
if st.button("Generate Poetic Responses"):
    combined_input1 = " ".join([input1_1, input1_2, input1_3, input1_4])
    combined_input2 = " ".join([input2_1, input2_2, input2_3, input2_4])
    full_input = combined_input1 + " " + combined_input2

    # Generate responses
    response1 = generate_response(combined_input1)
    response2 = generate_response(combined_input2)
    ml_poem = ml_generate_poem(full_input)

    # Display
    st.subheader("Poetic Response from Input Set 1")
    st.write(response1)
    st.subheader("Poetic Response from Input Set 2")
    st.write(response2)
    st.subheader("ML-Generated Poem Line")
    st.write(ml_poem)

    # Append to CSV1, CSV2, CSV3
    df1 = pd.concat([df1, pd.Series([input1_1, input1_2, input1_3, input1_4], name=f"Session_{len(df1.columns)+1}")], axis=1)
    df2 = pd.concat([df2, pd.Series([input2_1, input2_2, input2_3, input2_4], name=f"Session_{len(df2.columns)+1}")], axis=1)
    df3.loc[len(df3)] = [ml_poem]

    # Save locally
    df1.to_csv("CSV1.csv", index=False)
    df2.to_csv("CSV2.csv", index=False)
    df3.to_csv("CSV3.csv", index=False)

    # Store in session state for download
    st.session_state["csv1"] = df1
    st.session_state["csv2"] = df2
    st.session_state["csv3"] = df3

# --- Download Buttons ---
if "csv1" in st.session_state:
    buffer1 = io.StringIO()
    st.session_state["csv1"].to_csv(buffer1, index=False)
    buffer1.seek(0)
    st.download_button("Download CSV1", buffer1.getvalue(), "CSV1.csv", "text/csv", key="download_csv1")

if "csv2" in st.session_state:
    buffer2 = io.StringIO()
    st.session_state["csv2"].to_csv(buffer2, index=False)
    buffer2.seek(0)
    st.download_button("Download CSV2", buffer2.getvalue(), "CSV2.csv", "text/csv", key="download_csv2")

if "csv3" in st.session_state:
    buffer3 = io.StringIO()
    st.session_state["csv3"].to_csv(buffer3, index=False)
    buffer3.seek(0)
    st.download_button("Download CSV3", buffer3.getvalue(), "CSV3.csv", "text/csv", key="download_csv3")
