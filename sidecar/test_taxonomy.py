import pytest
from sidecar.taxonomy import CATEGORIES, CATEGORY_BY_KEY, ALL_PROMPTS, ALL_KEYS

def test_taxonomy_lengths():
    assert len(CATEGORIES) > 0, "A taxonomia não pode ser vazia"
    assert len(CATEGORIES) == len(CATEGORY_BY_KEY), "Mismatch entre CATEGORIES e CATEGORY_BY_KEY"
    assert len(CATEGORIES) == len(ALL_PROMPTS), "Mismatch entre CATEGORIES e ALL_PROMPTS"
    assert len(CATEGORIES) == len(ALL_KEYS), "Mismatch entre CATEGORIES e ALL_KEYS"

def test_taxonomy_keys_unique():
    keys = [cat.key for cat in CATEGORIES]
    assert len(keys) == len(set(keys)), "Existem chaves duplicadas na taxonomia"

def test_taxonomy_prompts_unique():
    prompts = [cat.prompt for cat in CATEGORIES]
    assert len(prompts) == len(set(prompts)), "Existem prompts duplicados na taxonomia"

def test_taxonomy_utility_flags():
    for cat in CATEGORIES:
        if cat.group == "Utilitário":
            assert cat.is_utility is True, f"A categoria utilitária {cat.key} deve ter is_utility=True"
        else:
            assert cat.is_utility is False, f"A categoria {cat.key} não deve ser utilitária"
