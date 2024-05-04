import os
import tempfile
from git import Repo
from github import Github
from github import Auth

import logging

logger = logging.getLogger(__name__)

def fork_repo(source_repo = "Janos95/kdtree"):
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)
    github_user = g.get_user()
    repo = g.get_repo(source_repo)
    fork = github_user.create_fork(repo).full_name
    g.close()
    return fork



def create_branch(
    file_content,
    branch_name="docsy",
    commit_message="first commit",
    relative_file_path="README.md",
):
    with tempfile.TemporaryDirectory() as repo_path:
        logging.info(f"Created temporary directory {repo_path}")

        username = "felixzieger"
        token = os.environ.get("GITHUB_TOKEN")
        repo_url = f"https://{username}:{token}@github.com/felixzieger/congenial-computing-machine.git"
        repo = Repo.clone_from(repo_url, repo_path)

        if branch_exists(branch_name):
            logging.info(f"Branch '{branch_name}' already exists. Checking out...")
            repo.git.checkout(branch_name)
        else:
            logging.info(f"Branch '{branch_name}' doesn't exist yet. Creating...")
            repo.git.checkout("-b", branch_name)

        file_path = os.path.join(repo_path, relative_file_path)
        with open(file_path, "w") as file:
            file.write(file_content)

        repo.index.add([file_path])
        repo.index.commit(commit_message)

        origin = repo.remote()
        origin.push()

        logging.info(f"Branch '{branch_name}' pushed successfully!")


def branch_exists(branch_name):
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)
    repo = g.get_repo("felixzieger/congenial-computing-machine")
    branches = [branch.name for branch in repo.get_branches()]
    g.close()
    return branch_name in branches


def pr_exists(title):
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)
    repo = g.get_repo("felixzieger/congenial-computing-machine")
    pulls = repo.get_pulls()
    g.close()
    return title in [pull.title for pull in pulls]


def create_pr(title):
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)
    repo = g.get_repo("felixzieger/congenial-computing-machine")
    if pr_exists(title):
        logging.info(f"PR '{title}' exists. Nothing to do")
        pulls = repo.get_pulls()
        return next(
            iter([pull.html_url for pull in pulls if pull.title == title]), None
        )

    body = """
    SUMMARY
    
    A small step for me, a big step for me
    """

    pr = repo.create_pull(base="main", head="docsy", title=title, body=body)

    g.close()
    print(f"New PR '{title}' created and pushed successfully!")
    return pr.html_url


def main():
    if "GITHUB_TOKEN" not in os.environ:
        raise EnvironmentError("GITHUB_TOKEN is missing")
    logging.basicConfig(level=logging.INFO)

    # suggestion = """
    # ## Where to Find Kraken API Documentation
    
    # To access the Kraken API documentation, you can visit [https://kraken.dev.meshcloud.io/docs/index.html](https://kraken.dev.meshcloud.io/docs/index.html). The API documentation provides detailed information on how to interact with the Kraken service programmatically.
    
    # If you encounter any issues or need further assistance, you can also submit a ticket at [https://app.clickup.com/t/86bwhj5m0](https://app.clickup.com/t/86bwhj5m0) for additional support.
    # """
    # create_branch(file_content=suggestion)
    # print(create_pr(title="My first end-to-end test"))
    print(fork_repo())


if __name__ == "__main__":
    main()
