import streamlit as st
from pages.advanced import check_api_key, main as advanced_main

def main():
    st.title("H5P Flashcard Generator")

    if check_api_key():
        advanced_main()
    else:
        st.error("Failed to configure GROQ API Key. Please try again.")

if __name__ == "__main__":
    main()