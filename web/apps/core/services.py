from typing import Iterator
from .dtos import SearchRequest, SiteResult

class SherlockService:
    def search(self, req: SearchRequest) -> Iterator[SiteResult]:
        raise NotImplementedError("A implementação real será feita pela Dupla 1")