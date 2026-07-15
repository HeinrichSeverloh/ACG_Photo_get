import builtins
import json
import types
from unittest.mock import patch, MagicMock

# Import the module under test
import sys, os
sys.path.append(os.path.abspath('.'))
import main

def test_fetch_success(monkeypatch):
    # Mock response JSON
    mock_data = {
        "items": [
            {
                "id": "123",
                "title": "Test Image",
                "artist": {"name": "Artist"},
                "url": "http://example.com/image.jpg"
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_data
    mock_resp.raise_for_status.return_value = None
    # Ensure headers for content type not needed for fetch
    monkeypatch.setattr(main.requests, "get", lambda *args, **kwargs: mock_resp)

    result = main.fetch_from_nekosapi()
    assert isinstance(result, list)
    assert len(result) == 1
    item = result[0]
    assert item["pid"] == "123"
    assert item["title"] == "Test Image"
    assert item["author"] == "Artist"
    assert item["urls"]["original"] == "http://example.com/image.jpg"
