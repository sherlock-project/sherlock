from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from .forms import SearchForm
from apps.core.services import SherlockService
from apps.core.dtos import SearchRequest
from apps.core.exceptions import ServiceTimeoutError

def index_view(request):
    pass

def results_view(request):
    pass