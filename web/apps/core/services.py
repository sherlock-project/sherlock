from typing import Iterator
from .dtos import SearchRequest, SiteResult
from sherlock_project.sherlock import sherlock  # importado para permitir mock nos testes

class SherlockService:
    def search(self, req: SearchRequest) -> Iterator[SiteResult]:
        raise NotImplementedError("A implementação real será feita pela Dupla 1")