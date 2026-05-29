# pyrefly: ignore [missing-import]
import pytest
from sherlock_project.sherlock import interpolate_string

"""
Testes de caixa-preta para interpolate_string().
Técnicas: Particionamento de Equivalência (CE) e Análise de Valor-Limite (VL).

Assinatura: interpolate_string(input_object, username)
Comportamento:
  - str  → substitui todas as ocorrências de "{}" por username
  - dict → aplica recursivamente nos valores
  - list → aplica recursivamente nos elementos
  - outros tipos → retorna sem alteração
"""


# ---------------------------------------------------------------------------
# Particionamento de Equivalência
# ---------------------------------------------------------------------------

class TestInterpolateStringParticionamento:
    """CE – classes de equivalência para o parâmetro input_object."""

    # --- CE1: input_object é str com "{}" ---
    def test_str_com_placeholder(self):
        """CE1 – str contém "{}": deve substituir pelo username."""
        assert interpolate_string("{}test", "user") == "usertest"

    