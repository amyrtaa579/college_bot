from dataclasses import dataclass


@dataclass
class PageDTO:
    title: str
    content: str
    files: list[dict]  # [{uuid, filename, mime_type}]
    page: int
    total_pages: int


class ViewAboutCollegeUseCase:
    """Просмотр раздела «О колледже»"""
    
    def __init__(self, page_repo: "PageRepository", page_size: int):
        self._repo = page_repo
        self._page_size = page_size
    
    def execute(self, page: int = 1) -> PageDTO | None:
        result = self._repo.get_by_section("about", page, self._page_size)
        if not result.items:
            return None
        
        p = result.items[0]
        return PageDTO(
            title=p.title,
            content=p.content,
            files=[{"uuid": f.uuid, "filename": f.filename, 
                    "mime_type": f.mime_type} for f in p.files],
            page=result.page,
            total_pages=result.total_pages
        )