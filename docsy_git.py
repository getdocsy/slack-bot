import os
import tempfile
from git import Repo
from github import Github
from github import Auth



def create_branch():
    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)
        repo_path = tmpdirname

        # Clone the remote repository
        if "GITHUB_TOKEN" not in os.environ: 
            raise EnvironmentError("GITHUB_TOKEN is missing")

        username = "felixzieger"
        token = os.environ.get("GITHUB_TOKEN")

        repo_url = f"https://{username}:{token}@github.com/felixzieger/congenial-computing-machine.git"
        repo = Repo.clone_from(repo_url, repo_path)

        # Create a new branch based on the main branch
        new_branch_name = "docsy"
        main_branch = repo.heads.main
        new_branch = repo.create_head(new_branch_name, commit=main_branch.commit)
        new_branch.checkout()

        # Update the file(s) in the new branch
        file_path = os.path.join(repo_path, "README.md")
        with open(file_path, "w") as file:
            file.write("# New content for the file")

        # Stage the changes
        repo.index.add([file_path])

        # Commit the changes
        commit_message = "Update README.md in new branch"
        repo.index.commit(commit_message)

        # Push the new branch to the remote repository
        origin = repo.remote()
        origin.push(new_branch)

        print(f"New branch '{new_branch_name}' created and pushed successfully!")



def create_pr():

    if "GITHUB_TOKEN" not in os.environ: 
        raise EnvironmentError("GITHUB_TOKEN is missing")

    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)
    repo = g.get_repo("felixzieger/congenial-computing-machine")
    
    title = "My first PR using python"
    body = '''
    
    SUMMARY
    
    A small step for me, a big step for me
    '''
    
    pr = repo.create_pull(base="main", head="docsy", title=title, body=body)
    pr
    
    g.close()
    print(f"New PR '{title}' created and pushed successfully!")
    
create_branch()
create_pr()



