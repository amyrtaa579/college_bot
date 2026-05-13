from dataclasses import dataclass
from core.entities.models import PaginatedResult, Specialty, ImportantDate
from core.use_cases.about_college import PageDTO
@dataclass
class AdmissionSpecialtyItem:
    id: int
    code: str
    name: str
    profiles: list[dict]


class ViewAdmissionUseCase:
    """Просмотр раздела «Приёмная комиссия»"""
    
    def __init__(self, page_repo, admission_repo, page_size: int):
        self._page_repo = page_repo
        self._admission_repo = admission_repo
        self._page_size = page_size
    
    def get_rules(self, page: int = 1) -> PageDTO | None:
        """Описание и правила"""
        result = self._page_repo.get_by_section("admission-rules", page, self._page_size)
        if not result.items:
            return None
        p = result.items[0]
        return PageDTO(
            title=p.title, content=p.content,
            files=[{"uuid": f.uuid, "filename": f.filename,
                    "mime_type": f.mime_type} for f in p.files],
            page=result.page, total_pages=result.total_pages
        )
    
    def get_specialties_table(self, page: int = 1) -> "PaginatedResult":
        """Таблица специальностей ПК"""
        return self._admission_repo.get_specialties_table(page, self._page_size)
    
    def get_dates_list(self, page: int = 1) -> "PaginatedResult":
        """Список важных дат"""
        return self._admission_repo.get_important_dates(page, self._page_size)
    
    def get_date_detail(self, date_id: int, page: int = 1) -> PageDTO | None:
        """Детальная информация о дате"""
        date = self._admission_repo.get_date_by_id(date_id)
        if date is None:
            return None
        
        result = self._admission_repo.get_date_pages(date_id, page, self._page_size)
        if not result.items:
            return None
        
        p = result.items[0]
        return PageDTO(
            title=f"{date.short_title}\n{p.title}",
            content=p.content,
            files=[{"uuid": f.uuid, "filename": f.filename,
                    "mime_type": f.mime_type} for f in p.files],
            page=result.page, total_pages=result.total_pages
        )