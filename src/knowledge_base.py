"""Base de conocimiento del dominio Felidae para pyDatalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from pyDatalog import pyDatalog


@dataclass(frozen=True)
class FeatureDefinition:
    key: str
    label: str
    category: str


FEATURE_CATALOG: List[FeatureDefinition] = [
    FeatureDefinition("vertebrate", "Es vertebrado", "Nucleo Mammalia"),
    FeatureDefinition("endothermic", "Presenta endotermia", "Nucleo Mammalia"),
    FeatureDefinition("body_hair", "Tiene cobertura corporal de pelo", "Nucleo Mammalia"),
    FeatureDefinition("viviparous", "Reproduccion vivipara", "Nucleo Mammalia"),
    FeatureDefinition("carnivorous_diet", "Alimentacion carnivora", "Nucleo Carnivora"),
    FeatureDefinition("carnassial_dentition", "Denticion carnasal especializada", "Nucleo Carnivora"),
    FeatureDefinition("predatory_behavior", "Comportamiento depredador", "Nucleo Carnivora"),
    FeatureDefinition("retractile_claws", "Presenta garras retractiles", "Nucleo Felidae"),
    FeatureDefinition("digitigrade_locomotion", "Locomocion digitigrada", "Nucleo Felidae"),
    FeatureDefinition("feline_morphology", "Morfologia corporal felina (craneo/hocico)", "Nucleo Felidae"),
    FeatureDefinition("mane_present", "Posee melena", "Rasgos de especie"),
    FeatureDefinition("social_groups", "Vive en grupos sociales", "Rasgos de especie"),
    FeatureDefinition("savanna_habitat", "Habitat de sabana", "Rasgos de especie"),
    FeatureDefinition("striped_coat", "Patron de pelaje rayado", "Rasgos de especie"),
    FeatureDefinition("forest_habitat", "Habitat boscoso", "Rasgos de especie"),
    FeatureDefinition("solitary_behavior", "Comportamiento mayormente solitario", "Rasgos de especie"),
    FeatureDefinition("small_body", "Talla corporal pequena", "Rasgos de especie"),
    FeatureDefinition("domesticated_behavior", "Asociado a entorno domestico", "Rasgos de especie"),
    FeatureDefinition("vocal_meow", "Vocalizacion tipo maullido", "Rasgos de especie"),
    FeatureDefinition("ear_tufts", "Presenta penachos en orejas", "Rasgos de especie"),
    FeatureDefinition("short_tail", "Cola relativamente corta", "Rasgos de especie"),
    FeatureDefinition("temperate_forest_habitat", "Habitat de bosque templado", "Rasgos de especie"),
    FeatureDefinition("non_retractile_claws", "No presenta garras retractiles", "Rasgos contradictorios"),
    FeatureDefinition("oviparous", "Reproduccion ovipara", "Rasgos contradictorios"),
    FeatureDefinition("feathers", "Cobertura corporal de plumas", "Rasgos contradictorios"),
    FeatureDefinition("herbivorous_diet", "Alimentacion herbivora", "Rasgos contradictorios"),
    FeatureDefinition("ectothermic", "Regulacion ectotermica", "Rasgos contradictorios"),
]

FEATURE_LABELS: Dict[str, str] = {feature.key: feature.label for feature in FEATURE_CATALOG}

RULE_REQUIREMENTS: Dict[str, List[str]] = {
    "Mammalia": ["vertebrate", "endothermic", "body_hair", "viviparous"],
    "Carnivora": ["carnivorous_diet", "carnassial_dentition", "predatory_behavior"],
    "Felidae": ["retractile_claws", "digitigrade_locomotion", "feline_morphology"],
    "Panthera leo": ["mane_present", "social_groups", "savanna_habitat"],
    "Panthera tigris": ["striped_coat", "forest_habitat", "solitary_behavior"],
    "Felis catus": ["small_body", "domesticated_behavior", "vocal_meow"],
    "Lynx lynx": ["ear_tufts", "short_tail", "temperate_forest_habitat"],
}

CONTRADICTION_MESSAGES: Dict[str, str] = {
    "claws_conflict": "Conflicto: se marcaron garras retractiles y no retractiles.",
    "reproduction_conflict": "Conflicto: se marcaron reproduccion vivipara y ovipara.",
    "body_cover_conflict": "Conflicto: se marcaron pelo y plumas como cobertura corporal.",
    "diet_conflict": "Conflicto: se marcaron dieta carnivora y herbivora.",
    "temperature_conflict": "Conflicto: se marcaron endotermia y ectotermia.",
}

pyDatalog.create_terms(
    "observation, infer_class, infer_order, infer_family, species_candidate, contradiction, X"
)

# pyDatalog inyecta simbolos de forma dinamica; se anotan para el analizador estatico.
observation: Any
infer_class: Any
infer_order: Any
infer_family: Any
species_candidate: Any
contradiction: Any
X: Any

_RULES_INITIALIZED = False
_ACTIVE_FACTS = set()


def _initialize_rules() -> None:
    global _RULES_INITIALIZED

    if _RULES_INITIALIZED:
        return

    infer_class("Mammalia") <= (
        observation("vertebrate")
        & observation("endothermic")
        & observation("body_hair")
        & observation("viviparous")
    )

    infer_order("Carnivora") <= (
        infer_class("Mammalia")
        & observation("carnivorous_diet")
        & observation("carnassial_dentition")
        & observation("predatory_behavior")
    )

    infer_family("Felidae") <= (
        infer_order("Carnivora")
        & observation("retractile_claws")
        & observation("digitigrade_locomotion")
        & observation("feline_morphology")
    )

    species_candidate("Panthera leo") <= (
        infer_family("Felidae")
        & observation("mane_present")
        & observation("social_groups")
        & observation("savanna_habitat")
    )

    species_candidate("Panthera tigris") <= (
        infer_family("Felidae")
        & observation("striped_coat")
        & observation("forest_habitat")
        & observation("solitary_behavior")
    )

    species_candidate("Felis catus") <= (
        infer_family("Felidae")
        & observation("small_body")
        & observation("domesticated_behavior")
        & observation("vocal_meow")
    )

    species_candidate("Lynx lynx") <= (
        infer_family("Felidae")
        & observation("ear_tufts")
        & observation("short_tail")
        & observation("temperate_forest_habitat")
    )

    contradiction("claws_conflict") <= (
        observation("retractile_claws") & observation("non_retractile_claws")
    )

    contradiction("reproduction_conflict") <= (
        observation("viviparous") & observation("oviparous")
    )

    contradiction("body_cover_conflict") <= (
        observation("body_hair") & observation("feathers")
    )

    contradiction("diet_conflict") <= (
        observation("carnivorous_diet") & observation("herbivorous_diet")
    )

    contradiction("temperature_conflict") <= (
        observation("endothermic") & observation("ectothermic")
    )

    _RULES_INITIALIZED = True


def load_observations(features: List[str]) -> None:
    """Carga hechos observados para una consulta, reemplazando hechos previos."""
    _initialize_rules()

    normalized = set(features)

    for removed_feature in _ACTIVE_FACTS - normalized:
        -observation(removed_feature)

    for new_feature in normalized - _ACTIVE_FACTS:
        +observation(new_feature)

    _ACTIVE_FACTS.clear()
    _ACTIVE_FACTS.update(normalized)


def clear_observations() -> None:
    """Elimina hechos observados previamente cargados."""
    for existing_feature in list(_ACTIVE_FACTS):
        -observation(existing_feature)
    _ACTIVE_FACTS.clear()


def _query_single_column(query_result) -> List[str]:
    return [row[0] for row in query_result.data]


def infer_taxonomy() -> Dict[str, str | None]:
    """Devuelve clase, orden y familia inferidas por reglas."""
    _initialize_rules()

    inferred_class = _query_single_column(infer_class(X))
    inferred_order = _query_single_column(infer_order(X))
    inferred_family = _query_single_column(infer_family(X))

    return {
        "class": inferred_class[0] if inferred_class else None,
        "order": inferred_order[0] if inferred_order else None,
        "family": inferred_family[0] if inferred_family else None,
    }


def infer_species_candidates() -> List[str]:
    """Devuelve especies candidatas dentro de Felidae."""
    _initialize_rules()
    return _query_single_column(species_candidate(X))


def detect_contradictions() -> List[str]:
    """Devuelve codigos de contradicciones detectadas por reglas."""
    _initialize_rules()
    return _query_single_column(contradiction(X))
