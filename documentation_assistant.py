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
                    "You are a friendly AI coworker. "
                    "Your help our company by improving our public documentation so it answers the questions people have about our product. "
                    "As input, you will receive chat conversations where someone asks a questions and someone answers the question. "
                ),
            },
        ]
        self.writing_prompt = []

    def get_file_path_suggestion(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + [
                {"role": "user", "name": message[0], "content": message[1]}
                for message in messages
            ]
            + [
                {
                    "role": "system",
                    "content": "Here is the list of files of the public documentation for our product.",
                },
            ]
            + [{"role": "system", "content": file_path} for file_path in file_paths]
            + [
                {
                    "role": "system",
                    "content": (
                        "Pick exactly one file path from the above list where you think the question from the chat conversation should be answered. Only answer with the file path."
                    ),
                },
            ]
        )
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=prompt
        )
        return completion.choices[0].message.content

    def get_file_content_suggestion(self, messages, file_path, file_content):
        prompt = (
            self.base_prompt
            + [
                {"role": "user", "name": message[0], "content": message[1]}
                for message in messages
            ]
            + [
                {
                    "role": "system",
                    "content": f"We are expanding file {file_path} to now answer the question from the chat conversation above.",
                },
                {
                    "role": "system",
                    "content": "Here is how the file currently looks like.",
                },
                {
                    "role": "system",
                    "content": file_content,
                },
            ]
            + [
                {
                    "role": "system",
                    "content": (
                        "Modify the above markdown file. Keep the edits as minimal as possible while still answering the question. We afterwards will open a Pull Request against the public docs and want only meaningful changes in our git history."
                    ),
                },
            ]
        )
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=prompt
        )
        return completion.choices[0].message.content


if __name__ == "__main__":
    assistant = DocumentationAssistant()
    messages = [
        ("Alice", "How do I activate my account?"),
        ("Bob", "Go to settings and click 'Activate Account'."),
    ]
    print(assistant.get_suggestion(messages))
