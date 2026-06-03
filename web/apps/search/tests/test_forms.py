import pytest
from apps.search.forms import SearchForm

def test_form_accepts_valid_username():
    """Teste 1: SearchForm({'username':'john_doe'}) é válido."""
    form = SearchForm({'username': 'john_doe'})
    assert form.is_valid() is True

def test_form_rejects_empty_username():
    """Teste 2: Username vazio -> form inválido com erro em username."""
    form = SearchForm({'username': ''})
    assert form.is_valid() is False
    assert 'username' in form.errors

def test_form_rejects_invalid_chars():
    """Teste 3: 'jo hn' -> inválido."""
    form = SearchForm({'username': 'jo hn'})
    assert form.is_valid() is False
    assert 'username' in form.errors
    assert form.errors['username'][0] == 'Nome de usuário contém caracteres inválidos.'