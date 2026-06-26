"""Permite ejecutar la fábrica como módulo:  python -m factory <comando>"""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
