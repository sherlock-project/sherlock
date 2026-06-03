"""
Testes RED — Dia 1, Dupla 1 (SherlockService).

Técnica: TDD (ciclo Red → Green → Refactor).
Estes testes foram escritos ANTES da implementação real do SherlockService.
Todos devem FALHAR com a implementação atual (NotImplementedError).

Testes deste arquivo:
  #1 test_search_returns_results_for_known_user
  #2 test_search_rejects_empty_username
"""

import pytest
from unittest.mock import patch, MagicMock

from apps.core.services import SherlockService
from apps.core.dtos import SearchRequest, SiteResult
from apps.core.exceptions import InvalidUsernameError
from sherlock_project.result import QueryResult, QueryStatus


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
# Teste #1 — RED: serviço entrega SiteResult para cada hit retornado pelo mock
# ---------------------------------------------------------------------------

class TestSearchReturnsResults:

    def test_search_returns_results_for_known_user(self, service, two_found_results):
        """
        Dado: mock de sherlock() devolvendo 2 sites com status CLAIMED.
        Quando: SherlockService.search() é chamado com username válido.
        Então: retorna 2 SiteResult com status "found" e URLs corretas.

        RED: falha porque SherlockService.search() levanta NotImplementedError.
        """
        req = SearchRequest(username="torvalds")

        with patch("apps.core.services.sherlock", return_value=two_found_results):
            results = list(service.search(req))

        assert len(results) == 2
        assert all(isinstance(r, SiteResult) for r in results)
        assert all(r.status == "found" for r in results)

        site_names = {r.site_name for r in results}
        assert site_names == {"GitHub", "Twitter"}

    def test_search_result_has_correct_url(self, service, two_found_results):
        """
        Complementar ao #1: cada SiteResult deve carregar a URL do perfil.

        RED: mesmo motivo — NotImplementedError.
        """
        req = SearchRequest(username="torvalds")

        with patch("apps.core.services.sherlock", return_value=two_found_results):
            results = list(service.search(req))

        urls = {r.url for r in results}
        assert "https://github.com/torvalds" in urls
        assert "https://twitter.com/torvalds" in urls


# ---------------------------------------------------------------------------
# Teste #2 — RED: username vazio levanta InvalidUsernameError
# ---------------------------------------------------------------------------

class TestSearchValidatesUsername:

    def test_search_rejects_empty_username(self, service):
        """
        Dado: SearchRequest com username vazio.
        Quando: SherlockService.search() é chamado.
        Então: levanta InvalidUsernameError antes de qualquer chamada de rede.

        RED: falha porque SherlockService.search() levanta NotImplementedError,
             não InvalidUsernameError.
        """
        req = SearchRequest(username="")

        with pytest.raises(InvalidUsernameError):
            list(service.search(req))

    def test_search_rejects_empty_username_without_network_call(self, service):
        """
        Complementar ao #2: a validação deve ocorrer ANTES de chamar sherlock(),
        portanto nenhuma chamada de rede deve ser feita.

        RED: mesmo motivo.
        """
        req = SearchRequest(username="")

        with patch("apps.core.services.sherlock") as mock_sherlock:
            with pytest.raises(InvalidUsernameError):
                list(service.search(req))

            mock_sherlock.assert_not_called()
