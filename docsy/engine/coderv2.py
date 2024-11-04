from aider.coders import Coder as AiderCoder
from aider.models import Model
from aider.io import InputOutput
from loguru import logger
from docsy.model.GitRepository import Commit, LocalGitRepository

AIDER_MODEL = Model("gpt-4o-mini")
io = InputOutput(yes=True) # automatically confirm all prompts
   

class DocsyCoder:
    def __init__(self, target_repo: LocalGitRepository):
        self.target_repo = target_repo

    def _get_suggest_prompt(self, source_commits: list[Commit]) -> str:
        return (
            "/ask" + "\n"
            "These changes are made to the code of our application:\n"
            f"{str(source_commits)}\n"
            "Are changes to the documentation needed?\n"
            "If so, which files in the documentation need to be updated to reflect the changes? List the paths of the files."
        )

    def suggest(self, source_commits: list[Commit]):
        prompt = self._get_suggest_prompt(source_commits)
        logger.info(f"Running with prompt: {prompt}")
        coder = AiderCoder.create(main_model=AIDER_MODEL, io=io)
        coder.run(prompt)
        # TODO parse the output and return the FileSuggestions