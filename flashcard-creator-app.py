import streamlit as st
import json
import os
from groq import Groq
from agents import generate_book_title, generate_book_structure, generate_section
from inference import GenerationStatistics

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
    total_stats = GenerationStatistics("mixtral-8x7b-32768")
    
    # Generate a title for the flashcard set
    flashcard_set_title = generate_book_title(materials, "mixtral-8x7b-32768", client)
    
    # Generate a structure for the topic
    structure_stats, structure_json = generate_book_structure(materials, "", "mixtral-8x7b-32768", client, long=False)
    total_stats.add(structure_stats)
    structure = json.loads(structure_json)
    
    flashcards = []
    
    # Generate content for each section and create flashcards
    for section_title, section_description in structure.items():
        section_content = ""
        section_stats = GenerationStatistics("mixtral-8x7b-32768")
        for chunk in generate_section(f"{section_title}: {section_description}", "", "mixtral-8x7b-32768", client):
            if isinstance(chunk, str):
                section_content += chunk
            elif isinstance(chunk, GenerationStatistics):
                section_stats.add(chunk)
        total_stats.add(section_stats)
        
        # Create flashcards from the section content
        cards, cards_stats = create_cards_from_content(section_content, num_cards // len(structure))
        flashcards.extend(cards)
        total_stats.add(cards_stats)
    
    return flashcard_set_title, flashcards, total_stats

def create_cards_from_content(content, num_cards):
    client = Groq(api_key=st.session_state.api_key)
    
    prompt = f"""Create {num_cards} flashcards based on the following content:

{content}

Format each flashcard as follows:
Q: [Question]
A: [Answer]

Separate each flashcard with a blank line."""

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
        model="mixtral-8x7b-32768",
        max_tokens=1000,
        temperature=0.7
    )
    
    stats = GenerationStatistics(
        model_name="mixtral-8x7b-32768",
        input_time=response.usage.prompt_time,
        output_time=response.usage.completion_time,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        total_time=response.usage.total_time
    )
    
    flashcards = []
    card_texts = response.choices[0].message.content.strip().split('\n\n')
    for card_text in card_texts:
        parts = card_text.split('\n')
        if len(parts) == 2:
            question = parts[0][3:].strip()  # Remove "Q: " prefix
            answer = parts[1][3:].strip()    # Remove "A: " prefix
            flashcards.append({"question": question, "answer": answer})
    return flashcards, stats

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
    num_cards = st.number_input("Number of flashcards to generate:", min_value=1, max_value=50, value=10)
    if st.button("Generate Flashcards"):
        if st.session_state.api_key and materials:
            with st.spinner("Generating flashcards..."):
                flashcard_set_title, generated_cards, stats = generate_flashcards(st.session_state.api_key, materials, num_cards)
            if generated_cards:
                st.session_state.flashcards.extend(generated_cards)
                save_flashcards(st.session_state.flashcards)
                st.success(f"Generated {len(generated_cards)} flashcards for: {flashcard_set_title}")
                st.markdown("## Generation Statistics")
                st.markdown(str(stats))
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