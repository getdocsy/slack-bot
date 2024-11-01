from aider.coders import Coder as AiderCoder
from aider.models import Model
from aider.io import InputOutput
from loguru import logger
from docsy_server.api.model import Suggestion, GithubRepositoryContext
from docsy_server.engine.github_manager import GitHubManager

AIDER_MODEL = Model("gpt-4o-mini")
io = InputOutput(yes=True) # automatically confirm all prompts
   

class DocsyCoder:
    def __init__(self, github_manager: GitHubManager):
        self.github_manager = github_manager

    def _get_prompt(self, suggestion: Suggestion, context: GithubRepositoryContext) -> str:
        return (
                "These changes are made to the code of our application:\n"
                f"{str(context)}\n"
                "The user has agreed to the following changes to the documentation: \n"
                f"{str(suggestion)}\n"
                "Apply the changes to the documentation."
        )

    def apply(self, suggestion: Suggestion, context: GithubRepositoryContext) -> dict:
        branch_name = f"docsy-suggestion"
        self.github_manager.create_branch(branch_name)

        file_paths = self.github_manager.resolve_file_paths(suggestion.get_file_paths())
        coder = AiderCoder.create(main_model=AIDER_MODEL, fnames=file_paths, io=io)
        prompt = self._get_prompt(suggestion, context)
        logger.info(f"Running with prompt: {prompt}")
        coder.run(prompt) # commits changes automatically

        self.github_manager.push_branch(branch_name)
