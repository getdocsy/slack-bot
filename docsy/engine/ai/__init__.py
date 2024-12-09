import json
from loguru import logger
import os
import base64
import textwrap
from openai import OpenAI
from typing import TypedDict, Literal
from docsy.api.model import (
    GithubRepositoryContext,
    FileSuggestion,
    GithubRepository,
    Suggestion,
)

AI_MODEL = "gpt-4o-mini"


class Prompt(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str
    # name: str | None


class AI:
    def __init__(self):

        self.client = OpenAI()
        self.base_prompt = [
            {
                "role": "system",
                "content": (
                    "You are Docsy, a friendly AI bot. "
                    "Your are an expert at analyzing documentation for software products. "
                ),
            },
        ]

    def _log_prompt(self, prompt):
        for message in prompt:
            content = (
                message["role"]
                + ": "
                + textwrap.shorten(message["content"], width=90, placeholder="...")
            )
            logger.debug(content)

    def analyze(self, url: str) -> str:
        logger.info("Querying AI")
        self._log_prompt(prompt)
        completion = self.client.chat.completions.create(
            model=AI_MODEL, messages=prompt
        )
        suggestion = completion.choices[0].message.content
        logger.info("AI responsed")
        logger.debug(textwrap.shorten(suggestion, width=100, placeholder="..."))
        return suggestion


if __name__ == "__main__":
    ai = AI()
    messages = [
        ("Alice", "How do I activate my account?"),
        ("Bob", "Go to settings and click 'Activate Account'."),
    ]
    print(ai.get_file_path_suggestion(messages, ["README.md", "docs/account.md"]))
