from dataclasses import dataclass

class Context:
    pass

@dataclass
class GithubRepositoryContext(Context):
    """Represents a GitHub repository.

    Attributes:
        github_repository_name (str): The name of the GitHub repository in format 'owner/repo'
        pull_request_number (int): The number of the pull request being worked on
    """
    github_repository_name: str
    pull_request_number: int
