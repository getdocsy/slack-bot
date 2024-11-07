from loguru import logger
import click
import json

from docsy.engine.coderv2 import DocsyCoder
from docsy.model.repo import LocalGitRepository
from docsy.utils.error import DocsyCLIError


@click.group()
def cli():
    pass


@cli.command()
def init() -> None:
    with open("docsy.json", "w") as f:
        json.dump(
            {
                "target": {
                    "full_repo_name": "felixzieger/docsy-docs",
                    "default_branch": "main",
                    "local_path": "/Users/felix/Documents/docsy-docs",
                }
            },
            f,
        )


@cli.command()
@click.option("--commit", help="Specific commit reference or hash to use as source")
def suggest(commit: str | None) -> None:
    # Load source repo
    source_repo = LocalGitRepository(
        "felixzieger/docsy", "main", "/Users/felix/Documents/docsy/server"
    )
    if commit:
        # If commit is specified, use it directly
        source_commits = [source_repo.get_commit(commit)]
    else:
        source_branch = source_repo.get_current_branch()
        if source_branch != source_repo.default_branch:
            # If we are not on the default branch, we take all commits ahead of the default branch
            source_commits = source_repo.get_commits_ahead_of_default()
        else:
            # If we are on the default branch, we take the last commit
            source_commits = [source_repo.get_last_commit()]

    # Load target repo
    config = json.load(open("docsy.json"))
    target_repo = LocalGitRepository(
        config["target"]["full_repo_name"],
        config["target"]["default_branch"],
        config["target"]["local_path"],
    )

    # Suggest changes
    coder = DocsyCoder(target_repo)
    suggestion = coder.suggest(source_commits)
    print(suggestion)

    # Apply changes
    try:
        coder.apply(suggestion, source_commits)
    except DocsyCLIError as e:
        print(e)


if __name__ == "__main__":
    cli()
