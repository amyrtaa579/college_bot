from fastapi import APIRouter, Query, HTTPException

from api.dependencies import get_specialties_use_case, _fact_repo

router = APIRouter(tags=["Специальности"])
PAGE_SIZE = 3


@router.get("/specialties")
async def get_specialties_list(page: int = Query(1, ge=1)):
    """Получить список специальностей (пагинированный)"""
    uc = get_specialties_use_case()
    result = uc.get_list(page)
    
    return {
        "items": [
            {"id": s.id, "code": s.code, "name": s.name}
            for s in result.items
        ],
        "page": result.page,
        "total_pages": result.total_pages,
        "total": result.total
    }


@router.get("/specialties/{specialty_id}")
async def get_specialty_detail(specialty_id: int, page: int = Query(1, ge=1)):
    """Получить детальную информацию о специальности"""
    uc = get_specialties_use_case()
    dto = uc.get_detail(specialty_id, page)
    
    if dto is None:
        raise HTTPException(status_code=404, detail="Специальность не найдена")
    
    return {
        "id": dto.id,
        "code": dto.code,
        "name": dto.name,
        "profiles": dto.profiles,
        "page": {
            "title": dto.page.title,
            "content": dto.page.content,
            "files": dto.page.files,
            "page": dto.page.page,
            "total_pages": dto.page.total_pages
        },
        "has_facts": dto.has_facts
    }


@router.get("/specialties/{specialty_id}/facts")
async def get_specialty_facts(specialty_id: int, page: int = Query(1, ge=1)):
    """Получить список интересных фактов о специальности"""
    result = _fact_repo.get_list(specialty_id, page, PAGE_SIZE)
    
    return {
        "items": [
            {"id": f.id, "title": f.title}
            for f in result.items
        ],
        "page": result.page,
        "total_pages": result.total_pages
    }
