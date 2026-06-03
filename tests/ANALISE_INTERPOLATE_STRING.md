# Análise de Testes — `interpolate_string`

**Arquivo testado:** `sherlock_project/sherlock.py`, linhas 146–153  
**Arquivo de testes:** `tests/test_interpolate_string.py`  
**Total de casos:** 28 (18 caixa-preta + 10 caixa-branca)  
**Resultado:** 28/28 passando

---

## 1. Código-alvo

```python
def interpolate_string(input_object, username):       # L146
    if isinstance(input_object, str):                 # L147
        return input_object.replace("{}", username)   # L148
    elif isinstance(input_object, dict):              # L149
        return {k: interpolate_string(v, username)    # L150
                for k, v in input_object.items()}
    elif isinstance(input_object, list):              # L151
        return [interpolate_string(i, username)       # L152
                for i in input_object]
    return input_object                               # L153
```

**Comportamento especificado:**

| Tipo de `input_object` | Retorno |
|------------------------|---------|
| `str` | substitui todas as ocorrências de `"{}"` por `username` |
| `dict` | dicionário com mesmas chaves; valores processados recursivamente |
| `list` | lista com elementos processados recursivamente |
| qualquer outro | retorna sem alteração |

---

## 2. Caixa-Preta

### 2.1 Particionamento de Equivalência

**Classe de equivalência para `input_object`:**

| ID  | Classe | Representante | Comportamento esperado |
|-----|--------|---------------|------------------------|
| CE1 | `str` com `"{}"` | `"{}test"` | substitui placeholder |
| CE2 | `str` sem `"{}"` | `"abc"` | retorna inalterado |
| CE3 | `dict` (não-vazio) | `{"url": "/{}"}`  | recursão nos valores |
| CE3b | `dict` vazio | `{}` | retorna `{}` |
| CE4 | `list` (não-vazia) | `["{}a", "b"]` | recursão nos elementos |
| CE4b | `list` vazia | `[]` | retorna `[]` |
| CE5 | outros tipos | `None`, `42`, `True` | retorna sem alteração |

**Testes:** `TestInterpolateStringParticionamento` (9 casos)

### 2.2 Análise de Valor Limite

| ID  | Limite analisado | Entrada | Resultado esperado |
|-----|-----------------|---------|-------------------|
| VL1 | `username` vazio | `("prefix{}suffix", "")` | `"prefixsuffix"` |
| VL2 | `username` com 1 char | `("{}ok", "a")` | `"aok"` |
| VL3 | `input_object` = `"{}"` (só placeholder) | `("{}", "abc")` | `"abc"` |
| VL4 | `input_object` = `""` (string vazia) | `("", "user")` | `""` |
| VL5 | múltiplos `"{}"` | `("{}-{}-{}", "x")` | `"x-x-x"` |
| VL6 | `dict` com 1 par | `({"k": "{}"}, "v")` | `{"k": "v"}` |
| VL7 | `list` com 1 elemento | `(["{}"], "z")` | `["z"]` |
| VL8 | `list` aninhada | `([["{}"], "{}"], "r")` | `[["r"], "r"]` |
| VL9 | `dict` aninhado | `({"outer": {"inner": "{}"}}, "deep")` | `{"outer": {"inner": "deep"}}` |

**Testes:** `TestInterpolateStringValorLimite` (9 casos)

---

## 3. Caixa-Branca

### 3.1 Condições e Branches identificados

```
C1 = isinstance(input_object, str)
C2 = isinstance(input_object, dict)   ← avaliada somente quando C1=False
C3 = isinstance(input_object, list)   ← avaliada somente quando C1=False e C2=False
```

| Branch | Condições para ativação | Linha | Ação |
|--------|------------------------|-------|------|
| B1 | C1 = True | L148 | `str.replace("{}", username)` |
| B2 | C1=False, C2=True | L150 | recursão sobre valores do dict |
| B3 | C1=False, C2=False, C3=True | L152 | recursão sobre elementos da list |
| B4 | C1=False, C2=False, C3=False | L153 | retorna `input_object` sem alteração |

### 3.2 MC/DC — por que não se aplica aqui

O critério **MC/DC** exige decisões com **duas ou mais condições booleanas** combinadas por `and`/`or` dentro de uma mesma expressão. Cada `if`/`elif` desta função contém exatamente **uma condição** (`isinstance`). Não existem decisões compostas.

Neste caso, MC/DC reduz-se matematicamente à cobertura de decisão simples, que já é idêntica à cobertura de branches. Declarar isso explicitamente demonstra compreensão do critério — e não confundir "cadeia de `elif`" com "decisão composta" é justamente o que o critério busca verificar.

> **Para o grupo:** se o trabalho exigir uma demonstração real de MC/DC, deve-se escolher uma função com `and`/`or` nas condições. O `sherlock.py` tem candidatos (`check_for_parameter`, lógicas de detecção de resultado).

### 3.3 Tabela de cobertura de branches

| Caso | C1 | C2 | C3 | Branch | Teste |
|------|----|----|----|---------|-|
| CB-01 | T | — | — | B1 | `test_CB01_branch_str` |
| CB-02 | F | T | — | B2 | `test_CB02_branch_dict` |
| CB-03 | F | F | T | B3 | `test_CB03_branch_list` |
| CB-04 | F | F | F | B4 | `test_CB04_branch_default_float` |
| CB-04b | F | F | F | B4 | `test_CB04_branch_default_bytes` |

### 3.4 Pares de independência por condição

Como cada decisão tem uma condição, o par de independência mostra qual input muda o branch quando apenas aquela condição é alterada:

| Condição | Par | Mudança observada |
|----------|-----|-------------------|
| C1 | (CB-01, CB-02) | C1: T→F; resultado: B1→B2 |
| C2 | (CB-02, CB-03) | C2: T→F (C1=F em ambos); resultado: B2→B3 |
| C3 | (CB-03, CB-04) | C3: T→F (C1=C2=F em ambos); resultado: B3→B4 |

### 3.5 Testes de recursão

A função é recursiva: os branches B2 e B3 chamam `interpolate_string` novamente sobre cada valor/elemento. Os testes de caixa-preta usaram apenas strings dentro de dicts e lists (CE3, VL6–9), o que faz a recursão sempre cair em B1. Os testes de caixa-branca exploram os caminhos recursivos completos:

| Teste | Caminho de branches | Descrição |
|-------|---------------------|-----------|
| `test_CB_recursao_B2_para_B4` | B2 → B4 | dict com valor inteiro |
| `test_CB_recursao_B3_para_B4` | B3 → B4 | list com `None` e `int` |
| `test_CB_recursao_B2_para_B3` | B2 → B3 → B1 | dict cujo valor é list de strings |
| `test_CB_recursao_B3_para_B2` | B3 → B2 → B1 | list cujos elementos são dicts |
| `test_CB_recursao_profundidade_3` | B2 → B3 → B1 | dict → list → str (profundidade 3) |

---

## 4. Integração entre as abordagens

### 4.1 Cobertura estrutural alcançada pelos testes funcionais

Os testes de caixa-preta (CE + VL) **já cobrem todos os 4 branches** da função. Isso ocorre porque a especificação é precisa o suficiente para que cada classe de equivalência corresponda diretamente a um branch:

| Branch | Coberto por (caixa-preta) |
|--------|--------------------------|
| B1 | CE1, CE2, VL1–VL5 |
| B2 | CE3, CE3b, VL6, VL9 |
| B3 | CE4, CE4b, VL7, VL8 |
| B4 | CE5 (None, int, bool) |

**Conclusão:** para esta função, bons testes funcionais são suficientes para 100% de cobertura de branches. Isso não é regra geral — em funções com condições implícitas ou com lógica de negócio desacoplada da especificação, a cobertura estrutural frequentemente revela lacunas.

### 4.2 Lacunas que a análise estrutural revelou

Os testes de caixa-preta **não testaram** os caminhos recursivos onde a chamada interna acessa branches diferentes de B1. Especificamente:

| Lacuna identificada | Causa | Teste criado |
|--------------------|-------|--------------|
| Dict com valor inteiro | CE3 usou apenas strings como valores | `test_CB_recursao_B2_para_B4` |
| List com elementos `None`/`int` | CE4 usou apenas strings como elementos | `test_CB_recursao_B3_para_B4` |
| Dict cujo valor é uma list | VL9 testou dict aninhado (dict→dict), não dict→list | `test_CB_recursao_B2_para_B3` |

Esses são casos em que a **análise de fluxo de execução** (tracing recursivo) encontrou caminhos que a especificação funcional não tornou óbvios.

### 4.3 Trechos cobertos estruturalmente sem validação funcional suficiente

O branch B4 (linha 153) é alcançado pelos testes CE5 (`None`, `int`, `bool`). Porém, esses tipos são passados como `input_object` de nível superior. A análise estrutural mostra que B4 **também é alcançado recursivamente** — quando um dict ou list contém um valor que não é str/dict/list. Antes dos testes de caixa-branca, esse comportamento não tinha validação explícita.

### 4.4 Como a análise estrutural ajudou a identificar lacunas nos testes funcionais

O mapeamento do grafo de chamadas recursivas (`B2 chama interpolate_string sobre cada valor`, `B3 chama sobre cada elemento`) revelou que a especificação funcional implica comportamento para qualquer tipo como valor folha — mas os testes funcionais cobriram apenas o tipo `str` como folha. Isso é um padrão clássico: **testes baseados em especificação tendem a cobrir o "caminho feliz" do tipo especificado**, enquanto a análise estrutural força o testador a considerar todos os tipos que o código pode receber via recursão.

### 4.5 Como os requisitos influenciaram os cenários estruturais

O requisito funcional de VL5 ("múltiplos `{}`") direcionou o teste de `str.replace`, que substitui todas as ocorrências. Isso é relevante estruturalmente porque L148 (`replace`) é o único statement no branch B1 — qualquer bug nessa substituição seria detectado. O requisito motivou o caso de teste que mais stressou a lógica interna do branch.

---

## 5. Evidências de Cobertura

### 5.1 Execução dos testes

```
$ coverage run --rcfile=.coveragerc -m pytest tests/test_interpolate_string.py -v
...
28 passed in 0.18s
```

### 5.2 Relatório de cobertura (arquivo completo)

```
Name                           Stmts   Miss Branch BrPart  Cover
----------------------------------------------------------------
sherlock_project/sherlock.py     387    346    158      1     9%
Missing: 14-17, 71-108, 115-143, 159, 167-170, 211-505, ...
----------------------------------------------------------------
```

> Cobertura de 9% no arquivo completo é esperada — apenas `interpolate_string`
> (L146–153) foi alvo desta suíte. As linhas 146–153 **não aparecem** na lista
> `Missing`, confirmando cobertura de linha de **100% da função**.  
> `BrPart=1` refere-se a outro trecho do arquivo, não à função analisada.

### 5.3 Cobertura de branches da função (verificada manualmente)

| Branch | Linha | Coberto? | Testes que cobrem |
|--------|-------|----------|-------------------|
| B1 (str) | L148 | ✓ | CE1, CE2, VL1–VL5, CB-01 |
| B2 (dict) | L150 | ✓ | CE3, VL6, CB-02, recursões |
| B3 (list) | L152 | ✓ | CE4, VL7, CB-03, recursões |
| B4 (default) | L153 | ✓ | CE5, CB-04, CB-04b, recursões |

**Cobertura de branches da função: 4/4 (100%)**

---

## 6. Rastreabilidade

| Funcionalidade | Requisito/Comportamento | Técnica | Testes |
|----------------|------------------------|---------|--------|
| Substituição de `"{}"` em strings | `str.replace("{}", username)` | CE1, VL3, VL5 | `test_str_com_placeholder`, `test_str_somente_placeholder`, `test_multiplos_placeholders`, `test_CB01_branch_str` |
| String sem placeholder não é alterada | retorno inalterado | CE2 | `test_str_sem_placeholder` |
| Username vazio remove placeholder | `replace("{}", "")` | VL1 | `test_username_vazio` |
| Dict: substituição nos valores | recursão em B2 | CE3, VL6, CB-02 | `test_dict_com_placeholder_nos_valores`, `test_dict_um_par`, `test_CB02_branch_dict` |
| Dict vazio retorna dict vazio | B2, iteração vazia | CE3b | `test_dict_vazio` |
| List: substituição nos elementos | recursão em B3 | CE4, VL7, CB-03 | `test_list_com_placeholder`, `test_list_um_elemento`, `test_CB03_branch_list` |
| List vazia retorna list vazia | B3, iteração vazia | CE4b | `test_list_vazia` |
| Outros tipos retornam sem alteração | B4 (default) | CE5, CB-04 | `test_none_retorna_none`, `test_int_retorna_mesmo_valor`, `test_bool_retorna_mesmo_valor`, `test_CB04_branch_default_float` |
| Recursão: dict com valor não-string | B2 → B4 | CB (branco) | `test_CB_recursao_B2_para_B4` |
| Recursão: list com elemento não-string | B3 → B4 | CB (branco) | `test_CB_recursao_B3_para_B4` |
| Recursão profunda dict→list→str | B2 → B3 → B1 | CB (branco) | `test_CB_recursao_B2_para_B3`, `test_CB_recursao_profundidade_3` |
| Recursão list→dict→str | B3 → B2 → B1 | CB (branco) | `test_CB_recursao_B3_para_B2` |
| Estruturas aninhadas | recursão multinível | VL8, VL9 | `test_list_aninhada`, `test_dict_aninhado` |
