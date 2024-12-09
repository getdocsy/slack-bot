import pytest
from docsy.engine.ai.analyze import AI

def test_analyze_docsy_docs():
    print("\nStarting analysis of docs.getdocsy.com")
    ai = AI()
    result = ai.analyze("https://docs.getdocsy.com")
    print(f"Analysis result: {result[:200]}...")  # Print first 200 chars of result
    
    # Basic assertions to verify the response
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0 