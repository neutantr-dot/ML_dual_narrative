import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# Poetic response function
def generate_response(input1, input2):
    return (
        f"From your reflections on nature, emotions, colors, and dreams — "
        f"'{input1}' — and your memories, aspirations, seasons, and hope — "
        f"'{input2}' — emerges this poetic thought: "
        f"'Stars whisper secrets to the night, carrying echoes of your soul.'"
    )

# Sidebar upload
st.sidebar.header("Upload Previous Session Files")
uploaded_csv1 = st.sidebar.file_uploader("Upload CSV1.csv", type="csv")
uploaded_csv2 = st.sidebar.file_uploader("Upload CSV2.csv", type="csv")
uploaded_csv3 = st.sidebar.file_uploader("Upload CSV3.csv", type="csv")

# Load uploaded or fallback to local
df1 = pd.read_csv(uploaded_csv1) if uploaded_csv1 else pd.read_csv("CSV1.csv") if os.path.exists("CSV1.csv") else pd.DataFrame()
df2 = pd.read_csv(uploaded_csv2) if uploaded_csv2 else pd.read_csv("CSV2.csv") if os.path.exists("CSV2.csv") else pd.DataFrame()
df3 = pd.read_csv(uploaded_csv3) if uploaded_csv3 else pd.read_csv("CSV3.csv") if os.path.exists("CSV3.csv") else pd.DataFrame()

# App title
st.title("Poem Generator with Dual Input Sets")

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

# Check if all inputs are filled
inputs_filled = all([
    input1_1, input1_2, input1_3, input1_4,
    input2_1, input2_2, input2_3, input2_4
])

# Generate button
if inputs_filled:
    if st.button("Generate Poetic Response"):
        combined_input1 = " ".join([input1_1, input1_2, input1_3, input1_4])
        combined_input2 = " ".join([input2_1, input2_2, input2_3, input2_4])

        poetic_output = generate_response(combined_input1, combined_input2)
        st.session_state["poetic_output"] = poetic_output

        # Create readable date string
        base_date = datetime.now().strftime("%a, %b %d, %Y")  # e.g., Thu, Aug 28, 2025

        # Count existing columns with today's date
        def count_existing(df, base_date):
            return sum([1 for col in df.columns if col.startswith(f"Session {base_date}")])

        count1 = count_existing(df1, base_date) + 1
        count2 = count_existing(df2, base_date) + 1
        count3 = count_existing(df3, base_date) + 1

        col_name1 = f"Session {base_date} ({count1})"
        col_name2 = f"Session {base_date} ({count2})"
        col_name3 = f"Session {base_date} ({count3})"

        # Append inputs and output to respective DataFrames
        new_col1 = pd.Series([input1_1, input1_2, input1_3, input1_4], name=col_name1)
        new_col2 = pd.Series([input2_1, input2_2, input2_3, input2_4], name=col_name2)
        new_col3 = pd.Series([poetic_output], name=col_name3)

        df1 = pd.concat([df1, new_col1], axis=1)
        df2 = pd.concat([df2, new_col2], axis=1)
        df3 = pd.concat([df3, new_col3], axis=1)

        # Save updated CSVs
        df1.to_csv("CSV1.csv", index=False)
        df2.to_csv("CSV2.csv", index=False)
        df3.to_csv("CSV3.csv", index=False)

        # Store in session state
        st.session_state["csv1"] = df1
        st.session_state["csv2"] = df2
        st.session_state["csv3"] = df3
else:
    st.warning("Please fill in all input fields before generating.")

# Display poetic output
if "poetic_output" in st.session_state:
    st.subheader("Generated Poetic Response")
    st.write(st.session_state["poetic_output"])

# Display session history
if not df1.empty:
    st.subheader("Session History - Input Set 1")
    st.dataframe(df1)

if not df2.empty:
    st.subheader("Session History - Input Set 2")
    st.dataframe(df2)

if not df3.empty:
    st.subheader("Session History - Poetic Output")
    st.dataframe(df3)

# Download buttons
if "csv1" in st.session_state and "csv2" in st.session_state and "csv3" in st.session_state:
    csv1_buffer = io.StringIO()
    csv2_buffer = io.StringIO()
    csv3_buffer = io.StringIO()
    st.session_state["csv1"].to_csv(csv1_buffer, index=False)
    st.session_state["csv2"].to_csv(csv2_buffer, index=False)
    st.session_state["csv3"].to_csv(csv3_buffer, index=False)
    csv1_buffer.seek(0)
    csv2_buffer.seek(0)
    csv3_buffer.seek(0)

    st.download_button("Download CSV1", csv1_buffer.getvalue(), "CSV1.csv", "text/csv", key="download_csv1")
    st.download_button("Download CSV2", csv2_buffer.getvalue(), "CSV2.csv", "text/csv", key="download_csv2")
    st.download_button("Download CSV3", csv3_buffer.getvalue(), "CSV3.csv", "text/csv", key="download_csv3")
