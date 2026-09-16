"""
Taxonomia oficial de classificação visual para o PhotoOrganizer (RF04.2 e RF04.3).
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass(frozen=True)
class Category:
    group: str
    key: str
    prompt: str
    destination: str
    is_utility: bool = False

UTILITY_THRESHOLD = 0.60
GENERAL_THRESHOLD = 0.35

CATEGORIES: List[Category] = [
    # Utilitários / Documentos (Prioridade 1 - Isolamento)
    Category("Utilitário", "receipt_invoice", "a photo of a paper receipt, bill, or tax invoice", "Documentos/Comprovantes/", is_utility=True),
    Category("Utilitário", "document_text", "a photograph of a printed document, contract, or form", "Documentos/Texto/", is_utility=True),
    Category("Utilitário", "id_card", "a photo of an identity card, driver license, or passport", "Documentos/Identidade/", is_utility=True),
    Category("Utilitário", "screenshot", "a screenshot of a mobile phone screen or computer desktop", "Screenshots/", is_utility=True),
    Category("Utilitário", "handwritten_notes", "a photo of a notebook page with handwriting or a whiteboard", "Documentos/Anotacoes/", is_utility=True),

    # Eventos (Subpastas dinâmicas)
    Category("Eventos", "birthday_party", "a photo of a birthday party with cake or party decorations", "MM-AAAA/Aniversario/"),
    Category("Eventos", "wedding_ceremony", "a photo of a wedding ceremony, bride, or wedding reception", "MM-AAAA/Casamento/"),
    Category("Eventos", "concert_show", "a photo of a music concert, live stage performance, or festival", "MM-AAAA/Show/"),
    Category("Eventos", "sports_event", "a photo of people playing sports or an athletic competition", "MM-AAAA/Esportes/"),
    Category("Eventos", "barbecue_party", "a photo of a barbecue gathering, churrasco, or outdoor grill party", "MM-AAAA/Churrasco/"),

    # Ambientes (Subpastas dinâmicas)
    Category("Ambientes", "beach_ocean", "a photo of a beach, ocean shore, and sea", "MM-AAAA/Praia/"),
    Category("Ambientes", "hiking_nature", "a photo of a hiking trail, mountains, or green forest", "MM-AAAA/Natureza/"),
    Category("Ambientes", "cityscape_street", "a photo of city streets, urban architecture, and buildings", "MM-AAAA/Cidade/"),
    Category("Ambientes", "sunset_sunrise", "a scenic photograph of a sunset or sunrise in the sky", "MM-AAAA/PorDoSol/"),
    Category("Ambientes", "pool_resort", "a photo of a swimming pool or vacation resort", "MM-AAAA/Piscina/"),
    Category("Ambientes", "home_indoor", "a photo taken indoors inside a house, bedroom, or living room", "MM-AAAA/Casa/"),

    # Pessoas (Geral)
    Category("Pessoas", "selfie", "a close-up selfie photograph of a person", "MM-AAAA/Geral/"),
    Category("Pessoas", "group_portrait", "a group photo of friends or family posing together", "MM-AAAA/Geral/"),
    Category("Pessoas", "baby_child", "a photograph of a baby, toddler, or young child", "MM-AAAA/Geral/"),
    Category("Pessoas", "portrait_person", "a portrait photograph of a single person", "MM-AAAA/Geral/"),

    # Pets (Geral)
    Category("Pets", "cat", "a close-up photo of a domestic cat", "MM-AAAA/Geral/"),
    Category("Pets", "dog", "a photo of a domestic dog or puppy", "MM-AAAA/Geral/"),
    Category("Pets", "birds_wildlife", "a photo of birds, farm animals, or wildlife", "MM-AAAA/Geral/"),

    # Gastronomia (Geral)
    Category("Gastronomia", "food_meal", "a close-up food photo of a cooked meal on a plate", "MM-AAAA/Geral/"),
    Category("Gastronomia", "drinks_coffee", "a photo of a cup of coffee, cocktails, or beverages on a table", "MM-AAAA/Geral/"),

    # Hobbies/Misc (Geral)
    Category("Hobbies/Misc", "vehicles", "a photograph of a car, motorcycle, or vehicle", "MM-AAAA/Geral/"),
    Category("Hobbies/Misc", "plants_garden", "a close-up photo of house plants, flowers, or a garden", "MM-AAAA/Geral/"),
    Category("Hobbies/Misc", "crafts_art", "a photo of handmade pottery, ceramics, crafts, or art", "MM-AAAA/Geral/"),
]

CATEGORY_BY_KEY: Dict[str, Category] = {cat.key: cat for cat in CATEGORIES}
ALL_PROMPTS: List[str] = [cat.prompt for cat in CATEGORIES]
ALL_KEYS: List[str] = [cat.key for cat in CATEGORIES]
