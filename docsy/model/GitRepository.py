from dataclasses import dataclass
from git import Repo

from docsy.model.Commit import Commit

@dataclass
class GitRepository():
    full_repo_name: str # Only works for github
    branch: str

@dataclass
class LocalGitRepository(GitRepository):
    local_path: str
    _repo: Repo = None

    def __post_init__(self):
        self._repo = Repo(self.local_path)

    def get_last_commit(self) -> Commit:
        return self.get_commits_between('HEAD~', 'HEAD')[0]

    def get_commits_ahead_of_default(self) -> list[Commit]:
        """
        Gets commits that the current branch is ahead of the default branch
        Args:
            default_branch: The name of the default branch (e.g. 'main')
        Returns:
            List of commits that are ahead of the default branch
        """
        # Get the merge base using GitPython
        merge_base = self._repo.merge_base(self._repo.head.commit, self._repo.refs[self.branch].commit)
        return self.get_commits_between(merge_base[0].hexsha, 'HEAD')

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
        for commit in self._repo.iter_commits(f'{from_sha}..{to_sha}'):
            # Get diff with parent
            diff = commit.parents[0].diff(commit, create_patch=True)
            diff_text = '\n'.join(d.diff.decode('utf-8') for d in diff)
            
            commits.append(Commit(
                sha=commit.hexsha,
                message=commit.message.strip(),
                diff=diff_text
            ))
        
        return commits
