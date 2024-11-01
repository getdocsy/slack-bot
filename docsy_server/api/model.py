from dataclasses import dataclass
from typing import Union, List

@dataclass
class Commit:
    sha: str
    message: str
    diff: str

    def __str__(self):
        return f"{self.sha[:4]} - {self.message} - {self.diff}"

@dataclass
class GithubRepository():
    github_repo_full_name: str

@dataclass
class GithubRepositoryContext(GithubRepository):
    commits: list[Commit] = None

    def __str__(self):
        commits_str = "\n".join(str(c) for c in self.commits) if self.commits else ""
        return f"{self.github_repo_full_name}\n{commits_str}"

@dataclass
class FileSuggestion:
    path: str
    action: str  # "+|-|~"
    explanation: str
    content: str | None = None

@dataclass
class Suggestion():
    files: list[FileSuggestion]
    target: GithubRepository = None

    def __init__(self, files=None, target=None, **kwargs):
        if files and isinstance(files[0], dict):
            self.files = [FileSuggestion(**f) for f in files]
        else:
            self.files = files or []
        self.target = target

    def get_file_paths(self) -> list[str]:
        return [file.path for file in self.files]

    def export_to_cli_format(self) -> dict:
        return {
            "files": self.files
        }
