from dataclasses import dataclass
import os
import re
from git import Repo, Commit as GitCommit

from docsy.model.commit import Commit


@dataclass
class GitRepository:
    full_repo_name: str  # Only works for github
    default_branch: str


@dataclass
class LocalGitRepository(GitRepository):
    local_path: str
    _repo: Repo = None

    def __post_init__(self):
        self._repo = Repo(self.local_path)

    def is_dirty(self) -> bool:
        return self._repo.is_dirty()

    def get_last_commit(self) -> Commit:
        return self.get_commits_between("HEAD~", "HEAD")[0]

    def get_commit(self, sha: str) -> Commit:
        return self.format_commit(self._repo.commit(sha))

    def get_current_branch(self) -> str:
        return self._repo.active_branch.name

    def get_commits_ahead_of_default(self) -> list[Commit]:
        """
        Gets commits that the current branch is ahead of the default branch
        Args:
            default_branch: The name of the default branch (e.g. 'main')
        Returns:
            List of commits that are ahead of the default branch
        """
        # Get the merge base using GitPython
        merge_base = self._repo.merge_base(
            self._repo.head.commit, self._repo.refs[self.default_branch].commit
        )
        return self.get_commits_between(merge_base[0].hexsha, "HEAD")

    def get_commits_between(self, from_sha: str, to_sha: str) -> list[Commit]:
        """
        Gets a list of commits between two SHAs
        Args:
            from_sha: Starting SHA (older). This SHA will not be included in the result.
            to_sha: Ending SHA (newer). This SHA will be included in the result.
        Returns:
            List of commits between the two SHAs. Empty list if the SHAs are the same.
        """
        commits = []
        for commit in self._repo.iter_commits(f"{from_sha}..{to_sha}"):
            commits.append(self.format_commit(commit))
        return commits

    def format_commit(self, commit: GitCommit) -> Commit:
        diff = commit.parents[0].diff(commit, create_patch=True)
        diff_text = "\n".join(d.diff.decode("utf-8") for d in diff)
        return Commit(sha=commit.hexsha, message=commit.message.strip(), diff=diff_text)

    def get_md_files_with_headings(self) -> list[tuple[str, list[str]]]:
        files = self.list_files(filetype="md")
        return [(file, self.get_md_file_headings(file)) for file in files]

    def list_files(self, filetype: str = None) -> list[str]:
        files = []
        for entry in self._repo.commit().tree.traverse():
            if entry.type == "blob" and (
                filetype is None or entry.path.endswith(f".{filetype}")
            ):
                files.append(entry.path)
        return files

    def get_md_file_headings(self, file_path: str) -> list[str]:
        file_content = self.get_file_content(file_path)
        return re.findall(r"^#+\s+(.*)$", file_content, re.MULTILINE)

    def get_file_content(self, file_path: str) -> str:
        return open(os.path.join(self.local_path, file_path)).read()

    def write_file(self, file_path: str, file_content: str):
        with open(os.path.join(self.local_path, file_path), "w") as file:
            file.write(file_content)
