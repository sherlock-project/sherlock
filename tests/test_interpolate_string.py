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
        
   # --- CE4: input_object é list ---
    def test_list_com_placeholder(self):
        """CE4 – list com strings contendo "{}": substitui em todos os elementos."""
        entrada = ["{}a", "b{}", "c"]
        assert interpolate_string(entrada, "x") == ["xa", "bx", "c"]

    def test_list_vazia(self):
        """CE4b – list vazia: deve retornar list vazia."""
        assert interpolate_string([], "user") == []

    # --- CE5: input_object é de outro tipo ---
    def test_none_retorna_none(self):
        """CE5a – None: deve retornar None sem alteração."""
        assert interpolate_string(None, "user") is None

    def test_int_retorna_mesmo_valor(self):
        """CE5b – int: deve retornar o mesmo valor sem alteração."""
        assert interpolate_string(42, "user") == 42

    def test_bool_retorna_mesmo_valor(self):
        """CE5c – bool: deve retornar o mesmo valor sem alteração."""
        assert interpolate_string(True, "user") is True


# ---------------------------------------------------------------------------
# Análise de Valor Limite
# ---------------------------------------------------------------------------

class TestInterpolateStringValorLimite:
    """VL – valores nos limites dos domínios de entrada."""

    # --- Limites do username ---
    def test_username_vazio(self):
        """VL1 – username = "": substitui "{}" por string vazia."""
        assert interpolate_string("prefix{}suffix", "") == "prefixsuffix"

    def test_username_um_caractere(self):
        """VL2 – username com exatamente 1 caractere."""
        assert interpolate_string("{}ok", "a") == "aok"

    # --- Limites da string de entrada ---
    def test_str_somente_placeholder(self):
        """VL3 – input_object == "{}": resultado deve ser exatamente o username."""
        assert interpolate_string("{}", "abc") == "abc"

    def test_str_vazia(self):
        """VL4 – input_object == "": resultado deve ser string vazia."""
        assert interpolate_string("", "user") == ""

    def test_multiplos_placeholders(self):
        """VL5 – múltiplos "{}" na mesma string: todos devem ser substituídos."""
        assert interpolate_string("{}-{}-{}", "x") == "x-x-x"

    # --- Limites de estruturas compostas ---
    def test_dict_um_par(self):
        """VL6 – dict com exatamente 1 par chave-valor."""
        assert interpolate_string({"k": "{}"}, "v") == {"k": "v"}

    def test_list_um_elemento(self):
        """VL7 – list com exatamente 1 elemento."""
        assert interpolate_string(["{}"], "z") == ["z"]

    def test_list_aninhada(self):
        """VL8 – list com list aninhada: deve aplicar recursivamente."""
        assert interpolate_string([["{}"], "{}"], "r") == [["r"], "r"]

    def test_dict_aninhado(self):
        """VL9 – dict com dict aninhado: deve aplicar recursivamente."""
        entrada = {"outer": {"inner": "{}"}}
        assert interpolate_string(entrada, "deep") == {"outer": {"inner": "deep"}}
