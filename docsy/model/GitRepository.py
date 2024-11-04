from dataclasses import dataclass
import subprocess

from docsy.model.Commit import Commit

@dataclass
class GitRepository():
    full_repo_name: str # Only works for github
    branch: str

@dataclass
class LocalGitRepository(GitRepository):
    local_path: str

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
        # Get the merge base (common ancestor) between current HEAD and default branch
        merge_base_result = subprocess.run(
            ["git", "-C", self.local_path, "merge-base", "HEAD", self.branch],
            capture_output=True,
            text=True,
            cwd=self.local_path
        )
        merge_base = merge_base_result.stdout.strip()

        # Get commits between merge base and HEAD
        return self.get_commits_between(merge_base, 'HEAD')

    def get_commits_between(self, from_sha: str, to_sha: str) -> list[Commit]:
        """
        Gets a list of commits between two SHAs
        Args:
            from_sha: Starting SHA (older). This SHA will not be included in the result.
            to_sha: Ending SHA (newer). This SHA will be included in the result.
        Returns:
            List of commits between the two SHAs. Empty list if the SHAs are the same.
        """
        # Get list of commit SHAs and messages between from_sha and to_sha
        log_result = subprocess.run(
            ["git", "-C", self.local_path, "log", "--format=%H%n%s", f"{from_sha}..{to_sha}"],
            capture_output=True,
            text=True,
            cwd=self.local_path
        )
        commit_info = [line for line in log_result.stdout.strip().split('\n') if line]

        # Group SHA and message pairs
        commits = []
        for i in range(0, len(commit_info), 2):
            sha = commit_info[i]
            message = commit_info[i + 1]
            
            # Get diff to parent
            diff_result = subprocess.run(
                ["git", "-C", self.local_path, "diff", f"{sha}~", sha], # ~ is a shortcut for parent. see https://gitirc.eu/gitrevisions.html
                capture_output=True,
                text=True,
                cwd=self.local_path
            )
            diff = diff_result.stdout.strip()
            
            commits.append(Commit(sha=sha, message=message, diff=diff))
        
        return commits
