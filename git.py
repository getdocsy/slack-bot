import os
from github import Github
from github import InputGitTreeElement
from github import Auth

from random import randint
version = randint(1,100)

def create_branch():
    if "GITHUB_TOKEN" not in os.environ: 
        raise EnvironmentError("GITHUB_TOKEN is missing")

    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth)
    repo = g.get_repo("felixzieger/congenial-computing-machine")

    file_path = 'README.md'
    file = repo.get_contents(file_path)
    new_content = f"# Congenial Computing Machine Docs v{version}"
    repo.update_file(file.path, f"commit message {version}", new_content, file.sha)


    main_ref = repo.get_git_ref("heads/main")
    latest_commit = repo.get_commit(main_ref.object.sha)
    new_tree = repo.create_git_tree([
        InputGitTreeElement(file.path, '100644', 'blob', content=new_content)
    ], base_tree=latest_commit.commit.tree)
    new_commit = repo.create_git_commit("my first commit using python", new_tree, [latest_commit])

    g.close()

create_branch()

def create_pr():

    if "GITHUB_TOKEN" not in os.environ: 
        raise EnvironmentError("GITHUB_TOKEN is missing")

    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)
    repo = g.get_repo("felixzieger/congenial-computing-machine")
    
    body = '''
    
    SUMMARY
    
    A small step for me, a big step for me
    '''
    
    pr = repo.create_pull(base="main", head="docsy", title="My first PR using python", body=body)
    pr
    
    g.close()
    






