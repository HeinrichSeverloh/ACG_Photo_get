import os
import tempfile
from io import BytesIO
from unittest.mock import MagicMock, patch

import sys
sys.path.append(os.path.abspath('.'))
import main

def create_png_bytes():
    # Generate a tiny PNG (1x1 pixel)
    from PIL import Image
    img = Image.new('RGB', (1, 1), color='red')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def test_download_single_image_success(tmp_path, monkeypatch):
    # Set a temporary save directory
    main.CONFIG["SAVE_DIR"] = str(tmp_path)
    # Ensure PID log is inside the temp dir
    # Monkeypatch the register_pid to avoid file writes for simplicity
    monkeypatch.setattr(main, "register_pid", lambda pid: None)

    png_data = create_png_bytes()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "image/png"}
    mock_resp.iter_content = lambda chunk_size: [png_data]
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
    mock_resp.raise_for_status.return_value = None
    mock_resp.content = png_data

    monkeypatch.setattr(main.requests, "get", lambda *args, **kwargs: mock_resp)

    image_info = {
        "pid": "test123",
        "title": "TestImage",
        "urls": {"original": "http://example.com/image.png"},
    }

    status = main.download_single_image(image_info)
    assert status == "success"
    # Verify file exists
    files = os.listdir(str(tmp_path))
    assert any(f.startswith("test123_TestImage") and f.endswith('.png') for f in files)
