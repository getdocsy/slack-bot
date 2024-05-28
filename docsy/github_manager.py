import os
import tempfile
import logging
from git import Repo
from github import GithubIntegration, Auth
from pathlib import Path


class GitHubManager:
    def __init__(
        self,
        repo_name: str,
        app_id,
        app_private_key,
        app_installation_id,
    ):
        appAuth = Auth.AppAuth(app_id, app_private_key)
        gi = GithubIntegration(auth=appAuth)
        self.github = gi.get_github_for_installation(app_installation_id)
        self.token = gi.get_access_token(app_installation_id).token
        self.repo_name = repo_name
        self.github_repo = self.github.get_repo(self.repo_name)
        self.repo, self.repo_path = self._clone_repo()

    # def fork_repo(self, source_repo):
    #     fork = self.github.get_user().create_fork(self.github_repo).full_name
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
        branch_name,
        commit_message="first commit",
    ):
        if self._branch_exists(branch_name):
            logging.info(f"Branch '{branch_name}' exists. Checking out...")
            self.repo.git.checkout(branch_name)
        else:
            logging.info(f"Branch '{branch_name}' doesn't exist. Creating...")
            self.repo.git.checkout("-b", branch_name)
        file_path = os.path.join(self.repo_path, relative_file_path)
        with open(file_path, "w") as file:
            file.write(file_content)
        self.repo.index.add([file_path])
        self.repo.index.commit(commit_message)

        origin = self.repo.remote()
        origin.push(refspec=f"{branch_name}:{branch_name}")
        logging.info(f"Branch '{branch_name}' pushed successfully!")

    def create_pr(self, branch_name, title, body):
        if self._pr_exists(title):
            logging.info(f"PR '{title}' exists. Nothing to do")
            return None
        pr = self.github_repo.create_pull(
            base="main", head=branch_name, title=title, body=body
        )
        return pr.html_url

    def _clone_repo(self):
        repo_path = tempfile.mkdtemp()  # TODO better handling of temp directories. This one would need to be cleaned up.
        logging.debug(f"Cloning repository to {repo_path}...")
        repo_url = f"https://x-access-token:{self.token}@github.com/{self.repo_name}"
        repo = Repo.clone_from(repo_url, repo_path)
        return repo, repo_path

    def _branch_exists(self, branch_name):
        branches = [branch.name for branch in self.github_repo.get_branches()]
        return branch_name in branches

    def _pr_exists(self, title):
        pulls = self.github_repo.get_pulls()
        return title in [pull.title for pull in pulls]

    def close(self):
        self.github.close()


def main():
    GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
    GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")
    GITHUB_APP_INSTALLATION_ID = int(
        os.environ.get("GITHUB_APP_INSTALLATION_ID") or 0
    )  # We need an int but can't be sure the env variable is set at all. There is surely something nicer, but good enough for now.

    gitHubManager = GitHubManager(
        "felixzieger/congenial-computing-machine",
        GITHUB_APP_ID,
        GITHUB_APP_PRIVATE_KEY,
        GITHUB_APP_INSTALLATION_ID,
    )

    gitHubManager.create_branch("README.md", "Hi there", "testing_new_branches")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
