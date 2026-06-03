import pytest
from sherlock_project.sherlock import interpolate_string

"""
Testes de caixa-preta e caixa-branca para interpolate_string().

  Caixa-preta  → Particionamento de Equivalência (CE) + Análise de Valor Limite (VL)
  Caixa-branca → Cobertura de Decisões/Branches (CB) + análise de MC/DC

Código analisado (sherlock_project/sherlock.py, linhas 146-153):

    def interpolate_string(input_object, username):
        if isinstance(input_object, str):                              # L147
            return input_object.replace("{}", username)                # L148
        elif isinstance(input_object, dict):                           # L149
            return {k: interpolate_string(v, username)                 # L150
                    for k, v in input_object.items()}
        elif isinstance(input_object, list):                           # L151
            return [interpolate_string(i, username) for i in input_object]  # L152
        return input_object                                            # L153

Condições identificadas:
    C1 = isinstance(input_object, str)
    C2 = isinstance(input_object, dict)   [avaliada somente quando C1=False]
    C3 = isinstance(input_object, list)   [avaliada somente quando C1=False e C2=False]

Branches (B):
    B1 – C1=True               → executa str.replace (L148)
    B2 – C1=False, C2=True     → recursão no dict    (L150)
    B3 – C1=False, C2=False, C3=True  → recursão na list (L152)
    B4 – C1=False, C2=False, C3=False → retorna sem alteração (L153)

Nota sobre MC/DC:
    MC/DC é aplicável a decisões com DUAS OU MAIS condições booleanas combinadas
    por 'and'/'or'. Cada if/elif nesta função contém uma única condição (isinstance).
    Não existem decisões compostas — MC/DC reduz-se, aqui, à cobertura de decisão
    simples, que é idêntica à cobertura de branches. Isso é declarado explicitamente
    para demonstrar compreensão do critério; não é omissão.
"""


# ---------------------------------------------------------------------------
# Particionamento de Equivalência (Caixa-Preta)
# ---------------------------------------------------------------------------

class TestInterpolateStringParticionamento:
    """CE – classes de equivalência para o parâmetro input_object."""

    # CE1: str com "{}"
    def test_str_com_placeholder(self):
        assert interpolate_string("{}test", "user") == "usertest"

    # CE2: str sem "{}"
    def test_str_sem_placeholder(self):
        assert interpolate_string("semplaceholder", "user") == "semplaceholder"

    # CE3: dict
    def test_dict_com_placeholder_nos_valores(self):
        entrada = {"url": "https://site.com/{}/perfil", "id": "{}"}
        esperado = {"url": "https://site.com/joao/perfil", "id": "joao"}
        assert interpolate_string(entrada, "joao") == esperado

    def test_dict_vazio(self):
        assert interpolate_string({}, "user") == {}

    # CE4: list
    def test_list_com_placeholder(self):
        assert interpolate_string(["{}a", "b{}", "c"], "x") == ["xa", "bx", "c"]

    def test_list_vazia(self):
        assert interpolate_string([], "user") == []

    # CE5: outros tipos
    def test_none_retorna_none(self):
        assert interpolate_string(None, "user") is None

    def test_int_retorna_mesmo_valor(self):
        assert interpolate_string(42, "user") == 42

    def test_bool_retorna_mesmo_valor(self):
        assert interpolate_string(True, "user") is True


# ---------------------------------------------------------------------------
# Análise de Valor Limite (Caixa-Preta)
# ---------------------------------------------------------------------------

class TestInterpolateStringValorLimite:
    """VL – valores nos limites dos domínios de entrada."""

    # VL1: username vazio
    def test_username_vazio(self):
        assert interpolate_string("prefix{}suffix", "") == "prefixsuffix"

    # VL2: username com 1 caractere
    def test_username_um_caractere(self):
        assert interpolate_string("{}ok", "a") == "aok"

    # VL3: string = somente "{}"
    def test_str_somente_placeholder(self):
        assert interpolate_string("{}", "abc") == "abc"

    # VL4: string vazia
    def test_str_vazia(self):
        assert interpolate_string("", "user") == ""

    # VL5: múltiplos "{}" — verifica que replace substitui TODAS as ocorrências
    def test_multiplos_placeholders(self):
        assert interpolate_string("{}-{}-{}", "x") == "x-x-x"

    # VL6: dict com 1 par
    def test_dict_um_par(self):
        assert interpolate_string({"k": "{}"}, "v") == {"k": "v"}

    # VL7: list com 1 elemento
    def test_list_um_elemento(self):
        assert interpolate_string(["{}"], "z") == ["z"]

    # VL8: list aninhada (list dentro de list)
    def test_list_aninhada(self):
        assert interpolate_string([["{}"], "{}"], "r") == [["r"], "r"]

    # VL9: dict aninhado (dict dentro de dict)
    def test_dict_aninhado(self):
        assert interpolate_string({"outer": {"inner": "{}"}}, "deep") == \
               {"outer": {"inner": "deep"}}


# ---------------------------------------------------------------------------
# Cobertura de Branches / Decisões (Caixa-Branca)
# ---------------------------------------------------------------------------

class TestInterpolateStringCaixaBranca:
    """
    Testes estruturais: garantem que todos os branches do if/elif/else
    sejam exercitados. Também cobrem chamadas recursivas que atingem
    branches distintos dentro da mesma invocação.

    Tabela de cobertura de decisões:

        Caso  | C1(str) | C2(dict) | C3(list) | Branch exercitado
        ------|---------|----------|----------|-------------------
        CB-01 |    T    |    —     |    —     | B1 (L148)
        CB-02 |    F    |    T     |    —     | B2 (L150)
        CB-03 |    F    |    F     |    T     | B3 (L152)
        CB-04 |    F    |    F     |    F     | B4 (L153)

    Pares de independência (análogo a MC/DC, já que cada decisão tem 1 condição):
        C1: (CB-01 vs CB-02) — única diferença é C1; saída muda de B1 para B2
        C2: (CB-02 vs CB-03) — única diferença é C2; saída muda de B2 para B3
        C3: (CB-03 vs CB-04) — única diferença é C3; saída muda de B3 para B4
    """

    # --- Branch B1: isinstance(input_object, str) = True (L148) ---
    def test_CB01_branch_str(self):
        """CB-01 – C1=True: executa str.replace, retorna string com substituição."""
        assert interpolate_string("/{}/profile", "alice") == "/alice/profile"

    # --- Branch B2: C1=False, isinstance(input_object, dict) = True (L150) ---
    def test_CB02_branch_dict(self):
        """CB-02 – C1=False, C2=True: cobre o branch do dict."""
        assert interpolate_string({"endpoint": "/{}"}, "bob") == {"endpoint": "/bob"}

    # --- Branch B3: C1=False, C2=False, isinstance(input_object, list) = True (L152) ---
    def test_CB03_branch_list(self):
        """CB-03 – C1=False, C2=False, C3=True: cobre o branch da list."""
        assert interpolate_string(["/{}"], "carol") == ["/carol"]

    # --- Branch B4: todos False, linha L153 ---
    def test_CB04_branch_default_float(self):
        """CB-04 – C1=C2=C3=False: float passa pelo branch default sem alteração."""
        assert interpolate_string(3.14, "user") == 3.14

    def test_CB04_branch_default_bytes(self):
        """CB-04b – bytes também cai no branch default (não é str/dict/list)."""
        valor = b"{}dados"
        assert interpolate_string(valor, "user") is valor

    # --- Recursão: B2 → B4 (dict com valor não-str/dict/list) ---
    def test_CB_recursao_B2_para_B4(self):
        """
        Motivação estrutural: o branch B2 chama interpolate_string recursivamente
        sobre CADA valor do dict. Se o valor for um int, a recursão deve cair no
        branch B4 e retornar o inteiro inalterado.
        Gap identificado: os testes de caixa-preta usaram apenas strings como
        valores de dict (CE3, VL6), nunca testando o caminho B2→B4.
        """
        assert interpolate_string({"count": 5, "label": "{}"}, "x") == \
               {"count": 5, "label": "x"}

    # --- Recursão: B3 → B4 (list com elementos não-str/dict/list) ---
    def test_CB_recursao_B3_para_B4(self):
        """
        B3 chama interpolate_string recursivamente sobre CADA elemento da list.
        Elemento None aciona B4 e é retornado sem alteração.
        Gap identificado: os testes de caixa-preta testaram lists apenas com strings.
        """
        assert interpolate_string(["{}", None, 99], "v") == ["v", None, 99]

    # --- Recursão: B2 → B3 (dict cujo valor é list) ---
    def test_CB_recursao_B2_para_B3(self):
        """B2 (dict) → recursão no valor → B3 (list) → recursão no elemento → B1 (str)."""
        assert interpolate_string({"urls": ["{}", "{}/extra"]}, "u") == \
               {"urls": ["u", "u/extra"]}

    # --- Recursão: B3 → B2 (list cujos elementos são dicts) ---
    def test_CB_recursao_B3_para_B2(self):
        """B3 (list) → recursão no elemento → B2 (dict) → recursão no valor → B1 (str)."""
        assert interpolate_string([{"k": "{}"}], "v") == [{"k": "v"}]

    # --- Recursão profundidade 3: B2 → B3 → B1 ---
    def test_CB_recursao_profundidade_3(self):
        """
        Percurso completo B2→B3→B1 em uma única chamada.
        Garante que os três branches principais são acionados via recursão.
        """
        assert interpolate_string({"data": ["{}prefix"]}, "TEST") == \
               {"data": ["TESTprefix"]}
