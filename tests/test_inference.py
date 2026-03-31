"""Pruebas representativas del motor de inferencia taxonomica."""

from __future__ import annotations

import unittest

from src.inference_engine import InferenceEngine


class InferenceEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = InferenceEngine()

    def test_complete_case_infers_felidae_and_species(self) -> None:
        result = self.engine.infer(
            [
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
            ]
        )

        self.assertEqual(result["classification"]["class"], "Mammalia")
        self.assertEqual(result["classification"]["order"], "Carnivora")
        self.assertEqual(result["classification"]["family"], "Felidae")
        self.assertIn("Panthera leo", result["classification"]["species_candidates"])
        self.assertEqual(result["status"], "concluyente")

    def test_incomplete_case_reports_missing_evidence(self) -> None:
        result = self.engine.infer(
            [
                "vertebrate",
                "body_hair",
                "viviparous",
                "carnivorous_diet",
                "predatory_behavior",
            ]
        )

        self.assertIsNone(result["classification"]["family"])
        self.assertEqual(result["status"], "incompleto")
        self.assertTrue(any("Evidencia insuficiente" in w for w in result["warnings"]))

    def test_ambiguous_case_reports_multiple_species(self) -> None:
        result = self.engine.infer(
            [
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
                "striped_coat",
                "forest_habitat",
                "solitary_behavior",
            ]
        )

        species = result["classification"]["species_candidates"]
        self.assertEqual(result["classification"]["family"], "Felidae")
        self.assertIn("Panthera leo", species)
        self.assertIn("Panthera tigris", species)
        self.assertEqual(result["status"], "ambiguo")

    def test_conflict_case_reports_contradictions(self) -> None:
        result = self.engine.infer(
            [
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
            ]
        )

        self.assertEqual(result["status"], "conflictivo")
        self.assertTrue(any("Conflicto" in w for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
