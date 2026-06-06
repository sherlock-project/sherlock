from django.http import HttpResponse
from django.views import View

from apps.core.dtos import SearchRequest
from apps.core.services import SherlockService

from .exporters import to_csv, to_json

_VALID_FORMATS = {"csv", "json"}


class ExportView(View):
    def get(self, request):
        username = request.GET.get("username", "").strip()
        fmt = request.GET.get("format", "").strip()

        if not username:
            return HttpResponse("username is required", status=400)

        if fmt not in _VALID_FORMATS:
            return HttpResponse(f"format must be one of: {', '.join(_VALID_FORMATS)}", status=400)

        results = list(SherlockService().search(SearchRequest(username=username)))

        if fmt == "csv":
            return HttpResponse(to_csv(results), content_type="text/csv")

        return HttpResponse(to_json(results, username), content_type="application/json")
