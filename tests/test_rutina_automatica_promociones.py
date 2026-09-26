import json
import urllib.error

# Import from the script directly
import importlib.util
from unittest.mock import MagicMock, patch

import pytest

spec = importlib.util.spec_from_file_location("rutina", "scripts/rutina_automatica_promociones.py")
assert spec is not None
rutina = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(rutina)


def test_extraer_json_robusto_objeto():
    # Test valid JSON object
    data = {"title": "Test", "description": "Test Desc", "discount_code": "TEST", "valid_until": "2024-12-31"}
    json_str = json.dumps(data)
    assert rutina.extraer_json_robusto(json_str) == data

    # Test with extra text
    text_with_json = f"Here is the JSON:\n```json\n{json_str}\n```\nEnjoy!"
    assert rutina.extraer_json_robusto(text_with_json) == data


def test_extraer_json_robusto_lista():
    # Test valid JSON array
    data = [{"title": "Test", "description": "Test Desc", "discount_code": "TEST", "valid_until": "2024-12-31"}]
    json_str = json.dumps(data)
    assert rutina.extraer_json_robusto(json_str) == data

    # Test with extra text
    text_with_json = f"Here is the JSON list:\n{json_str}\nHope this helps."
    assert rutina.extraer_json_robusto(text_with_json) == data


def test_validar_promocion_valida():
    data = {"title": "Test", "description": "Test Desc", "discount_code": "TEST", "valid_until": "2024-12-31"}
    promos = rutina.validar_promocion(data)
    assert len(promos) == 1
    assert promos[0].title == "Test"


def test_validar_promocion_invalida():
    data = {"title": "Test"}  # Missing required fields
    with pytest.raises(rutina.ValidationError):
        rutina.validar_promocion(data)


@patch("urllib.request.urlopen")
def test_desplegar_promocion_exito(mock_urlopen: MagicMock):
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"success": true}'
    mock_urlopen.return_value = mock_response

    promo = rutina.Promocion(title="Test", description="Desc", discount_code="CODE", valid_until="2024-12-31")
    result = rutina.desplegar_promocion(promo, "http://api.test", "fake_key", False)
    assert result is True


@patch("urllib.request.urlopen")
def test_desplegar_promocion_fallo(mock_urlopen: MagicMock):
    mock_urlopen.side_effect = urllib.error.URLError("Failed")

    promo = rutina.Promocion(title="Test", description="Desc", discount_code="CODE", valid_until="2024-12-31")
    result = rutina.desplegar_promocion(promo, "http://api.test", "fake_key", False)
    assert result is False
