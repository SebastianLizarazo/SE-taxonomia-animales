"""Punto de entrada de la aplicacion."""

try:
    from .gui import run_app
except ImportError:
    from gui import run_app


if __name__ == "__main__":
    run_app()
