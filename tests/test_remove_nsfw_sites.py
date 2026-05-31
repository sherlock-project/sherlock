import pytest
from argparse import ArgumentTypeError
from sherlock_project.sites import SitesInformation

# TESTES CAIXA-BRANCA (MC/DC), COMPLEMENTADO POR CAIXA-PRETA: remove_nsfw_sites()
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