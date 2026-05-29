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

    # --- CE2: input_object é str sem "{}" ---
    def test_str_sem_placeholder(self):
        """CE2 – str sem "{}": deve retornar a string inalterada."""
        assert interpolate_string("semplaceholder", "user") == "semplaceholder"

    # --- CE3: input_object é dict ---
    def test_dict_com_placeholder_nos_valores(self):
        """CE3 – dict com valores string contendo "{}": substitui em cada valor."""
        entrada = {"url": "https://site.com/{}/perfil", "id": "{}"}
        esperado = {"url": "https://site.com/joao/perfil", "id": "joao"}
        assert interpolate_string(entrada, "joao") == esperado

    def test_dict_vazio(self):
        """CE3b – dict vazio: deve retornar dict vazio."""
        assert interpolate_string({}, "user") == {}
