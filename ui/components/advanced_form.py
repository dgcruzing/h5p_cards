import streamlit as st

MODEL_LIST = ["llama3-70b-8192", "llama3-8b-8192", "gemma2-9b-it"]

def render_advanced_groq_form(on_submit, button_disabled=False, button_text="Generate Chapter"):
    st.sidebar.title("Select AI Models")

    # Sidebar content
    with st.sidebar:
        st.warning(
            "🚧 Advanced Mode is in beta: You're using a version with experimental features."
        )

        st.markdown("### For creating chapter content:")
        section_agent_model = st.selectbox(
            "Section Agent Model",
            MODEL_LIST,
            index=1,
            help="Generates content for the chapter using the 5E Instructional Model",
        )

    with st.form("groqform"):
        st.info(
            "You are using advanced mode with additional features. Visit [here](/) to use the streamlined version."
        )

        if not st.session_state.get("api_key"):
            st.subheader("API Key")
            groq_input_key = st.text_input(
                "Enter your Groq API Key (gsk_yA...):", "", type="password"
            )
        else:
            groq_input_key = None

        st.subheader("Chapter Details")
        subject = st.text_input("Subject", help="Enter the main subject of the course")
        element = st.text_input("Element", help="Enter the specific element being addressed")
        performance_criteria = st.text_input("Performance Criteria", help="Enter the performance criteria for this chapter")
        topic = st.text_input("Topic", help="Enter the main topic of this chapter")

        st.subheader("Chapter Title")
        topic_text = st.text_input(
            "What do you want the chapter to be about?",
            value="",
            help="Enter the main topic or title of your chapter",
        )

        st.subheader("Additional Instructions")
        additional_instructions = st.text_area(
            "Provide any specific guidelines or preferences for the chapter's content",
            placeholder="E.g., 'Focus on beginner-friendly content', 'Include case studies', etc.",
            value="",
        )

        col1, col2 = st.columns(2)
        with col1:
            writing_style = st.selectbox(
                "Writing Style", ["Casual", "Formal", "Academic", "Creative"]
            )
        with col2:
            complexity_level = st.select_slider(
                "Complexity Level",
                options=["Beginner", "Intermediate", "Advanced", "Expert"],
            )

        st.subheader("Seed Content")
        seed_content = st.text_area(
            "Provide any existing notes or content to be incorporated into the chapter",
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
        subject,
        element,
        performance_criteria,
        topic,
    )