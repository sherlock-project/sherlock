import pytest
from argparse import ArgumentTypeError
from sherlock_project.sherlock import timeout_check
from sherlock_project.sites import SitesInformation

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


# TESTES CAIXA-BRANCA, COMPLEMENTADO POR CAIXA-PRETA: remove_nsfw_sites()
class MockSite:
    """Classe falsa para imitar a estrutura de objetos do Sherlock"""
    def __init__(self, is_nsfw):
        self.is_nsfw = is_nsfw

@pytest.fixture
def mock_sites_info():
    """Fixture para inicializar o objeto real mas isolar a base de dados"""
    info = SitesInformation()
    
    info.sites = {
        "SiteAdulto": MockSite(is_nsfw=True),
        "SiteComum": MockSite(is_nsfw=False),
        "SiteAdultoExcecao": MockSite(is_nsfw=True)
    }
    return info

def test_nsfw_mcdc_true_true(mock_sites_info):
    mock_sites_info.remove_nsfw_sites(do_not_remove=[])
    assert "SiteAdulto" not in mock_sites_info.sites

def test_nsfw_mcdc_true_false(mock_sites_info):
    mock_sites_info.remove_nsfw_sites(do_not_remove=["SiteAdultoExcecao"])
    # Como o mock_sites_info transforma tudo em minúsculas, a checagem se mantém
    assert "SiteAdultoExcecao" in mock_sites_info.sites

def test_nsfw_mcdc_false_x(mock_sites_info):
    mock_sites_info.remove_nsfw_sites(do_not_remove=[])
    assert "SiteComum" in mock_sites_info.sites