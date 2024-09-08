from .h5p_export import create_h5p_json
from .markdown import create_markdown_file, create_flashcards_markdown
from .pdf import create_pdf_file

import json
from io import BytesIO
from markdown import markdown
from weasyprint import HTML, CSS

def create_h5p_json(flashcards, title):
    h5p_content = {
        "title": f"<p>{title}</p>",
        "mode": "normal",
        "description": "<p>These cards are designed to help you learn and memorize the key concepts. Try to answer from memory before flipping the cards.</p>",
        "dialogs": [],
        "behaviour": {
            "enableRetry": True,
            "disableBackwardsNavigation": False,
            "scaleTextNotCard": False,
            "randomCards": True,
            "maxProficiency": 5,
            "quickProgression": False
        },
        "answer": "Turn",
        "next": "Next",
        "prev": "Previous",
        "retry": "Try again",
        "correctAnswer": "I got it right!",
        "incorrectAnswer": "I got it wrong",
        "round": "Round @round",
        "cardsLeft": "Cards left: @number",
        "nextRound": "Proceed to round @round",
        "startOver": "Start over",
        "showSummary": "Next",
        "summary": "Summary",
        "summaryCardsRight": "Cards you got right:",
        "summaryCardsWrong": "Cards you got wrong:",
        "summaryCardsNotShown": "Cards in pool not shown:",
        "summaryOverallScore": "Overall Score",
        "summaryCardsCompleted": "Cards you have completed learning:",
        "summaryCompletedRounds": "Completed rounds:",
        "summaryAllDone": "Well done! You got all @cards cards correct @max times in a row!",
        "progressText": "Card @card of @total",
        "cardFrontLabel": "Card front",
        "cardBackLabel": "Card back",
        "tipButtonLabel": "Show tip",
        "audioNotSupported": "Your browser does not support this audio",
        "confirmStartingOver": {
            "header": "Start over?",
            "body": "All progress will be lost. Are you sure you want to start over?",
            "cancelLabel": "Cancel",
            "confirmLabel": "Start over"
        }
    }

    for card in flashcards:
        h5p_content["dialogs"].append({
            "tips": [],
            "text": f"<p style=\"text-align: center;\">{card['question']}</p>",
            "answer": f"<p style=\"text-align: center;\">{card['answer']}</p>"
        })

    return json.dumps(h5p_content, indent=2)
