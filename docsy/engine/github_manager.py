import os
import tempfile
from loguru import logger
import shutil
from git import Repo, Actor
from github import GithubIntegration, Auth
from pathlib import Path


def get_github_manager_for_team(db, team_id: str):
    customer = db.get_customer(team_id)
    github_app_installation_id = customer.github_app_installation_id
    docs_repo = customer.docs_repo
    content_subdir = customer.content_subdir
    if (not github_app_installation_id) or (not docs_repo) or (not content_subdir):
        raise ValueError(
            "I am missing some bits in the configuration. Please complete the setup in the app home."
        )

    # Docsy uses the same GitHub App independent of who is using it
    GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
    assert GITHUB_APP_ID is not None
    GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")
    assert GITHUB_APP_PRIVATE_KEY is not None

    return GitHubManager(
        docs_repo,
        GITHUB_APP_ID,
        GITHUB_APP_PRIVATE_KEY,
        github_app_installation_id,
        content_subdir=content_subdir,
        base_branch=customer.base_branch,
    )


def get_github_manager_for_repo(github_app_installation_id: int, repo_name: str):
    # Docsy uses the same GitHub App independent of who is using it
    GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
    assert GITHUB_APP_ID is not None
    GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")
    assert GITHUB_APP_PRIVATE_KEY is not None

    return GitHubManager(
        repo_name,
        GITHUB_APP_ID,
        GITHUB_APP_PRIVATE_KEY,
        github_app_installation_id,
    )


def _get_author():
    match os.environ.get("GITHUB_APP_ID"):
        case "907984":
            return Actor(
                "getdocsy-dev[Bot]",
                "171074497+getdocsy-dev[bot]@users.noreply.github.com",
            )
        case "909544":
            return Actor(
                "getdocsy[Bot]",
                "171265091+getdocsy[bot]@users.noreply.github.com",  # Also mentioned in Dockerfile
            )
        case _:
            raise ValueError("Unknown GitHub App ID")


class GitHubManagerException(Exception):
    pass


class GitHubManager:
    def __init__(
        self,
        repo_name: str,
        app_id: str,
        app_private_key: str,
        app_installation_id: int,
        content_subdir="./",
        base_branch="main",
    ):
        appAuth = Auth.AppAuth(app_id, app_private_key.replace("\\n", "\n"))
        gi = GithubIntegration(auth=appAuth)
        self.github = gi.get_github_for_installation(app_installation_id)
        try:
            self.token = gi.get_access_token(app_installation_id).token
        except Exception as e:
            logger.error(f"Failed to clone git repository: {e}")
            raise GitHubManagerException("Failed to get access token")
        self.repo_name = repo_name
        self.github_repo = self.github.get_repo(self.repo_name)
        self.repo, self.repo_path = self._clone_repo()
        self.content_subdir = content_subdir or "./"
        self.asset_subdir = os.path.join(
            self.content_subdir, "assets"
        )  # TODO make configurable
        self.author = _get_author()
        self.base_branch = base_branch or "main"

    def list_md_files(self):
        paths = []
        for path in Path(os.path.join(self.repo_path, self.content_subdir)).rglob(
            "*.md"
        ):
            paths.append(os.path.relpath(path, self.repo_path))
        return paths

    def resolve_file_paths(self, file_paths: list[str]) -> list[str]:
        return [os.path.join(self.repo_path, file_path) for file_path in file_paths]

    def get_file_content(self, relative_file_path):
        file_path = os.path.join(self.repo_path, relative_file_path)
        with open(file_path, "r") as file:
            file_content = file.read()
        return file_content

    def create_branch(
        self,
        branch_name,
    ):
        if self._branch_exists_on_remote(branch_name):
            logger.info(f"Branch '{branch_name}' exists on remote. Checking out...")
            self.repo.git.checkout(branch_name)
        else:
            logger.info(f"Branch '{branch_name}' doesn't exist on remote. Creating...")
            self.repo.git.checkout("-b", branch_name)

    def add_files_to_index(self, file_paths: list[str]):
        self.repo.index.add(file_paths)

    def add_file(
        self,
        relative_file_path,
        file_content,
    ):
        file_path = os.path.join(self.repo_path, relative_file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(file_content)
        self.repo.index.add([file_path])

    def add_image(
        self,
        local_image_path,
    ):
        file_path = os.path.join(
            self.repo_path, self.asset_subdir, os.path.basename(local_image_path)
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        shutil.copyfile(local_image_path, file_path)
        self.repo.index.add([file_path])

    def commit(
        self,
        commit_message,
    ):
        self.repo.index.commit(
            commit_message, author=self.author, committer=self.author
        )

    def push_branch(
        self,
        branch_name,
    ):
        self.repo.git.checkout(branch_name)
        origin = self.repo.remote()
        origin.push(refspec=f"{branch_name}:{branch_name}")
        logger.info(f"Branch '{branch_name}' pushed successfully!")

    def create_pr(self, branch_name, title, body):
        existing_pr = self._get_pr(title)
        if existing_pr:
            logger.info(f"PR '{title}' exists. Nothing to do")
            return existing_pr.html_url
        pr = self.github_repo.create_pull(
            base=self.base_branch, head=branch_name, title=title, body=body
        )
        logger.info(f"PR '{title}' created successfully!")
        return pr.html_url

    def create_comment(self, pull_request_number, comment):
        logger.info(f"Creating comment on PR #{pull_request_number}...")
        pull_request = self.github_repo.get_pull(pull_request_number)
        pull_request.create_issue_comment(comment)

    def _clone_repo(self):
        repo_path = (
            tempfile.mkdtemp()
        )  # TODO better handling of temp directories. This one would need to be cleaned up.
        logger.debug(f"Cloning repository to {repo_path}...")
        repo_url = f"https://x-access-token:{self.token}@github.com/{self.repo_name}"
        repo = Repo.clone_from(repo_url, repo_path, depth=1)
        logger.debug("Finished cloning repository")
        return repo, repo_path

    def get_commits(self, pull_request_number):
        pull_request = self.github_repo.get_pull(pull_request_number)
        return pull_request.get_commits()

    def get_diff(self, base_commit, head_commit):
        return self.repo.git.diff(base_commit, head_commit)

    def _branch_exists_on_remote(self, branch_name):
        branches = [branch.name for branch in self.github_repo.get_branches()]
        return branch_name in branches

    def _get_pr(self, title):
        pulls = self.github_repo.get_pulls()
        for pull in pulls:
            if pull.title == title:
                return pull
        return None

    def close(self):
        self.github.close()


if __name__ == "__main__":
    GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
    GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY")

    ghm = GitHubManager(
        "felixzieger/congenial-computing-machine",
        app_id=GITHUB_APP_ID,
        app_installation_id=51286673,
        app_private_key=GITHUB_APP_PRIVATE_KEY,
        content_subdir="meshcloud-docs/docs/",
    )

    rand = 124

    ghm.create_branch(
        branch_name=f"test-branch-{rand}",
    )
    ghm.add_file(
        relative_file_path="meshcloud-docs/docs/test.md",
        file_content="This is a test file",
    )
    ghm.commit(
        commit_message="Test commit",
    )
    ghm.push_branch(
        branch_name=f"test-branch-{rand}",
    )
    ghm.create_pr(
        branch_name=f"test-branch-{rand}",
        title="Test PR",
        body="This is a test PR",
    )
