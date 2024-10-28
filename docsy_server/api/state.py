from dataclasses import dataclass

class State:
    pass

@dataclass
class GithubRepositoryState(State):
    """Represents a GitHub repository at a specific commit.

    Attributes:
        github_repository_name (str): The name of the GitHub repository in format 'owner/repo'
        branch (str): The branch name in the repository being worked with
    """
    github_repository_name: str
    branch: str
