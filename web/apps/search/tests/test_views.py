import pytest
from django.urls import reverse
from apps.core.dtos import SiteResult, SearchRequest
from apps.core.exceptions import ServiceTimeoutError

pytestmark = pytest.mark.django_db

def test_index_view_get_renders_form(client):
    """Teste 4: GET / retorna 200 e contém o form."""
    url = reverse('search:index')
    response = client.get(url)
    
    assert response.status_code == 200
    content = response.content.decode()
    assert 'data-testid="search-form"' in content
    assert 'data-testid="username-input"' in content
    assert 'data-testid="submit-btn"' in content

def test_results_view_post_invalid_returns_form_with_errors(client):
    """Teste 5: POST sem username -> 200 + erro renderizado."""
    url = reverse('search:results')
    response = client.post(url, {'username': ''})
    
    assert response.status_code == 200
    content = response.content.decode()
    assert 'Este campo é obrigatório.' in content
    assert 'data-testid="search-form"' in content

def test_results_view_post_valid_calls_service_with_username(client, mocker):
    """Teste 6: POST válido invoca SherlockService.search com SearchRequest."""
    mock_service = mocker.patch('apps.search.views.SherlockService.search', return_value=[])
    
    url = reverse('search:results')
    client.post(url, {'username': 'torvalds'})
    
    mock_service.assert_called_once()
    called_request = mock_service.call_args[0][0]
    assert isinstance(called_request, SearchRequest)
    assert called_request.username == 'torvalds'

def test_results_view_renders_hits(client, mocker):
    """Teste 7: Página de resultados mostra todos os SiteResult."""
    fake_results = [
        SiteResult(site_name='GitHub', url='https://github.com/torvalds', status='found', response_time_ms=100, error_message=None),
        SiteResult(site_name='Reddit', url='https://reddit.com/user/torvalds', status='not_found', response_time_ms=50, error_message=None)
    ]
    mocker.patch('apps.search.views.SherlockService.search', return_value=fake_results)
    
    url = reverse('search:results')
    response = client.post(url, {'username': 'torvalds'})
    
    content = response.content.decode()
    assert 'data-testid="results-list"' in content
    assert 'data-testid="result-row"' in content
    assert 'GitHub' in content
    assert 'Reddit' in content

def test_results_view_renders_empty_state(client, mocker):
    """Teste 8: Zero resultados renderiza empty-state."""
    mocker.patch('apps.search.views.SherlockService.search', return_value=[])
    
    url = reverse('search:results')
    response = client.post(url, {'username': 'ghost_user_999'})
    
    content = response.content.decode()
    assert 'data-testid="empty-state"' in content

def test_results_view_renders_error_on_timeout(client, mocker):
    """Teste 9: Quando service levanta ServiceTimeoutError, mostra error-state."""
    mocker.patch('apps.search.views.SherlockService.search', side_effect=ServiceTimeoutError("Timeout"))
    
    url = reverse('search:results')
    response = client.post(url, {'username': 'torvalds'})
    
    content = response.content.decode()
    assert 'data-testid="error-state"' in content
    assert 'Timeout ao consultar o serviço upstream.' in content