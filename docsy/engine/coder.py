from aider.coders import Coder as AiderCoder
from aider.models import Model
from aider.io import InputOutput
from loguru import logger
from docsy.api.model import FileSuggestion, Suggestion, GithubRepositoryContext
from docsy.engine.github_manager import GitHubManager

AIDER_MODEL = Model("gpt-4o-mini")
io = InputOutput(yes=True) # automatically confirm all prompts
   

class DocsyCoder:
    def __init__(self, github_manager: GitHubManager):
        self.github_manager = github_manager

    def _get_apply_prompt(self, suggestion: Suggestion, context: GithubRepositoryContext) -> str:
        return (
                "These changes are made to the code of our application:\n"
                f"{str(context)}\n"
                "The user has agreed to the following changes to the documentation: \n"
                f"{str(suggestion)}\n"
                "Apply the changes to the documentation."
        )

    def _get_suggest_prompt(self, github_repo_context: GithubRepositoryContext, file_paths: list[str]) -> str:
        return (
            "/ask" + "\n"
            "The following changes are made to the code:" + str(github_repo_context) + "\n"
            "This is the current structure of the documentation:" + "\n".join(file_paths) + "\n"
            "Which files in the documentation need to be updated to reflect the changes? " + "\n"
            "Answer with a JSON object with the following format: " + "\n"
            "{\"files\": [{\"path\": \"path/to/file\", \"action\": \"+\", \"explanation\": \"explanation of why this file needs to be updated\"}]}" + "\n"
            "Where 'path' is the path to the file that needs to be updated, and 'action' is '+' if the file should be created, '-' if the file should be deleted, or '~' if the file should be modified." + "\n"
            "Explanation is optional, but if provided, it should be a short explanation of which of the code changes require a change to this file. Keep it short." + "\n"
            "Do not format your answer as markdown, just return the JSON object."
        )

    def suggest(self, github_repo_context: GithubRepositoryContext, file_paths: list[str]) -> list[FileSuggestion]:
        prompt = self._get_suggest_prompt(github_repo_context, file_paths)
        logger.info(f"Running with prompt: {prompt}")
        file_paths = self.github_manager.resolve_file_paths(file_paths)
        coder = AiderCoder.create(main_model=AIDER_MODEL, fnames=file_paths, io=io)
        coder.run(prompt)
        # TODO parse the output and return the FileSuggestions
        
    def apply(self, suggestion: Suggestion, context: GithubRepositoryContext) -> dict:
        branch_name = f"docsy-suggestion"
        self.github_manager.create_branch(branch_name)

        file_paths = self.github_manager.resolve_file_paths(suggestion.get_file_paths())
        coder = AiderCoder.create(main_model=AIDER_MODEL, fnames=file_paths, io=io)
        prompt = self._get_apply_prompt(suggestion, context)
        logger.info(f"Running with prompt: {prompt}")
        coder.run(prompt) # commits changes automatically
