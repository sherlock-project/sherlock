import re

from django import forms


class SearchForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        error_messages={'required': 'Este campo é obrigatório.'},
        widget=forms.TextInput(attrs={'data-testid': 'username-input'}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            raise forms.ValidationError('Nome de usuário contém caracteres inválidos.')
        return username
