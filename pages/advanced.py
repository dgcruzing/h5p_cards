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
import zipfile
import tempfile

# Now import from tools
from tools import create_h5p_json, create_markdown_file, create_pdf_file, create_flashcards_markdown

def check_api_key():
    if "GROQ_API_KEY" in st.session_state and st.session_state.GROQ_API_KEY:
        return True
    
    api_key = st.text_input("Enter your Groq API Key:", type="password")
    if api_key:
        try:
            # Test the API key
            client = Groq(api_key=api_key)
            client.chat.completions.create(
                messages=[{"role": "user", "content": "Test"}],
                model="mixtral-8x7b-32768",
                max_tokens=1
            )
            st.session_state.GROQ_API_KEY = api_key
            return True
        except Exception as e:
            st.error(f"Invalid API key: {str(e)}")
    return False

def generate_flashcards(materials, num_cards=10, model="mixtral-8x7b-32768"):
    client = Groq(api_key=st.session_state.GROQ_API_KEY)
    prompt = f"""Create {num_cards} flashcards based on the following content:

{materials}

Format each flashcard as follows:
Question: [Question]
Answer: [Answer]

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
    content = response.choices[0].message.content.strip()
    card_texts = content.split('\n\n')
    for card_text in card_texts:
        parts = card_text.split('\n')
        if len(parts) == 2:
            question = parts[0].replace("Question: ", "").strip()
            answer = parts[1].replace("Answer: ", "").strip()
            flashcards.append({"question": question, "answer": answer})
    
    return flashcards, {
        "model_name": model,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }

def load_flashcards():
    if 'flashcards' in st.session_state:
        return st.session_state.flashcards
    elif os.path.exists("flashcards.json"):
        with open("flashcards.json", "r") as f:
            return json.load(f)
    return []

def save_flashcards(flashcards):
    st.session_state.flashcards = flashcards
    with open("flashcards.json", "w") as f:
        json.dump(flashcards, f)

def display_statistics(statistics_text):
    st.text(statistics_text)

def display_flashcards(flashcards):
    st.header("Generated Flashcards")
    if flashcards:
        for i, card in enumerate(flashcards, 1):
            with st.expander(f"Flashcard {i}"):
                st.markdown(f"**Question:** {card['question']}")
                st.markdown(f"**Answer:** {card['answer']}")
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
        topic_text,
        additional_instructions,
        writing_style,
        complexity_level,
        seed_content,
        uploaded_file,
        section_agent_model,
        num_cards,
    )

def clear_session_state():
    for key in list(st.session_state.keys()):
        if key != 'GROQ_API_KEY':  # Keep the API key
            del st.session_state[key]
    if os.path.exists("flashcards.json"):
        os.remove("flashcards.json")  # Remove the saved flashcards file

def main():
    st.title("H5P Flashcard Generator")

    if not check_api_key():
        st.stop()

    # Add a refresh button
    if st.button("Refresh Page"):
        clear_session_state()
        st.experimental_rerun()

    # Load existing flashcards or initialize an empty list
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []

    (
        submitted,
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
        button_disabled=st.session_state.get('button_disabled', False),
        button_text=st.session_state.get('button_text', "Generate"),
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
    with st.spinner("Generating flashcards..."):
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
            materials,
            num_cards,
            section_agent_model
        )

        if flashcards:
            # Replace existing flashcards with new ones
            st.session_state.flashcards = flashcards
            save_flashcards(flashcards)
            st.success(f"Generated {len(flashcards)} new flashcards")
            display_flashcards(flashcards)
        else:
            st.warning("No flashcards were generated. Please try again with different inputs.")

        st.markdown("## Generation Statistics")
        st.markdown(f"- Model: {stats['model_name']}")
        st.markdown(f"- Total tokens: {stats['total_tokens']}")

def export_flashcards():
    if st.session_state.flashcards:
        st.write("Debug: Flashcards being exported:")
        st.json(st.session_state.flashcards)

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
        
        try:
            pdf_file = create_pdf_file(markdown_content)
            st.download_button(
                label="Download Flashcards as PDF",
                data=pdf_file,
                file_name="flashcards.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")

        # H5P export option
        h5p_content = create_h5p_json(st.session_state.flashcards, "Flashcard Set")
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create content folder
            content_dir = os.path.join(tmpdirname, "content")
            os.makedirs(content_dir)
            
            # Create content.json in the content folder
            with open(os.path.join(content_dir, "content.json"), "w") as f:
                f.write(h5p_content)

            # Create h5p.json in the root of the package
            h5p_json = {
                "title": "Flashcard Set",
                "language": "en",
                "mainLibrary": "H5P.DialogCards",
                "embedTypes": ["div"],
                "license": "U",
                "preloadedDependencies": [
                    {"machineName": "H5P.DialogCards", "majorVersion": "1", "minorVersion": "9"},
                    {"machineName": "H5P.JoubelUI", "majorVersion": "1", "minorVersion": "3"},
                    {"machineName": "H5P.FontAwesome", "majorVersion": "4", "minorVersion": "5"}
                ]
            }
            with open(os.path.join(tmpdirname, "h5p.json"), "w") as f:
                json.dump(h5p_json, f, indent=2)

            # Create dummy library folders
            libraries = [
                "H5P.DialogCards-1.9",
                "H5P.JoubelUI-1.3",
                "H5P.FontAwesome-4.5"
            ]
            for lib in libraries:
                os.makedirs(os.path.join(tmpdirname, lib))

            # Create ZIP file
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for root, dirs, files in os.walk(tmpdirname):
                    for file in files:
                        file_path = os.path.join(root, file)
                        archive_path = os.path.relpath(file_path, tmpdirname)
                        zip_file.write(file_path, archive_path)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        archive_path = os.path.relpath(dir_path, tmpdirname) + '/'
                        zinfo = zipfile.ZipInfo(archive_path)
                        zip_file.writestr(zinfo, '')

            # Offer the ZIP file for download
            st.download_button(
                label="Download H5P Package",
                data=zip_buffer.getvalue(),
                file_name="flashcards.h5p",
                mime="application/zip"
            )

        st.success("H5P package created successfully.")
        st.info("To use the H5P package:")
        st.markdown("""
        1. Download the H5P package.
        2. Go to your H5P-enabled platform (e.g., Moodle, WordPress with H5P plugin).
        3. Upload the downloaded .h5p file as new H5P content.
        4. The flashcards should now be available as H5P Dialog Cards content.
        """)
    else:
        st.info("No flashcards to export. Generate some flashcards first!")

if __name__ == "__main__":
    main()
