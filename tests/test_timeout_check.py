import pytest
from argparse import ArgumentTypeError
from sherlock_project.sherlock import timeout_check

# TESTES CAIXA-PRETA, COMPLEMENTADO POR CAIXA-BRANCA: timeout_check()
# Particionamento de Equivalência e Valor Limite
# O limite definido na regra de negócio é "maior que 0.0"

def test_timeout_lower_bound_valid_float():
    """Testa um valor válido na borda do intervalo aceito."""
    assert timeout_check("0.1") == 0.1

def test_timeout_zero_boundary():
    """Testa exatamente a borda do valor limite inferior (0.0)."""
    with pytest.raises(ArgumentTypeError, match="Timeout must be a positive number"):
        timeout_check("0")

def test_timeout_negative_out_of_bounds():
    """Testa um valor no intervalo inválido."""
    with pytest.raises(ArgumentTypeError, match="Timeout must be a positive number"):
        timeout_check("-1.5")

# CAIXA-BRANCA
# Precisamos forçar a entrada no bloco "except" da função
def test_timeout_invalid_string_branch():
    """Força a execução da exceção no cast de float."""
    with pytest.raises(ValueError, match="could not convert string to float"):
        timeout_check("texto_invalido")
