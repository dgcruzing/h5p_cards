import streamlit as st

def display_flashcards(flashcards):
    st.header("Your Flashcards")
    if flashcards:
        for i, card in enumerate(flashcards):
            with st.expander(f"Flashcard {i+1}"):
                st.subheader("Question")
                st.write(card['question'])
                st.subheader("Answer")
                st.write(card['answer'])
    else:
        st.info("No flashcards created yet. Go to the 'Create Flashcards' section to add some!")