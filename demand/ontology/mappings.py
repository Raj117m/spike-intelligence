"""
Maps raw concepts into canonical ontology concepts.
"""

from __future__ import annotations

from .concepts import CANONICAL

MAP = {
    # AI
    "Artificial Intelligence Industry In The United States": "Artificial Intelligence",
    "Artificial Intelligence": "Artificial Intelligence",
    "Large Language Models": "Generative AI",
    "Large Models": "Generative AI",
    "Generative Pre Trained Transformers": "Generative AI",
    "Chatbots": "Conversational AI",
    "Chatgpt": "Conversational AI",

    # Software
    "Software": "Software",
    "Microsoft Store": "Software",
    "Websites": "Software",
    "Consumer Software": "Consumer Software",
    "Productivity Software": "Productivity Software",

    # Sports
    "Association Football": "Sports",
    "Football": "Sports",
    "Olympics": "Sports",

    # Entertainment
    "Films": "Entertainment",
    "Television": "Entertainment",
    "Streaming": "Entertainment",

    # Retail
    "Shopping": "Retail",
    "E Commerce": "Retail",
}


def canonicalize(name: str) -> str:
    """
    Convert a noisy concept into a canonical ontology concept.
    """

    if name in MAP:
        return MAP[name]

    if name in CANONICAL:
        return name

    return name
