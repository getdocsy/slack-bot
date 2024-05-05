import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class DocumentationAssistant:
    def __init__(self):
        self.client = OpenAI()
        self.base_prompt = [
            {
                "role": "system",
                "content": (
                    "You are my friendly AI coworker. "
                    "Your help our company by writing public documentation that answers the questions people have about our product. "
                    "As input, you will receive chat conversations where someone asks a questions and someone answers the question and a markdown file that should answer the question but doesn't yet. "
                    "Exclusively write about what is in the product today. Do not include anything about features that are not implemented yet. Use active voice and present tense."
                ),
            },
        ]

    def get_suggestion(self, messages):
        prompt = self.base_prompt + [
            {"role": "user", "name": message[0], "content": message[1]}
            for message in messages
        ]
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=prompt
        )
        return completion.choices[0].message.content

    # Example of adding another method that might use a different prompt or settings
    def get_advanced_suggestion(self, messages, extra_instructions):
        prompt = (
            self.base_prompt
            + [{"role": "system", "content": extra_instructions}]
            + [
                {"role": "user", "name": message[0], "content": message[1]}
                for message in messages
            ]
        )
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=prompt
        )
        return completion.choices[0].message.content


# Example usage
if __name__ == "__main__":
    assistant = DocumentationAssistant()
    messages = [
        ("Alice", "How do I activate my account?"),
        ("Bob", "Go to settings and click 'Activate Account'."),
    ]
    print(assistant.get_suggestion(messages))
    print(
        assistant.get_advanced_suggestion(
            messages, "Include details on navigating the user interface."
        )
    )
