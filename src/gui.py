"""Interfaz grafica Tkinter para el sistema experto taxonomico."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

try:
    from .inference_engine import DEMO_CASES, InferenceEngine
except ImportError:
    from inference_engine import DEMO_CASES, InferenceEngine


class ExpertSystemGUI(tk.Tk):
    """Ventana principal de captura de rasgos y visualizacion de inferencias."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema Experto Taxonomico - Felidae")
        self.geometry("1120x720")
        self.minsize(980, 620)

        self.engine = InferenceEngine()
        self.feature_vars: dict[str, tk.BooleanVar] = {}

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(1, weight=1)

        header = ttk.Label(
            container,
            text="Identificacion taxonomica de animales (dominio Felidae)",
            font=("Segoe UI", 14, "bold"),
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        feature_panel = ttk.Frame(container)
        feature_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        feature_panel.columnconfigure(0, weight=1)
        feature_panel.rowconfigure(1, weight=1)

        case_row = ttk.Frame(feature_panel)
        case_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        case_row.columnconfigure(1, weight=1)

        ttk.Label(case_row, text="Caso de demostracion:").grid(row=0, column=0, sticky="w")

        self.case_combo = ttk.Combobox(
            case_row,
            state="readonly",
            values=["(sin caso)"] + list(DEMO_CASES.keys()),
        )
        self.case_combo.current(0)
        self.case_combo.grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Button(case_row, text="Cargar", command=self._load_demo_case).grid(row=0, column=2)

        notebook = ttk.Notebook(feature_panel)
        notebook.grid(row=1, column=0, sticky="nsew")

        features = self.engine.available_features()
        categories: dict[str, list[dict[str, str]]] = {}
        for feature in features:
            categories.setdefault(feature["category"], []).append(feature)

        for category, category_features in categories.items():
            tab = ttk.Frame(notebook, padding=10)
            tab.columnconfigure(0, weight=1)
            notebook.add(tab, text=category)

            for index, feature in enumerate(category_features):
                var = tk.BooleanVar(value=False)
                self.feature_vars[feature["key"]] = var
                check = ttk.Checkbutton(tab, text=feature["label"], variable=var)
                check.grid(row=index, column=0, sticky="w", pady=2)

        button_row = ttk.Frame(feature_panel)
        button_row.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(
            button_row,
            text="Inferir clasificacion",
            command=self._run_inference,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            button_row,
            text="Limpiar",
            command=self._clear_form,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        result_panel = ttk.Frame(container)
        result_panel.grid(row=1, column=1, sticky="nsew")
        result_panel.columnconfigure(0, weight=1)
        result_panel.rowconfigure(1, weight=1)

        ttk.Label(
            result_panel,
            text="Resultado de inferencia",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.output = ScrolledText(result_panel, wrap=tk.WORD, font=("Consolas", 10))
        self.output.grid(row=1, column=0, sticky="nsew")
        self.output.configure(state=tk.DISABLED)

        self._write_output(
            "Seleccione rasgos observables y presione 'Inferir clasificacion'.\n"
            "El sistema usara reglas pyDatalog para inferir clase, orden y familia."
        )

    def _run_inference(self) -> None:
        selected_features = [
            feature_key
            for feature_key, variable in self.feature_vars.items()
            if variable.get()
        ]

        result = self.engine.infer(selected_features)
        self._render_result(result)

    def _render_result(self, result: dict[str, object]) -> None:
        classification = result["classification"]
        warnings = result["warnings"]
        explanation = result["explanation"]
        input_labels = result["input_labels"]

        lines: list[str] = []
        lines.append("ESTADO DEL CASO")
        lines.append(f"- Estado: {result['status']}")
        lines.append("")

        lines.append("CARACTERISTICAS INGRESADAS")
        if input_labels:
            for label in input_labels:
                lines.append(f"- {label}")
        else:
            lines.append("- No se ingresaron caracteristicas.")
        lines.append("")

        lines.append("CLASIFICACION INFERIDA")
        lines.append(f"- Clase: {classification['class'] or 'No concluyente'}")
        lines.append(f"- Orden: {classification['order'] or 'No concluyente'}")
        lines.append(f"- Familia: {classification['family'] or 'No concluyente'}")

        species_candidates = classification["species_candidates"]
        if species_candidates:
            lines.append("- Especies candidatas: " + ", ".join(species_candidates))
        else:
            lines.append("- Especies candidatas: Sin sugerencias")
        lines.append("")

        lines.append("EXPLICACION DE LA INFERENCIA")
        for item in explanation:
            lines.append(f"- {item}")
        lines.append("")

        lines.append("ADVERTENCIAS")
        if warnings:
            for warning in warnings:
                lines.append(f"- {warning}")
        else:
            lines.append("- Ninguna")

        self._write_output("\n".join(lines))

    def _load_demo_case(self) -> None:
        selected_case = self.case_combo.get()

        if selected_case == "(sin caso)":
            return

        for variable in self.feature_vars.values():
            variable.set(False)

        for feature_key in DEMO_CASES[selected_case]:
            if feature_key in self.feature_vars:
                self.feature_vars[feature_key].set(True)

        self._run_inference()

    def _clear_form(self) -> None:
        for variable in self.feature_vars.values():
            variable.set(False)

        self.case_combo.current(0)
        self.engine.reset()
        self._write_output("Formulario reiniciado. Ingrese un nuevo conjunto de rasgos.")

    def _write_output(self, text: str) -> None:
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.configure(state=tk.DISABLED)


def run_app() -> None:
    app = ExpertSystemGUI()
    app.mainloop()
