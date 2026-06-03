from typing import Iterator

from sherlock_project.sherlock import (
    sherlock,  # noqa: F401 — necessário para patch nos testes
)

from .dtos import SearchRequest, SiteResult


class SherlockService:
    def search(self, req: SearchRequest) -> Iterator[SiteResult]:
        raise NotImplementedError("A implementação real será feita pela Dupla 1")
