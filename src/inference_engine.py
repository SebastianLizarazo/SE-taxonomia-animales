"""Motor de inferencia desacoplado de la interfaz."""

from __future__ import annotations

from typing import Dict, List

try:
    from .knowledge_base import (
        CONTRADICTION_MESSAGES,
        FEATURE_CATALOG,
        FEATURE_LABELS,
        RULE_REQUIREMENTS,
        clear_observations,
        detect_contradictions,
        infer_species_candidates,
        infer_taxonomy,
        load_observations,
    )
except ImportError:
    from knowledge_base import (
        CONTRADICTION_MESSAGES,
        FEATURE_CATALOG,
        FEATURE_LABELS,
        RULE_REQUIREMENTS,
        clear_observations,
        detect_contradictions,
        infer_species_candidates,
        infer_taxonomy,
        load_observations,
    )

DEMO_CASES: Dict[str, List[str]] = {
    "Leopardo/Leon (Felidae completo)": [
        "vertebrate",
        "endothermic",
        "body_hair",
        "viviparous",
        "carnivorous_diet",
        "carnassial_dentition",
        "predatory_behavior",
        "retractile_claws",
        "digitigrade_locomotion",
        "feline_morphology",
        "mane_present",
        "social_groups",
        "savanna_habitat",
    ],
    "Tigre (Felidae completo)": [
        "vertebrate",
        "endothermic",
        "body_hair",
        "viviparous",
        "carnivorous_diet",
        "carnassial_dentition",
        "predatory_behavior",
        "retractile_claws",
        "digitigrade_locomotion",
        "feline_morphology",
        "striped_coat",
        "forest_habitat",
        "solitary_behavior",
    ],
    "Caso incompleto": [
        "vertebrate",
        "body_hair",
        "viviparous",
        "carnivorous_diet",
        "predatory_behavior",
    ],
    "Caso contradictorio": [
        "vertebrate",
        "endothermic",
        "body_hair",
        "viviparous",
        "oviparous",
        "carnivorous_diet",
        "herbivorous_diet",
        "carnassial_dentition",
        "predatory_behavior",
        "retractile_claws",
        "non_retractile_claws",
        "digitigrade_locomotion",
        "feline_morphology",
    ],
}


class InferenceEngine:
    """Orquesta la evaluacion de hechos y reglas taxonomicas."""

    def infer(self, selected_features: List[str]) -> Dict[str, object]:
        clean_features = sorted(set(selected_features))

        load_observations(clean_features)
        taxonomy = infer_taxonomy()
        species_candidates = sorted(infer_species_candidates())
        contradiction_codes = sorted(detect_contradictions())

        status = self._determine_status(
            taxonomy["family"], species_candidates, contradiction_codes
        )
        warnings = self._build_warnings(clean_features, taxonomy, species_candidates, contradiction_codes)
        explanation = self._build_explanation(
            clean_features, taxonomy, species_candidates, contradiction_codes
        )

        return {
            "status": status,
            "input_features": clean_features,
            "input_labels": [FEATURE_LABELS.get(feature, feature) for feature in clean_features],
            "classification": {
                "class": taxonomy["class"],
                "order": taxonomy["order"],
                "family": taxonomy["family"],
                "species_candidates": species_candidates,
            },
            "warnings": warnings,
            "explanation": explanation,
        }

    @staticmethod
    def available_features() -> List[Dict[str, str]]:
        return [
            {"key": feature.key, "label": feature.label, "category": feature.category}
            for feature in FEATURE_CATALOG
        ]

    @staticmethod
    def reset() -> None:
        clear_observations()

    @staticmethod
    def _determine_status(
        inferred_family: str | None,
        species_candidates: List[str],
        contradiction_codes: List[str],
    ) -> str:
        if contradiction_codes:
            return "conflictivo"
        if inferred_family is None:
            return "incompleto"
        if len(species_candidates) > 1:
            return "ambiguo"
        return "concluyente"

    @staticmethod
    def _missing_requirements(rule_name: str, selected_features: List[str]) -> List[str]:
        required = set(RULE_REQUIREMENTS.get(rule_name, []))
        return sorted(required - set(selected_features))

    def _build_warnings(
        self,
        selected_features: List[str],
        taxonomy: Dict[str, str | None],
        species_candidates: List[str],
        contradiction_codes: List[str],
    ) -> List[str]:
        warnings: List[str] = []

        for code in contradiction_codes:
            warnings.append(CONTRADICTION_MESSAGES.get(code, f"Conflicto detectado: {code}."))

        if taxonomy["class"] is None:
            missing = self._missing_requirements("Mammalia", selected_features)
            warnings.append(
                "Evidencia insuficiente para inferir Mammalia. Faltan: "
                + self._format_feature_list(missing)
            )

        if taxonomy["order"] is None:
            missing = self._missing_requirements("Carnivora", selected_features)
            warnings.append(
                "Evidencia insuficiente para inferir Carnivora. Faltan: "
                + self._format_feature_list(missing)
            )

        if taxonomy["family"] is None:
            missing = self._missing_requirements("Felidae", selected_features)
            warnings.append(
                "Evidencia insuficiente para inferir Felidae. Faltan: "
                + self._format_feature_list(missing)
            )

        if taxonomy["family"] == "Felidae" and not species_candidates:
            warnings.append(
                "La familia Felidae fue inferida, pero faltan rasgos discriminativos para sugerir especie."
            )

        if len(species_candidates) > 1:
            warnings.append(
                "Caso ambiguo: mas de una especie candidata cumple las reglas."
            )

        return warnings

    def _build_explanation(
        self,
        selected_features: List[str],
        taxonomy: Dict[str, str | None],
        species_candidates: List[str],
        contradiction_codes: List[str],
    ) -> List[str]:
        explanation: List[str] = []

        explanation.append("Se cargaron hechos observables en la base de conocimiento pyDatalog.")
        explanation.append(self._rule_trace("Mammalia", taxonomy["class"] == "Mammalia", selected_features))
        explanation.append(self._rule_trace("Carnivora", taxonomy["order"] == "Carnivora", selected_features))
        explanation.append(self._rule_trace("Felidae", taxonomy["family"] == "Felidae", selected_features))

        if species_candidates:
            for species in species_candidates:
                explanation.append(self._rule_trace(species, True, selected_features))
        elif taxonomy["family"] == "Felidae":
            explanation.append(
                "No se activo ninguna regla de especie: faltan rasgos diferenciales adicionales."
            )

        if contradiction_codes:
            explanation.append(
                "Se activaron reglas de contradiccion; la clasificacion debe interpretarse con cautela."
            )

        return explanation

    def _rule_trace(self, rule_name: str, activated: bool, selected_features: List[str]) -> str:
        required = RULE_REQUIREMENTS.get(rule_name, [])
        readable_required = self._format_feature_list(required)

        if activated:
            return f"Regla {rule_name} activada por evidencias: {readable_required}."

        missing = self._missing_requirements(rule_name, selected_features)
        return (
            f"Regla {rule_name} no activada. Faltan: {self._format_feature_list(missing)}."
        )

    @staticmethod
    def _format_feature_list(feature_keys: List[str]) -> str:
        if not feature_keys:
            return "ninguna"
        return ", ".join(FEATURE_LABELS.get(feature, feature) for feature in feature_keys)
