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

    # def _get_suggestion_prompts(self, context: Context) -> list[Prompt]:
    #     suggestions = [c.suggestion for c in context if isinstance(c, Suggestion)]
    #     if len(suggestions) == 0:
    #         return []
    #     else:
    #         return [Prompt(role="system", content="The following suggestions were accepted by the user already:")] + [Prompt(role="user", content=s) for s in accepted_suggestions]

    def get_structure_suggestions(
        self, github_repo_context: GithubRepositoryContext, file_paths: list[str]
    ) -> list[FileSuggestion]:
        prompts = [
            Prompt(
                role="system", content="The following changes are made to the code:"
            ),
            Prompt(role="system", content=str(github_repo_context)),
            Prompt(
                role="system",
                content="The following is the current structure of the documentation:",
            ),
            Prompt(role="system", content="\n".join(file_paths)),
            Prompt(
                role="system",
                content=(
                    "Which files in the documentation needs to be updated to reflect the changes? "
                    "Answer with a JSON object with the following format: "
                    '{"files": [{"path": "path/to/file", "action": "+", "explanation": "explanation of why this file needs to be updated"}]}'
                    "Where 'path' is the path to the file that needs to be updated, and 'action' is '+' if the file should be created, '-' if the file should be deleted, or '~' if the file should be modified."
                    "Explanation is optional, but if provided, it should be a short explanation of which of the code changes require a change to this file. Keep it short."
                    "Do not format your answer as markdown, just return the JSON object."
                ),
            ),
        ]
        suggestion_str = self._get_suggestion(prompts)
        file_suggestions: list[FileSuggestion] = json.loads(suggestion_str)["files"]
        return file_suggestions

    def _convert_slack_thread_to_prompt(self, messages):
        return [
            {
                "role": "assistant" if message[0] == "assistant" else "user",
                "name": message[
                    0
                ],  # this attiribute could be left out for assistant messages (since only docsy is assistant, other bots would simply be users)
                "content": message[1],
            }
            for message in messages
        ]

    def _convert_images_to_prompt(self, image_paths):
        def _encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        return [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"This image was part of the chat conversation. It's available under assets/{os.path.basename(image_path)}. Reference it in the answer if it is relevant to the question.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{_encode_image(image_path)}",
                            "detail": "low",  # Expirement with this. Setting this to high might bring better results
                        },
                    },
                ],
            }
            for image_path in image_paths
        ]

    def get_base_file_name(self, messages):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "system",
                    "content": (
                        "We need a prefix for images that appeared in this thread. This prefix will end up in the file name of the images. Please answer with exactly one suggestion, sticking to lowercase letters and hyphens."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_file_path_suggestion(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "system",
                    "content": "Here is the list of files of the public documentation for the product the conversation is about.",
                },
            ]
            + [{"role": "system", "content": "\n".join(file_paths)}]
            + [
                {
                    "role": "system",
                    "content": (
                        "We need to decide on which page of the documentation the question from the chat conversation should be answered. "
                        "If you think an existing file is best, pick a file path from the above list. "
                        "If no existing file is suitable or if the user wants the information to appear on a new page, answer with a new file path. "
                        "In both cases, only answer with exactly one file path. Include the complete path in a format like it was shown in the list."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_sidebar_content_suggestion(
        self, messages, new_file_path, sidebar_file_content
    ):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "system",
                    "content": f"We want to answer this question in a new file {new_file_path} and need to add it to the sidebar. "
                    "Please suggest a file path for the new file. Only answer with the file path. Stick to the format of the existing file paths.",
                },
                {
                    "role": "system",
                    "content": "Here is how the sidebar file currently looks like.",
                },
                {
                    "role": "system",
                    "content": sidebar_file_content,
                },
                {
                    "role": "system",
                    "content": (
                        "Now repeat the sidebar file line by line and only add a single line with the new file path where you think it fits best. It's very important that you do not leave out any lines that were there before."
                        "We afterwards will open a Pull Request against the public docs and want only meaningful changes in our git history. Only answer with the new file content."
                        "Do not add a codefence at the first line of the file."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_file_content_suggestion(
        self, messages, local_image_paths, file_path, file_content
    ):
        prompt = (
            self.base_prompt
            + self._convert_slack_thread_to_prompt(messages)
            + self._convert_images_to_prompt(local_image_paths)
            + [
                {
                    "role": "system",
                    "content": f"Please modify the file {file_path} to now also answer the question from the chat conversation above.",
                },
                {
                    "role": "system",
                    "content": "Here is how the file currently looks like.",
                },
                {
                    "role": "system",
                    "content": file_content,
                },
                {
                    "role": "system",
                    "content": (
                        "Now repeat the file line by line and only do the minimal edits necessary to answer the question. It's very important that you do not leave out any lines that were there before if not absolutely necesary."
                        "We afterwards will open a Pull Request against the public docs and want only meaningful changes in our git history. Only answer with the new file content."
                        "Do not add a codefence at the first line of the file."
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def get_branch_name_suggestion(self, file_content, file_content_suggestion):
        prompt = self.base_prompt + [
            {
                "role": "system",
                "content": "Please suggest a branch name for the branch that will hold changes to the following file.",
            },
            {
                "role": "system",
                "content": "Here is how the file looked before the change.",
            },
            {
                "role": "system",
                "content": file_content,
            },
            {
                "role": "system",
                "content": "Here is how the file looks after the change.",
            },
            {
                "role": "system",
                "content": file_content_suggestion,
            },
            {
                "role": "system",
                "content": "Only answer with the suggested branch name. Only use lowercase letters and hyphens in the name. Keep the name short, if possible under 4 words.",
            },
        ]
        return self._get_suggestion(prompt)

    def get_next_action(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + [
                {
                    "role": "system",
                    "content": "Here is the list of files of the public documentation of the product.",
                }
            ]
            + [{"role": "system", "content": "\n".join(file_paths)}]
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "system",
                    "content": (
                        "Please decide what you want to do next. "
                        "You can either answer free form or offer to create a pull request (PR). "
                        "Only offer to create a PR if you are confident that the conversation contains enough information to create a meaningful PR. "
                        "If you want to offer the creation of a pull request, answer with SYSTEM_CREATE_PR"
                        "If you want to answer free form, answer with SYSTEM_DISCUSS"
                        "If you haven't said anything in the conversation yet, only answer with SYSTEM_CREATE_PR if the user told you to create a PR in their first message. "
                    ),
                },
            ]
        )
        return self._get_suggestion(prompt)

    def discuss(self, messages, file_paths):
        prompt = (
            self.base_prompt
            + [
                {
                    "role": "system",
                    "content": "Here is the list of files of the public documentation of the product.",
                }
            ]
            + [{"role": "system", "content": "\n".join(file_paths)}]
            + self._convert_slack_thread_to_prompt(messages)
            + [
                {
                    "role": "system",
                    "content": ("Write a response to the chat conversation."),
                },
            ]
        )
        return self._get_suggestion(prompt)


if __name__ == "__main__":
    ai = AI()
    messages = [
        ("Alice", "How do I activate my account?"),
        ("Bob", "Go to settings and click 'Activate Account'."),
    ]
    print(ai.get_file_path_suggestion(messages, ["README.md", "docs/account.md"]))
