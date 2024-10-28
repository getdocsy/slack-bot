import pytest
from docsy_server.api.api import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_suggestion_valid_input(client):
    # Arrange
    test_data = {
        "context": [
            {
                "github_repository_name": "felixzieger/docsy",
                "pull_request_number": 1
            }
        ]
    }

    # Act
    response = client.post('/engine/suggestion', 
                         data=json.dumps(test_data),
                         content_type='application/json')
    
    # Assert
    response_data = json.loads(response.data)
    print(response_data)
    assert response.status_code == 200
    assert "suggestion" in response_data

