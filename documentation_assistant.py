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

    def _get_suggestion(self, prompt):
        logging.debug(prompt)
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=prompt
        )
        suggestion = completion.choices[0].message.content
        logging.debug(suggestion)
        return suggestion

    def _convert_slack_thread_to_prompt(self, messages):
        return [
            {"role": "user", "name": message[0], "content": message[1]}
            for message in messages
        ]

    def get_file_path_suggestion(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
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
                        "Pick exactly one file path from the above list where you think the question from the chat conversation should be answered. Only answer with the file path. Include the complete path that was shown in the list."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_file_content_suggestion(self, messages, file_path, file_content):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "system",
                    "content": f"Please modify the markdown file {file_path} to now also answer the question from the chat conversation above.",
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
                        "Modify the markdown file and give out the complete file again. Keep the edits as minimal as possible while still answering the question. We afterwards will open a Pull Request against the public docs and want only meaningful changes in our git history. Only answer with the markdown file."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    assistant = DocumentationAssistant()
    messages = [
        ("Alice", "How do I activate my account?"),
        ("Bob", "Go to settings and click 'Activate Account'."),
    ]
    print(
        assistant.get_file_path_suggestion(messages, ["README.md", "docs/account.md"])
    )
