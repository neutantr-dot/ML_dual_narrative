import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime


if "initialized" not in st.session_state:
    st.session_state.clear()
    st.session_state["initialized"] = True


if st.sidebar.button("Clear Poetic History"):
    df3 = pd.DataFrame()
    df3.to_csv("CSV3.csv", index=False)
    st.session_state["csv3"] = df3
    st.experimental_rerun()

headers_df = pd.read_csv("https://raw.githubusercontent.com/neutantr-dot/poem/main/headers.csv")

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
df1 = pd.read_csv(uploaded_csv1) if uploaded_csv1 else pd.DataFrame()
df2 = pd.read_csv(uploaded_csv2) if uploaded_csv2 else pd.DataFrame()
#df3 = pd.read_csv(uploaded_csv3) if uploaded_csv3 else pd.DataFrame()
df3 = pd.read_csv(uploaded_csv3, encoding='utf-8') if uploaded_csv3 else pd.DataFrame()

# Input mode toggle
st.sidebar.markdown("---")
input_mode = st.sidebar.radio("Input Mode", ["Start Fresh", "Edit Last Session"])

# Prefill only if user uploaded CSVs and chose "Edit Last Session"
if input_mode == "Edit Last Session" and not df1.empty and not df2.empty:
    latest_input1 = df1.iloc[:, -1].tolist()
    latest_input2 = df2.iloc[:, -1].tolist()
else:
    latest_input1 = [""] * 4
    latest_input2 = [""] * 4

# App title
st.title("Poem Generator with Dual Input Sets")

# Input Set 1
st.header("Input Set 1")
input1_values = []
for i, row in headers_df[headers_df["InputSet"] == 1].reset_index(drop=True).iterrows():
    default_val = latest_input1[i] if i < len(latest_input1) else ""
    val = st.text_input(row["Label"], value=default_val, key=row["Field"])
    input1_values.append(val)



# Input Set 2

st.header("Input Set 2")
input2_values = []
for i, row in headers_df[headers_df["InputSet"] == 2].reset_index(drop=True).iterrows():
    default_val = latest_input2[i] if i < len(latest_input2) else ""
    val = st.text_input(row["Label"], value=default_val, key=row["Field"])
    input2_values.append(val)



# Check if all inputs are filled
# inputs_filled = all([
#    input1_1, input1_2, input1_3, input1_4,
#    input2_1, input2_2, input2_3, input2_4
#])

# Generate button

inputs_filled = all(input1_values + input2_values)

if inputs_filled:
    if st.button("Generate Poetic Response"):
        combined_input1 = " ".join(input1_values)
        combined_input2 = " ".join(input2_values)

        # Simulate ML classification (replace with real model later)
        main_category = "A"  # Placeholder
        sub_category = "1"   # Placeholder
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Append classification to internal file
        try:
            class_df = pd.read_csv("classification.csv")
        except:
            class_df = pd.DataFrame(columns=["Timestamp", "MainCategory", "SubCategory"])
        new_row = pd.DataFrame({
            "Timestamp": [timestamp],
            "MainCategory": [main_category],
            "SubCategory": [sub_category]
        })
        class_df = pd.concat([class_df, new_row], ignore_index=True)
        class_df.to_csv("classification.csv", index=False)

        poetic_output = generate_response(combined_input1, combined_input2)
        st.session_state["poetic_output"] = poetic_output


        # Create readable date string
        base_date = datetime.now().strftime("%a, %b %d, %Y")

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
        new_col1 = pd.Series(input1_values, name=col_name1)
        new_col2 = pd.Series(input2_values, name=col_name2)
        new_col3 = pd.Series([poetic_output], name=col_name3)

        df1 = pd.concat([df1, new_col1], axis=1)
        df2 = pd.concat([df2, new_col2], axis=1)

        if df3.empty:
            df3 = pd.DataFrame(index=[0])

        df3 = pd.concat([df3, new_col3], axis=1)


        # Save updated CSVs
        df1.to_csv("CSV1.csv", index=False, encoding='utf-8')
        df2.to_csv("CSV2.csv", index=False, encoding='utf-8')
        df3.to_csv("CSV3.csv", index=False, encoding='utf-8')

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
    
# Optional: Poem History Viewer
if not df3.empty:
    st.subheader("Browse Past Poetic Responses")
    selected_col = st.selectbox("Select a session to view its poem", df3.columns[::-1])
    selected_poem = df3[selected_col].values[0] if not df3[selected_col].empty else "No poem found."
    st.text_area("Poetic Response", selected_poem, height=150)


# Optional: Input Set 1 History Viewer
if not df1.empty:
    st.subheader("Browse Past Input Set 1 Sessions")
    selected_col1 = st.selectbox("Select a session from CSV1", df1.columns[::-1])
    selected_input1 = "\n".join(df1[selected_col1].dropna().astype(str))
    st.text_area("Input Set 1", selected_input1, height=150)

# Optional: Input Set 2 History Viewer
if not df2.empty:
    st.subheader("Browse Past Input Set 2 Sessions")
    selected_col2 = st.selectbox("Select a session from CSV2", df2.columns[::-1])
    selected_input2 = "\n".join(df2[selected_col2].dropna().astype(str))
    st.text_area("Input Set 2", selected_input2, height=150)

# Display last 2 columns of session history
# def show_last_two(df, label):
#    if not df.empty:
#        st.subheader(label)
#       st.dataframe(df.iloc[:, -2:] if df.shape[1] >= 2 else df)

# show_last_two(df1, "Session History - Input Set 1 (Last 2)")
# show_last_two(df2, "Session History - Input Set 2 (Last 2)")
# show_last_two(df3, "Session History - Poetic Output (Last 2)")

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
