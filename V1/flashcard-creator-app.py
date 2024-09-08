import streamlit as st
import json
import os
from groq import Groq

# Function to load flashcards from a file
def load_flashcards():
    if os.path.exists("flashcards.json"):
        with open("flashcards.json", "r") as f:
            return json.load(f)
    return []

# Function to save flashcards to a file
def save_flashcards(flashcards):
    with open("flashcards.json", "w") as f:
        json.dump(flashcards, f)

def create_flashcard():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Front (Question)")
        question = st.text_area("Enter the question:", height=200)
    with col2:
        st.subheader("Back (Answer)")
        answer = st.text_area("Enter the answer:", height=200)
    return {"question": question, "answer": answer}

def generate_flashcards(api_key, materials, num_cards=10):
    client = Groq(api_key=api_key)
    
    prompt = f"""Create {num_cards} flashcards based on the following material:

{materials}

Format each flashcard as follows:
Q: [Question]
A: [Answer]

Separate each flashcard with a blank line."""

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates educational flashcards."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768",  # or another appropriate Groq model
            max_tokens=1000,
            temperature=0.7
        )
        
        flashcards = []
        card_texts = response.choices[0].message.content.strip().split('\n\n')
        for card_text in card_texts:
            parts = card_text.split('\n')
            if len(parts) == 2:
                question = parts[0][3:].strip()  # Remove "Q: " prefix
                answer = parts[1][3:].strip()    # Remove "A: " prefix
                flashcards.append({"question": question, "answer": answer})
        return flashcards
    except Exception as e:
        st.error(f"Error generating flashcards: {str(e)}")
        return []

def main():
    st.title("Groq-Powered H5P Flashcard Creator")

    # Load existing flashcards
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = load_flashcards()

    # API Key handling
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    api_key = st.text_input("Enter your Groq API Key:", type="password", value=st.session_state.api_key)
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    # Create new flashcard
    st.header("Create a New Flashcard")
    new_card = create_flashcard()
    if st.button("Add Flashcard"):
        if new_card["question"] and new_card["answer"]:
            st.session_state.flashcards.append(new_card)
            save_flashcards(st.session_state.flashcards)
            st.success("Flashcard added successfully!")
        else:
            st.error("Please enter both question and answer.")

    # Groq-generated flashcards
    st.header("Generate Flashcards with Groq")
    materials = st.text_area("Enter your learning materials or document:")
    num_cards = st.number_input("Number of flashcards to generate:", min_value=1, max_value=20, value=10)
    if st.button("Generate Flashcards"):
        if st.session_state.api_key and materials:
            with st.spinner("Generating flashcards..."):
                generated_cards = generate_flashcards(st.session_state.api_key, materials, num_cards)
            if generated_cards:
                st.session_state.flashcards.extend(generated_cards)
                save_flashcards(st.session_state.flashcards)
                st.success(f"Generated {len(generated_cards)} flashcards!")
            else:
                st.error("Failed to generate flashcards. Please check your API key and try again.")
        else:
            st.error("Please enter both API key and learning materials.")

    # Display existing flashcards
    if st.session_state.flashcards:
        st.header("Your Flashcards")
        for i, card in enumerate(st.session_state.flashcards):
            st.subheader(f"Flashcard {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Question:", value=card['question'], height=100, key=f"q_{i}")
            with col2:
                st.text_area("Answer:", value=card['answer'], height=100, key=f"a_{i}")

    # Export flashcards
    if st.session_state.flashcards:
        if st.button("Export Flashcards"):
            flashcards_json = json.dumps(st.session_state.flashcards, indent=2)
            st.download_button(
                label="Download JSON",
                data=flashcards_json,
                file_name="flashcards.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
