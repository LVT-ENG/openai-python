import os
import json
import subprocess
from unittest import mock

import pytest

# Assuming we want to run the python script via subprocess for end-to-end tests
# or import and test specific functions if needed. We'll use subprocess for simplicity
# to cover arguments, env vars and outputs properly.

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "auto_deploy_v2.py")

@pytest.fixture
def valid_json_path(tmp_path):
    data = {
        "title": "Test Promo",
        "description": "50% off",
        "discount_code": "TEST50",
        "valid_until": "2024-12-31T23:59:59Z"
    }
    p = tmp_path / "valid_promo.json"
    p.write_text(json.dumps(data), encoding='utf-8')
    return str(p)

@pytest.fixture
def invalid_json_path(tmp_path):
    data = {
        "title": "Test Promo",
        "discount_code": "TEST50"
        # missing description and valid_until
    }
    p = tmp_path / "invalid_promo.json"
    p.write_text(json.dumps(data), encoding='utf-8')
    return str(p)

def test_missing_argument():
    result = subprocess.run(
        ["python3", SCRIPT_PATH],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "Uso:" in result.stdout

def test_file_not_found():
    result = subprocess.run(
        ["python3", SCRIPT_PATH, "nonexistent_file.json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "No se encontró el archivo" in result.stdout

def test_invalid_json(invalid_json_path):
    result = subprocess.run(
        ["python3", SCRIPT_PATH, invalid_json_path],
        capture_output=True,
        text=True
    )
    assert result.returncode == 1
    assert "Error de validación" in result.stdout
    assert "Falta el campo requerido" in result.stdout

def test_missing_api_key(valid_json_path, monkeypatch):
    monkeypatch.delenv("TRYONYOU_API_KEY", raising=False)
    result = subprocess.run(
        ["python3", SCRIPT_PATH, valid_json_path],
        capture_output=True,
        text=True,
        env=os.environ
    )
    assert result.returncode == 1
    assert "TRYONYOU_API_KEY no está definida" in result.stdout

@mock.patch("urllib.request.urlopen")
def test_successful_deploy(mock_urlopen, valid_json_path, monkeypatch):
    monkeypatch.setenv("TRYONYOU_API_KEY", "test_key")

    mock_response = mock.MagicMock()
    mock_response.read.return_value = b'{"status": "success"}'
    mock_urlopen.return_value = mock_response

    # Import script as module to mock urlopen easily instead of subprocess
    import sys
    import importlib.util
    spec = importlib.util.spec_from_file_location("auto_deploy", SCRIPT_PATH)
    auto_deploy = importlib.util.module_from_spec(spec)

    # Mock sys.argv
    test_args = ["auto_deploy_v2.py", valid_json_path]
    with mock.patch.object(sys, 'argv', test_args):
        # We need to capture stdout for asserting
        from io import StringIO
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            spec.loader.exec_module(auto_deploy)
            auto_deploy.main()
            output = mock_stdout.getvalue()

    assert "Despliegue exitoso" in output
    assert '{"status": "success"}' in output
    mock_urlopen.assert_called_once()
