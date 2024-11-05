import click
import json

from docsy.engine.coderv2 import DocsyCoder
from docsy.model.repo import LocalGitRepository

@click.group()
def cli():
    pass


@cli.command()
def init() -> None:
    with open("docsy.json", "w") as f:
        json.dump({ "target": { "full_repo_name": "felixzieger/docsy-docs", "default_branch": "main", "local_path": "/Users/felix/Documents/docsy-docs" } }, f)

@cli.command()
def suggest() -> None:
    # Load source repo
    source_repo = LocalGitRepository("felixzieger/docsy", "main", "/Users/felix/Documents/docsy/server")
    source_branch = source_repo.get_current_branch()
    if source_branch != source_repo.default_branch:
        source_commits = source_repo.get_commits_ahead_of_default()
    else:
        # If we are on the default branch, we take the last commit
        source_commits = [source_repo.get_last_commit()]

    # Load target repo
    config = json.load(open("docsy.json"))
    target_repo = LocalGitRepository(config["target"]["full_repo_name"], config["target"]["default_branch"], config["target"]["local_path"])

    # Suggest changes
    coder = DocsyCoder(target_repo)
    suggestion = coder.suggest(source_commits)
    print(suggestion)

if __name__ == '__main__':
    cli()
