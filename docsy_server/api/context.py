from dataclasses import dataclass

class Context:
    pass

@dataclass
class Commit:
    sha: str
    message: str
    diff: str

    def __str__(self):
        return f"{self.sha[:4]} - {self.message} - {self.diff}"

@dataclass
class GithubRepositoryContext(Context):
    github_repo_full_name: str
    commits: list[Commit] = None

    def __str__(self):
        commits_str = "\n".join(str(c) for c in self.commits) if self.commits else ""
        return f"{self.github_repo_full_name}\n{commits_str}"

@dataclass
class DocsySuggestionContext(Context):
    """Represents a Docsy suggestion.

    Attributes:
        suggestion (str): The suggestion to be made
        context (list[GithubRepositoryContext]): The context of the suggestion
    """
    suggestion: str
    context: list[GithubRepositoryContext]
