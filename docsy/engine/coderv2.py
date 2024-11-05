import textwrap
from openai import OpenAI
from loguru import logger
from docsy.model.prompt import Prompt
from docsy.model.repo import Commit, LocalGitRepository

AI_MODEL = "gpt-4o-mini"

class DocsyCoder:
    def __init__(self, target_repo: LocalGitRepository):
        self.target_repo = target_repo
        
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
            content = message["role"] + ": " + textwrap.shorten(message["content"], width=90, placeholder="...")
            logger.debug(content)

    def _get_suggestion(self, prompt: list[Prompt]) -> str:
        logger.info("Querying AI")
        self._log_prompt(prompt)
        completion = self.client.chat.completions.create(
            model=AI_MODEL, messages=prompt
        )
        suggestion = completion.choices[0].message.content
        logger.info("AI responsed")
        logger.debug(textwrap.shorten(suggestion, width=100, placeholder="..."))
        return suggestion

    def summarize_changes(self, source_commits: list[Commit]):
        prompt = [
            {"role": "system", "content": 
                "These changes are made to the code of our application:\n"
                f"{str(source_commits)}\n"
            },
            {"role": "system", "content": 
                "Please summarize the changes. Focus on the intent of the changes, not the exact code. "
                "If you can, explain the scope of the changes. For example: These changes only affect the CLI."
                "This will be used to update the documentation, so focus on the changes to the user-facing parts of the code."
            }
        ]
        return self._get_suggestion(prompt)


    def suggest(self, source_commits: list[Commit]):
        target_files_with_headings = self.target_repo.get_md_files_with_headings()
        summary = self.summarize_changes(source_commits)

        prompt = [
            {"role": "system", "content": 
                f"These are the changes that were made to the code:\n{summary}\n"
            },
            {"role": "system", "content": 
                "Here is a list of all the files in our documentation and their headings:\n"
                f"{target_files_with_headings}\n"
            },
            {"role": "system", "content": 
                "Are changes to the documentation needed?\n"
                "If so, which files in the documentation need to be updated to reflect the changes? List the paths of the files."
            }
        ]
        return self._get_suggestion(prompt)
