from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('results/', views.results_view, name='results'),
]