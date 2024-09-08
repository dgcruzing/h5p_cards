# H5P Flashcard Generator

This project is a Streamlit-based application that allows users to generate flashcards using AI and export them in various formats, including H5P-compatible JSON for use in H5P Dialog Cards.

## Features

- Generate flashcards using AI (powered by Groq)
- Customize flashcard generation with various parameters
- Export flashcards in multiple formats (JSON, Markdown, PDF, H5P)
- View generated flashcards within the application

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/h5p-flashcard-generator.git
   cd h5p-flashcard-generator
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Set up your Groq API key:
   - Create a `.env` file in the project root
   - Add your Groq API key: `GROQ_API_KEY=your_api_key_here`

2. Run the Streamlit app:
   ```bash
   streamlit run pages/advanced.py
   ```

3. Open your web browser and go to `http://localhost:8501`

4. Use the interface to:
   - Enter your flashcard set details
   - Generate flashcards
   - View generated flashcards
   - Export flashcards in various formats

## Exporting to H5P

1. After generating flashcards, click the "Export Flashcards" button.
2. Download the "H5P content.json" file.
3. In your H5P authoring tool:
   - Create a new H5P Dialog Cards content or edit an existing one
   - Click the "Import" button
   - Select the downloaded content.json file
   - The flashcards should now be imported into your H5P Dialog Cards content

## Project Structure

- `pages/advanced.py`: Main Streamlit application
- `tools/`: Utility functions for file operations and H5P export
- `ui/`: User interface components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.