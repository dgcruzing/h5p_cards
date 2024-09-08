import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
from groq import Groq
import json
from io import BytesIO
from markdown import markdown
from weasyprint import HTML, CSS
from tools import create_h5p_json, create_markdown_file, create_pdf_file, create_flashcards_markdown

# Initialize env variables and session states
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

states = {
    "api_key": GROQ_API_KEY,
    "button_disabled": False,
    "button_text": "Generate Flashcards",
    "statistics_text": "",
    "flashcards": [],
}

if GROQ_API_KEY:
    states["groq"] = Groq()

def ensure_states(state_dict):
    for key, default_value in state_dict.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

ensure_states(states)

def load_flashcards():
    if os.path.exists("flashcards.json"):
        with open("flashcards.json", "r") as f:
            return json.load(f)
    return []

def save_flashcards(flashcards):
    with open("flashcards.json", "w") as f:
        json.dump(flashcards, f)

def generate_flashcards(api_key, materials, num_cards=10, model="mixtral-8x7b-32768"):
    client = Groq(api_key=api_key)
    prompt = f"""Create {num_cards} flashcards based on the following content:

{materials}

Format each flashcard as follows:
Q: [Question]
A: [Answer]

Separate each flashcard with a blank line."""

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates educational flashcards."},
            {"role": "user", "content": prompt}
        ],
        model=model,
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
    
    return flashcards, {
        "model_name": model,
        "input_time": response.usage.prompt_time,
        "output_time": response.usage.completion_time,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_time": response.usage.total_time
    }

def display_statistics(statistics_text):
    st.text(statistics_text)

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
        st.info("No flashcards created yet. Generate some flashcards first!")

def render_advanced_groq_form(on_submit, button_disabled=False, button_text="Generate"):
    MODEL_LIST = ["llama3-70b-8192", "llama3-8b-8192", "gemma2-9b-it"]

    st.sidebar.title("Select AI Models")

    with st.sidebar:
        st.warning("🚧 Advanced Mode is in beta: You're using a version with experimental features.")

        st.markdown("### For creating content:")
        section_agent_model = st.selectbox(
            "Content Generation Model",
            MODEL_LIST,
            index=1,
            help="Generates content for flashcards",
        )

    with st.form("groqform"):
        st.info("You are using advanced mode with additional features.")

        if not st.session_state.get("api_key"):
            st.subheader("API Key")
            groq_input_key = st.text_input("Enter your Groq API Key (gsk_yA...):", "", type="password")
        else:
            groq_input_key = None

        st.subheader("Flashcard Details")
        topic_text = st.text_input("Flashcard Set Title", help="Enter a title for your flashcard set")
        num_cards = st.number_input("Number of flashcards to generate:", min_value=1, max_value=50, value=10)

        st.subheader("Additional Instructions")
        additional_instructions = st.text_area(
            "Provide any specific guidelines or preferences for the content",
            placeholder="E.g., 'Focus on beginner-friendly content', 'Include examples', etc.",
            value="",
        )

        col1, col2 = st.columns(2)
        with col1:
            writing_style = st.selectbox("Writing Style", ["Casual", "Formal", "Academic", "Creative"])
        with col2:
            complexity_level = st.select_slider("Complexity Level", options=["Beginner", "Intermediate", "Advanced", "Expert"])

        st.subheader("Seed Content")
        seed_content = st.text_area(
            "Provide any existing notes or content to be incorporated",
            placeholder="Enter your existing notes or content here...",
            height=200,
            value="",
        )

        st.subheader("File Upload")
        uploaded_file = st.file_uploader(
            "Upload a text file with your seed content (optional)",
            type=["txt"],
            help="Upload a text file with your seed content (optional)",
        )

        submitted = st.form_submit_button(
            button_text,
            on_click=on_submit,
            disabled=button_disabled,
        )

    return (
        submitted,
        groq_input_key,
        topic_text,
        additional_instructions,
        writing_style,
        complexity_level,
        seed_content,
        uploaded_file,
        section_agent_model,
        num_cards,
    )

def main():
    st.title("H5P Flashcard Generator")

    # Load existing flashcards
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = load_flashcards()

    (
        submitted,
        groq_input_key,
        topic_text,
        additional_instructions,
        writing_style,
        complexity_level,
        seed_content,
        uploaded_file,
        section_agent_model,
        num_cards
    ) = render_advanced_groq_form(
        on_submit=lambda: setattr(st.session_state, 'button_disabled', True),
        button_disabled=st.session_state.button_disabled,
        button_text=st.session_state.button_text,
    )

    if submitted:
        try:
            generate_flashcard_set(
                topic_text, additional_instructions, writing_style, complexity_level,
                seed_content, uploaded_file, section_agent_model, num_cards
            )
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            st.session_state.button_disabled = False

    if st.button("View All Flashcards"):
        display_flashcards(st.session_state.flashcards)

    if st.button("Export Flashcards"):
        export_flashcards()

def generate_flashcard_set(topic_text, additional_instructions, writing_style, complexity_level,
                           seed_content, uploaded_file, section_agent_model, num_cards):
    st.session_state.statistics_text = "Generating flashcards..."
    display_statistics(st.session_state.statistics_text)

    total_seed_content = seed_content or ""
    if uploaded_file:
        total_seed_content += uploaded_file.read().decode("utf-8")

    materials = f"""
    Topic: {topic_text}
    Writing Style: {writing_style}
    Complexity Level: {complexity_level}
    Additional Instructions: {additional_instructions}
    Seed Content: {total_seed_content}
    """

    flashcards, stats = generate_flashcards(
        st.session_state.api_key,
        materials,
        num_cards,
        section_agent_model
    )

    st.session_state.flashcards.extend(flashcards)
    save_flashcards(st.session_state.flashcards)

    st.success(f"Generated {len(flashcards)} flashcards")
    st.markdown("## Generation Statistics")
    st.markdown(str(stats))

    display_flashcards(flashcards)

def export_flashcards():
    if st.session_state.flashcards:
        flashcards_json = json.dumps(st.session_state.flashcards, indent=2)
        st.download_button(
            label="Download JSON",
            data=flashcards_json,
            file_name="flashcards.json",
            mime="application/json"
        )
        
        markdown_content = create_flashcards_markdown(st.session_state.flashcards)
        markdown_file = create_markdown_file(markdown_content)
        st.download_button(
            label="Download Flashcards as Markdown",
            data=markdown_file,
            file_name="flashcards.md",
            mime="text/markdown"
        )
        
        pdf_file = create_pdf_file(markdown_content)
        st.download_button(
            label="Download Flashcards as PDF",
            data=pdf_file,
            file_name="flashcards.pdf",
            mime="application/pdf"
        )

        # H5P export option
        h5p_json = create_h5p_json(st.session_state.flashcards, "Flashcard Set")
        st.download_button(
            label="Download H5P content.json",
            data=h5p_json,
            file_name="content.json",
            mime="application/json"
        )

        st.info("To use the H5P content.json file:")
        st.markdown("""
        1. Create a new H5P Dialog Cards content or edit an existing one.
        2. In the H5P editor, click on the "Import" button.
        3. Select the downloaded content.json file.
        4. The flashcards should now be imported into your H5P Dialog Cards content.
        """)
    else:
        st.info("No flashcards to export. Generate some flashcards first!")

if __name__ == "__main__":
    main()
