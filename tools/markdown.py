"""
Functions to manage markdown content
"""

from io import BytesIO


def create_markdown_file(content: str) -> BytesIO:
    """
    Create a Markdown file from the provided content.
    """
    markdown_file = BytesIO()
    markdown_file.write(content.encode("utf-8"))
    markdown_file.seek(0)
    return markdown_file

def create_flashcards_markdown(flashcards: list) -> str:
    """
    Create a markdown string from a list of flashcards.
    """
    markdown_content = "# Flashcards\n\n"
    for i, card in enumerate(flashcards, 1):
        markdown_content += f"## Flashcard {i}\n\n"
        markdown_content += f"**Question:** {card['question']}\n\n"
        markdown_content += f"**Answer:** {card['answer']}\n\n"
    return markdown_content
