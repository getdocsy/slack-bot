import os
import tempfile
import logging
from git import Repo
from github import Github, Auth
from pathlib import Path


class GitHubManager:
    def __init__(self, repo_name, username, token):
        self.repo_name = repo_name
        self.username = username
        self.token = token
        self.auth = Auth.Token(self.token)
        self.github = Github(auth=self.auth)
        self.repo, self.repo_path = self._clone_repo()

    # def fork_repo(self, source_repo):
    #     repo = self.github.get_repo(source_repo)
    #     fork = self.github.get_user().create_fork(repo).full_name
    #     return fork

    def list_md_files(self, subdir="meshcloud-docs/docs/"):
        paths = []
        for path in Path(os.path.join(self.repo_path, subdir)).rglob("*.md"):
            paths.append(os.path.relpath(path, self.repo_path))
        return paths

    def get_file_content(self, relative_file_path):
        file_path = os.path.join(self.repo_path, relative_file_path)
        with open(file_path, "r") as file:
            file_content = file.read()
        return file_content

    def create_branch(
        self,
        relative_file_path,
        file_content,
        branch_name="docsy",
        commit_message="first commit",
    ):
        if self._branch_exists(branch_name, self.repo):
            self.repo.git.checkout(branch_name)
        else:
            self.repo.git.checkout("-b", branch_name)
        file_path = os.path.join(self.repo_path, relative_file_path)
        with open(file_path, "w") as file:
            file.write(file_content)
        self.repo.index.add([file_path])
        self.repo.index.commit(commit_message)
        origin = self.repo.remote()
        origin.push()
        logging.info(f"Branch '{branch_name}' pushed successfully!")

    def create_pr(self, title, body="A small step for me, a big step for me"):
        if self._pr_exists(title):
            logging.info(f"PR '{title}' exists. Nothing to do")
            return None
        pr = self.github.get_repo(self.repo_name).create_pull(
            base="main", head="docsy", title=title, body=body
        )
        return pr.html_url

    def _clone_repo(self):
        repo_path = tempfile.mkdtemp() # TODO better handling of temp directories. This one would need to be cleaned up.
        repo_url = f"https://{self.username}:{self.token}@github.com/{self.repo_name}"
        repo = Repo.clone_from(repo_url, repo_path)
        return repo, repo_path

    def _branch_exists(self, branch_name, repo):
        branches = [branch.name for branch in repo.get_branches()]
        return branch_name in branches

    def _pr_exists(self, title):
        repo = self.github.get_repo(self.repo_name)
        pulls = repo.get_pulls()
        return title in [pull.title for pull in pulls]

    def close(self):
        self.github.close()


def main():
    logging.basicConfig(level=logging.INFO)
    gitHubManager = GitHubManager(
        "felixzieger/congenial-computing-machine",
        "felixzieger",
        os.environ.get("GITHUB_TOKEN"),
    )
    print(gitHubManager.get_file_content("README.md"))


if __name__ == "__main__":
    main()
