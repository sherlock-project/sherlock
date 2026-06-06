from django.urls import path

from .views import ExportView

urlpatterns = [
    path("export/", ExportView.as_view(), name="export"),
]
