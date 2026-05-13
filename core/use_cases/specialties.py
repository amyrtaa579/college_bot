from dataclasses import dataclass

from core.entities.models import PaginatedResult
from core.use_cases.about_college import PageDTO


@dataclass
class SpecialtyListItem:
    id: int
    code: str
    name: str


@dataclass
class SpecialtyDetailDTO:
    id: int
    code: str
    name: str
    profiles: list[dict]
    page: "PageDTO"
    has_facts: bool


class ViewSpecialtiesUseCase:
    """Просмотр каталога специальностей"""
    
    def __init__(self, specialty_repo: "SpecialtyRepository", 
                 fact_repo: "FactRepository", page_size: int):
        self._specialty_repo = specialty_repo
        self._fact_repo = fact_repo
        self._page_size = page_size
    
    def get_list(self, page: int = 1) -> "PaginatedResult":
        """Получить список специальностей"""
        result = self._specialty_repo.get_list(page, self._page_size)
        items = [SpecialtyListItem(id=s.id, code=s.code, name=s.name) 
                 for s in result.items]
        return PaginatedResult(items=items, total=result.total, 
                               page=result.page, page_size=result.page_size)
    
    def get_detail(self, specialty_id: int, page: int = 1) -> SpecialtyDetailDTO | None:
        """Получить детальную информацию о специальности"""
        spec = self._specialty_repo.get_by_id(specialty_id)
        if spec is None:
            return None
        
        pages_result = self._specialty_repo.get_description_pages(
            specialty_id, page, self._page_size
        )
        if not pages_result.items:
            return None
        
        p = pages_result.items[0]
        page_dto = PageDTO(
            title=p.title, content=p.content,
            files=[{"uuid": f.uuid, "filename": f.filename, 
                    "mime_type": f.mime_type} for f in p.files],
            page=pages_result.page, total_pages=pages_result.total_pages
        )
        
        facts_result = self._fact_repo.get_list(specialty_id, 1, 1)
        
        return SpecialtyDetailDTO(
            id=spec.id, code=spec.code, name=spec.name,
            profiles=[{"level": pr.education_level, 
                       "budget": pr.budget_places, 
                       "paid": pr.paid_places} for pr in spec.profiles],
            page=page_dto,
            has_facts=facts_result.total > 0
        )
