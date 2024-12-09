import json
from loguru import logger
import os
import base64
import textwrap
from openai import OpenAI

AI_MODEL = "gpt-4o-mini"

class BaseAI:
    def __init__(self):

        self.client = OpenAI()
        self.base_prompt = [
            {
                "role": "system",
                "content": (
                    "You are Docsy, a friendly AI coworker. "
                    "Your help the company by improving the public documentation so it answers the questions people have about their product. "
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

    def _get_suggestion(self, prompt) -> str:
        logger.info("Querying AI")
        self._log_prompt(prompt)
        completion = self.client.chat.completions.create(
            model=AI_MODEL, messages=prompt
        )
        suggestion = completion.choices[0].message.content
        logger.info("AI responsed")
        logger.debug(textwrap.shorten(suggestion, width=100, placeholder="..."))
        return suggestion