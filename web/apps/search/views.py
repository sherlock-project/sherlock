from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from .forms import SearchForm
from apps.core.services import SherlockService
from apps.core.dtos import SearchRequest
from apps.core.exceptions import ServiceTimeoutError

def index_view(request):
    if request.method == 'GET':
        form = SearchForm()
        return render(request, 'search/index.html', {'form': form})
    return HttpResponseNotAllowed(['GET'])

def results_view(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        
        if not form.is_valid():
            return render(request, 'search/index.html', {'form': form})

        username = form.cleaned_data['username']
        search_request = SearchRequest(username=username, sites=None, timeout=30.0)
        service = SherlockService()

        try:
            results = list(service.search(search_request))
            context = {
                'username': username,
                'results': results,
                'is_empty': len(results) == 0
            }
            return render(request, 'search/results.html', context)
            
        except ServiceTimeoutError:
            return render(request, 'search/results.html', {'error': 'Timeout ao consultar o serviço upstream.'})
            
    return HttpResponseNotAllowed(['POST'])