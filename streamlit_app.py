
import streamlit as st

def generate_response(user_input):
    return f"I'm feeling inspired by your words: '{user_input}'. Here's a poetic thought: 'Stars whisper secrets to the night.’"

st.title("Poem Generator")
user_input = st.text_input("Enter your inspiration:")
if st.button("Generate"):
    response = generate_response(user_input)
    st.markdown(f"**Poem:**<br>{response}", unsafe_allow_html=True)
