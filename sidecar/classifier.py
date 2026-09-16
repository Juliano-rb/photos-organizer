"""
Módulo de inferência visual Zero-Shot com SigLIP para PhotoOrganizer.
Implementa o carregamento do modelo, pré-computação dos text embeddings
e inferência ultra-rápida por imagem (RF04.1, RF04.2, RF04.3, RF04.4).
"""

import io
import logging
from pathlib import Path
from typing import Dict, List, Union, Any, Optional

import torch
from PIL import Image, ImageOps
from transformers import AutoProcessor, AutoModel

from sidecar.taxonomy import (
    CATEGORIES,
    ALL_PROMPTS,
    ALL_KEYS,
    CATEGORY_BY_KEY,
    UTILITY_THRESHOLD,
    GENERAL_THRESHOLD,
)

logger = logging.getLogger("siglip_classifier")

DEFAULT_MODEL_ID = "google/siglip-base-patch16-224"


def get_optimal_device() -> torch.device:
    """Detecta o melhor dispositivo disponível (CUDA, DirectML ou CPU)."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    
    # Tenta DirectML caso disponível no ambiente Windows
    try:
        import torch_directml
        return torch_directml.device()
    except ImportError:
        pass

    return torch.device("cpu")


class SigLIPClassifier:
    """
    Classificador visual zero-shot baseado no Google SigLIP.
    Mantém os embeddings das 26 categorias pré-calculados em memória para
    máxima performance durante a varredura (RF04.2).
    """

    def __init__(self, model_id: str = DEFAULT_MODEL_ID, device: Optional[torch.device] = None):
        self.model_id = model_id
        self.device = device or get_optimal_device()
        self.model: Optional[AutoModel] = None
        self.processor: Optional[AutoProcessor] = None
        self.text_features: Optional[torch.Tensor] = None
        self.logit_scale: Optional[torch.Tensor] = None
        self.logit_bias: Optional[torch.Tensor] = None
        self._is_ready: bool = False

    def load(self) -> None:
        """Carrega o modelo e pré-computa os embeddings dos prompts."""
        logger.info(f"Carregando modelo SigLIP '{self.model_id}' no dispositivo: {self.device}...")
        
        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.model = AutoModel.from_pretrained(self.model_id).to(self.device)
        self.model.eval()

        self._precompute_text_embeddings()
        self._is_ready = True
        logger.info("Modelo SigLIP carregado e embeddings de texto pré-computados com sucesso!")

    def _extract_tensor(self, output: Any) -> torch.Tensor:
        """Extrai o tensor de embedding de saídas do transformers."""
        if isinstance(output, torch.Tensor):
            return output
        if hasattr(output, "pooler_output") and output.pooler_output is not None:
            return output.pooler_output
        if hasattr(output, "last_hidden_state") and output.last_hidden_state is not None:
            return output.last_hidden_state
        if isinstance(output, (tuple, list)):
            return output[0]
        return output

    def _precompute_text_embeddings(self) -> None:
        """Pré-computa e normaliza os embeddings das 26 categorias da taxonomia."""
        if self.model is None or self.processor is None:
            raise RuntimeError("O modelo e o processador precisam ser carregados antes da pré-computação.")

        logger.info(f"Pré-computando embeddings para {len(ALL_PROMPTS)} categorias da taxonomia...")
        text_inputs = self.processor(
            text=ALL_PROMPTS,
            padding="max_length",
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            output = self.model.get_text_features(**text_inputs)
            features = self._extract_tensor(output)
            # Normalização L2 para similaridade de cosseno
            self.text_features = features / features.norm(dim=-1, keepdim=True)
            self.logit_scale = self.model.logit_scale.exp()
            self.logit_bias = self.model.logit_bias

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    def _load_image(self, image_input: Union[str, Path, bytes, Image.Image]) -> Image.Image:
        """Abre a imagem, normaliza orientação EXIF e converte para RGB."""
        if isinstance(image_input, (str, Path)):
            image = Image.open(str(image_input))
        elif isinstance(image_input, bytes):
            image = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            image = image_input
        else:
            raise ValueError(f"Formato de imagem não suportado: {type(image_input)}")

        # Corrige rotação física da câmera indicada no EXIF
        image = ImageOps.exif_transpose(image)
        return image.convert("RGB")

    def classify_image(self, image_input: Union[str, Path, bytes, Image.Image]) -> Dict[str, float]:
        """
        Calcula os scores de probabilidade SigLIP (Sigmoid de 0 a 1) para cada tag.
        Retorna dicionário {tag_key: score_float}.
        """
        if not self._is_ready or self.model is None or self.processor is None or self.text_features is None:
            raise RuntimeError("Classificador não inicializado. Chame .load() primeiro.")

        image = self._load_image(image_input)
        image_inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.model.get_image_features(**image_inputs)
            image_features = self._extract_tensor(output)
            # Normalização L2 do embedding visual
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            # Fórmula SigLIP: sigmoid(image_embeds @ text_embeds.T * logit_scale + logit_bias)
            logits = torch.matmul(image_features, self.text_features.t()) * self.logit_scale + self.logit_bias
            probs = torch.sigmoid(logits).squeeze(0).cpu().tolist()

        return {key: round(float(prob), 4) for key, prob in zip(ALL_KEYS, probs)}

    def evaluate_tags(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Aplica os limiares de decisão de negócio do PhotoOrganizer (RF04.4):
        - Prioridade 1 (Utilitários): score >= 0.60
        - Prioridade 2 (Marcação Geral): score >= 0.35
        """
        utility_tags = []
        general_tags = []
        is_utility = False
        primary_utility = None

        for key, score in scores.items():
            category = CATEGORY_BY_KEY.get(key)
            if not category:
                continue

            if category.is_utility and score >= UTILITY_THRESHOLD:
                is_utility = True
                utility_tags.append({"key": key, "score": score, "destination": category.destination})
                if primary_utility is None or score > primary_utility["score"]:
                    primary_utility = {"key": key, "score": score, "destination": category.destination}
            elif not category.is_utility and score >= GENERAL_THRESHOLD:
                general_tags.append({"key": key, "score": score, "destination": category.destination, "group": category.group})

        # Ordena tags gerais por relevância decrescente
        general_tags.sort(key=lambda x: x["score"], reverse=True)
        utility_tags.sort(key=lambda x: x["score"], reverse=True)

        return {
            "is_utility": is_utility,
            "primary_utility": primary_utility,
            "utility_tags": utility_tags,
            "general_tags": general_tags,
            "all_scores": scores,
        }


# Instância global reutilizável (Lazy loading)
_global_classifier: Optional[SigLIPClassifier] = None


def get_classifier() -> SigLIPClassifier:
    """Retorna a instância do classificador, carregando o modelo se necessário."""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = SigLIPClassifier()
        _global_classifier.load()
    return _global_classifier
