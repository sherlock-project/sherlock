"""
Testes — Dupla 1 (SherlockService).

Técnica: TDD (ciclo Red → Green → Refactor).

Testes deste arquivo:
  #1  test_search_returns_results_for_known_user        — GREEN (Dia 2)
  #1b test_search_result_has_correct_url                — GREEN (Dia 2)
  #2  test_search_rejects_empty_username                — GREEN (Dia 2)
  #2b test_search_rejects_empty_username_without_...    — GREEN (Dia 2)
  #6  test_site_result_mapping_status_found             — GREEN (Dia 2)
  #7  test_site_result_mapping_status_not_found         — GREEN (Dia 2)
"""


from unittest.mock import patch

import pytest
from sherlock_project.result import QueryResult, QueryStatus

from apps.core.dtos import SearchRequest, SiteResult
from apps.core.exceptions import InvalidUsernameError
from apps.core.services import SherlockService


def _make_query_result(username: str, site: str, url: str, status: QueryStatus) -> dict:
    """Monta a estrutura de retorno que sherlock() produz para um único site."""
    return {
        "url_main": f"https://{site.lower()}.com",
        "url_user": url,
        "status": QueryResult(
            username=username,
            site_name=site,
            site_url_user=url,
            status=status,
            query_time=0.5,
        ),
    }


@pytest.fixture
def service():
    return SherlockService()


@pytest.fixture
def two_found_results():
    """Resposta mockada de sherlock() com 2 sites encontrados."""
    return {
        "GitHub": _make_query_result(
            "torvalds", "GitHub", "https://github.com/torvalds", QueryStatus.CLAIMED
        ),
        "Twitter": _make_query_result(
            "torvalds", "Twitter", "https://twitter.com/torvalds", QueryStatus.CLAIMED
        ),
    }


# ---------------------------------------------------------------------------
# Teste #1 — serviço entrega SiteResult para cada hit retornado pelo mock
# ---------------------------------------------------------------------------

class TestSearchReturnsResults:

    def test_search_returns_results_for_known_user(self, service, two_found_results):
        """
        Dado: mock de sherlock() devolvendo 2 sites com status CLAIMED.
        Quando: SherlockService.search() é chamado com username válido.
        Então: retorna 2 SiteResult com status "found" e URLs corretas.

        """
        req = SearchRequest(username="torvalds")

        with patch("apps.core.services.sherlock", return_value=two_found_results):
            with patch("apps.core.services.SitesInformation"):
                results = list(service.search(req))

        assert len(results) == 2
        assert all(isinstance(r, SiteResult) for r in results)
        assert all(r.status == "found" for r in results)

        site_names = {r.site_name for r in results}
        assert site_names == {"GitHub", "Twitter"}

    def test_search_result_has_correct_url(self, service, two_found_results):
        """
        Complementar ao #1: cada SiteResult deve carregar a URL do perfil.

        """
        req = SearchRequest(username="torvalds")

        with patch("apps.core.services.sherlock", return_value=two_found_results):
            with patch("apps.core.services.SitesInformation"):
                results = list(service.search(req))

        urls = {r.url for r in results}
        assert "https://github.com/torvalds" in urls
        assert "https://twitter.com/torvalds" in urls


# ---------------------------------------------------------------------------
# Teste #2 — username vazio levanta InvalidUsernameError
# ---------------------------------------------------------------------------

class TestSearchValidatesUsername:

    def test_search_rejects_empty_username(self, service):
        """
        Dado: SearchRequest com username vazio.
        Quando: SherlockService.search() é chamado.
        Então: levanta InvalidUsernameError antes de qualquer chamada de rede.
        """
        req = SearchRequest(username="")

        with pytest.raises(InvalidUsernameError):
            list(service.search(req))

    def test_search_rejects_empty_username_without_network_call(self, service):
        """
        Complementar ao #2: a validação deve ocorrer ANTES de chamar sherlock(),
        portanto nenhuma chamada de rede deve ser feita.
        """
        req = SearchRequest(username="")

        with patch("apps.core.services.sherlock") as mock_sherlock:
            with pytest.raises(InvalidUsernameError):
                list(service.search(req))

            mock_sherlock.assert_not_called()


# ---------------------------------------------------------------------------
# Teste #6 — QueryStatus.CLAIMED mapeia para "found"
# ---------------------------------------------------------------------------

class TestSiteResultStatusMapping:

    def test_site_result_mapping_status_found(self, service):
        """
        Dado: mock de sherlock() devolvendo 1 site com status CLAIMED.
        Quando: SherlockService.search() é chamado.
        Então: o SiteResult resultante tem status "found".
        """
        mock_results = {
            "GitHub": _make_query_result(
                "torvalds", "GitHub", "https://github.com/torvalds", QueryStatus.CLAIMED
            ),
        }
        req = SearchRequest(username="torvalds")

        with patch("apps.core.services.sherlock", return_value=mock_results):
            with patch("apps.core.services.SitesInformation"):
                results = list(service.search(req))

        assert len(results) == 1
        assert results[0].status == "found"

    # -----------------------------------------------------------------------
    # Teste #7 — QueryStatus.AVAILABLE mapeia para "not_found"
    # -----------------------------------------------------------------------

    def test_site_result_mapping_status_not_found(self, service):
        """
        Dado: mock de sherlock() devolvendo 1 site com status AVAILABLE.
        Quando: SherlockService.search() é chamado.
        Então: o SiteResult resultante tem status "not_found".
        """
        mock_results = {
            "GitHub": _make_query_result(
                "nonexistent_user_xyz", "GitHub",
                "https://github.com/nonexistent_user_xyz", QueryStatus.AVAILABLE
            ),
        }
        req = SearchRequest(username="nonexistent_user_xyz")

        with patch("apps.core.services.sherlock", return_value=mock_results):
            with patch("apps.core.services.SitesInformation"):
                results = list(service.search(req))

        assert len(results) == 1
        assert results[0].status == "not_found"
