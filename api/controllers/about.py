from fastapi import APIRouter, Query

from api.dependencies import get_about_use_case

router = APIRouter(tags=["О колледже"])


@router.get("/pages/about")
async def get_about_pages(page: int = Query(1, ge=1)):
    """Получить страницы раздела «О колледже»"""
    uc = get_about_use_case()
    dto = uc.execute(page)
    
    if dto is None:
        return {"error": "Страница не найдена"}
    
    return {
        "title": dto.title,
        "content": dto.content,
        "files": dto.files,
        "page": dto.page,
        "total_pages": dto.total_pages
    }