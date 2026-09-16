import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch, MagicMock

from sidecar.server import app

# Cliente de teste do FastAPI
client = TestClient(app)

def test_health_endpoint():
    """Testa se o endpoint de healthcheck está respondendo corretamente."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "device" in data
    assert data["status"] in ["ready", "loading"]

def test_classify_endpoint_invalid_path():
    """Testa a validação de caminhos inexistentes."""
    response = client.post("/classify", json={"path": "C:\\caminho\\falso\\que\\nao\\existe.jpg"})
    assert response.status_code == 404
    assert "Arquivo não encontrado" in response.json()["detail"]

def test_classify_endpoint_not_a_file(tmp_path):
    """Testa a validação quando o caminho aponta para um diretório ao invés de arquivo."""
    dir_path = tmp_path / "dummy_dir"
    dir_path.mkdir()
    
    response = client.post("/classify", json={"path": str(dir_path)})
    assert response.status_code == 400
    assert "não é um arquivo" in response.json()["detail"]

@patch("sidecar.server.get_classifier")
def test_classify_endpoint_success(mock_get_classifier, tmp_path):
    """Testa o fluxo feliz da classificação mockando o modelo SigLIP para ser rápido."""
    # Cria uma imagem temporária vazia apenas para passar na validação de arquivo
    img_path = tmp_path / "test_img.jpg"
    img_path.write_bytes(b"dummy image data")

    # Mocka a instância do classificador
    mock_classifier = MagicMock()
    mock_classifier.is_ready = True
    
    # Mocka o retorno das funções do classificador
    mock_classifier.classify_image.return_value = {"dog": 0.05, "receipt_invoice": 0.01}
    mock_classifier.evaluate_tags.return_value = {
        "is_utility": False,
        "primary_utility": None,
        "utility_tags": [],
        "general_tags": [{"key": "dog", "score": 0.05, "destination": "MM-AAAA/Geral/"}],
        "all_scores": {"dog": 0.05, "receipt_invoice": 0.01}
    }
    
    mock_get_classifier.return_value = mock_classifier

    # Faz a requisição
    response = client.post("/classify", json={"path": str(img_path)})
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_utility"] is False
    assert len(data["general_tags"]) == 1
    assert data["general_tags"][0]["key"] == "dog"
