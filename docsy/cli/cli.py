from loguru import logger
import click
import json
import os
from docsy.cli.model.repo import LocalGitRepository
from docsy.cli.ai import DocsyCoder
from docsy.cli.utils.error import DocsyCLIError
from docsy.cli.utils.settings import load_settings, save_settings


@click.group()
def cli():
    pass


@cli.command()
def init() -> None:
    # Abort if docsy.json already exists
    if os.path.exists("docsy.json"):
        click.echo("Initialization aborted: docsy.json already exists.")
        return

    repo = LocalGitRepository()

    full_repo_name = repo.extract_full_repo_name_from_origin_url()

    # Ask about documentation location
    is_same_repo = click.confirm(
        "Is the documentation stored in the same repository?", default=False
    )

    if is_same_repo:
        # Get current repo details
        config = {
            "target": {
                "full_repo_name": full_repo_name,
                "default_branch": "main",
            }
        }
        save_settings({"targets": {full_repo_name: os.getcwd()}})
    else:
        # Ask for target repo details
        config = {
            "target": {
                "full_repo_name": click.prompt(
                    "Enter the full name of the documentation repository (e.g., username/repo)"
                ),
                "default_branch": click.prompt(
                    "Enter the default branch name", default="main"
                ),
            }
        }

        save_settings(
            {"targets": {full_repo_name: click.prompt("Enter the local path to the documentation repository")}}
        )

    # Write config to file
    with open("docsy.json", "w") as f:
        json.dump(config, f, indent=4)


@cli.command()
@click.option("--commit", help="Specific commit reference or hash to use as source")
def suggest(commit: str | None) -> None:
    # Load source repo
    source_repo = LocalGitRepository()
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
    settings = load_settings()
    full_repo_name = config["target"]["full_repo_name"]
    local_path = settings["targets"][full_repo_name]
    target_repo = LocalGitRepository(
        local_path,
    )

    # Suggest changes
    coder = DocsyCoder(target_repo)
    suggestion = coder.suggest(source_commits)

    # Apply changes
    try:
        coder.apply(suggestion, source_commits)
    except DocsyCLIError as e:
        print(e)


if __name__ == "__main__":
    
    cli()
