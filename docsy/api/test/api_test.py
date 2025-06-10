import pytest
from docsy.api.api import app
import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_generate_suggestion_valid_input(client):
    # Arrange
    test_data = {
        "context": [
            {
                "github_repo_full_name": "felixzieger/docsy",
                "commits": [
                    {
                        "sha": "abc123",
                        "message": "Test commit",
                        "diff": """
                            diff --git a/docsy/api/api.py b/docsy/api/api.py
                            index 29bcfb0..989afac 100644
                            --- a/docsy/api/api.py
                            +++ b/docsy/api/api.py
                            @@ -25,19 +25,17 @@ def generate_suggestion():
                                 states:list[str] = []
                                 events:list[str] = []
                                 for c in context:
                            -        try:
                            -            if 'pull_request_number' not in c:
                            -                return jsonify({"error": "Missing required field: pull_request_number"}), 400
                            -            c = GithubRepositoryContext(**c)
                            -        except Exception as e:
                            -            return jsonify({"error": str(e)}), 400
                            +        if 'pull_request_number' not in c:
                            +            return jsonify({"error": "Missing required field: pull_request_number"}), 400
                            +        c = GithubRepositoryContext(**c)
                            +
                                     ghm = get_github_manager_for_repo(51286673,c.github_repository_name) # TODO: choose installation id from auth
                                     states.append(ghm.list_md_files())
                                     for commit in ghm.get_commits(c.pull_request_number):
                                         events.append(ghm.get_diff(commit.parents[0].sha, commit.sha))
                             
                                 prompts = [
                            -        Prompt(role="system", content="The following changes are made to the repository:"),
                            +        Prompt(role="system", content="The following changes are made to the code:"),
                                 ] + [Prompt(role="user", content=event) for event in events] + [
                                     Prompt(role="system", content="Do you think the documentation needs to be updated to reflect the changes?")
                                 ]
                        """,
                    }
                ],
            },
        ],
        "target": {"github_repo_full_name": "felixzieger/docsy-docs"},
    }

    # Act
    response = client.post(
        "/engine/suggestion",
        data=json.dumps(test_data),
        content_type="application/json",
    )

    # Assert
    response_data = json.loads(response.data)
    print(response_data)
    assert response.status_code == 200
    assert "suggestion" in response_data
