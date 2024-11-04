import click
import json

from docsy.engine.coderv2 import DocsyCoder
from docsy.model.GitRepository import LocalGitRepository

@click.group()
def cli():
    pass


@cli.command()
def init() -> None:
    with open("docsy.json", "w") as f:
        json.dump({ "target": { "full_repo_name": "felixzieger/docsy-docs", "branch": "main", "local_path": "/Users/felix/Documents/docsy-docs" } }, f)

@cli.command()
def suggest() -> None:
    # Load source repo
    source_repo = LocalGitRepository("felixzieger/docsy", "main", "/Users/felix/Documents/docsy/server")


    # Load target repo
    config = json.load(open("docsy.json"))
    target_repo = LocalGitRepository(config["target"]["full_repo_name"], config["target"]["branch"], config["target"]["local_path"])

    # Suggest changes
    coder = DocsyCoder(target_repo)
    coder.suggest([source_repo.get_last_commit()])

    pass

if __name__ == '__main__':
    cli()
