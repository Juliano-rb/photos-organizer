import pytest
import torch
from unittest.mock import patch, MagicMock
from sidecar.classifier import SigLIPClassifier, get_optimal_device

def test_get_optimal_device():
    device = get_optimal_device()
    assert isinstance(device, torch.device)

def test_extract_tensor():
    classifier = SigLIPClassifier()
    
    # 1. Testando entrada de Tensor direto
    tensor = torch.tensor([1.0, 2.0])
    assert torch.equal(classifier._extract_tensor(tensor), tensor)
    
    # 2. Testando com pooler_output (padrão de alguns modelos transformers)
    class DummyOutput1:
        pooler_output = torch.tensor([3.0, 4.0])
    assert torch.equal(classifier._extract_tensor(DummyOutput1()), DummyOutput1.pooler_output)

    # 3. Testando com last_hidden_state
    class DummyOutput2:
        pooler_output = None
        last_hidden_state = torch.tensor([5.0, 6.0])
    assert torch.equal(classifier._extract_tensor(DummyOutput2()), DummyOutput2.last_hidden_state)
    
    # 4. Testando com tupla
    tup = (torch.tensor([7.0, 8.0]), )
    assert torch.equal(classifier._extract_tensor(tup), tup[0])

def test_evaluate_tags_with_utility():
    classifier = SigLIPClassifier()
    
    # Simulando scores de saída do SigLIP
    scores = {
        "receipt_invoice": 0.85,  # Utilitário, acima do UTILITY_THRESHOLD (0.60)
        "document_text": 0.55,    # Utilitário, abaixo do UTILITY_THRESHOLD
        "beach_ocean": 0.40,      # Geral, acima do GENERAL_THRESHOLD (0.35)
        "dog": 0.30,              # Geral, abaixo do GENERAL_THRESHOLD
        "cat": 0.90               # Geral, acima do GENERAL_THRESHOLD
    }

    result = classifier.evaluate_tags(scores)

    # is_utility deve ser True pois receipt_invoice >= 0.60
    assert result["is_utility"] is True
    
    # Primary utility deve ser o recibo, que tem o maior score utilitário
    assert result["primary_utility"]["key"] == "receipt_invoice"
    assert result["primary_utility"]["score"] == 0.85
    
    # Apenas o recibo deve estar na lista de utilitários
    assert len(result["utility_tags"]) == 1
    assert result["utility_tags"][0]["key"] == "receipt_invoice"

    # general_tags deve conter apenas cat e beach_ocean (ordenados do maior para o menor)
    assert len(result["general_tags"]) == 2
    assert result["general_tags"][0]["key"] == "cat"
    assert result["general_tags"][1]["key"] == "beach_ocean"

def test_evaluate_tags_no_utility():
    classifier = SigLIPClassifier()
    
    scores = {
        "receipt_invoice": 0.55,  # Utilitário, abaixo do limite (não é considerado)
        "beach_ocean": 0.80,      # Geral, acima do limite
    }

    result = classifier.evaluate_tags(scores)

    assert result["is_utility"] is False
    assert result["primary_utility"] is None
    assert len(result["utility_tags"]) == 0
    assert len(result["general_tags"]) == 1
    assert result["general_tags"][0]["key"] == "beach_ocean"
