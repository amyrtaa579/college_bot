from fastapi import APIRouter, Query, HTTPException

from api.dependencies import get_admission_use_case, _admission_repo

router = APIRouter(tags=["Приёмная комиссия"])
PAGE_SIZE = 3


@router.get("/admission/rules")
async def get_admission_rules(page: int = Query(1, ge=1)):
    """Получить страницы раздела «Описание и правила»"""
    uc = get_admission_use_case()
    dto = uc.get_rules(page)
    
    if dto is None:
        return {"error": "Страница не найдена"}
    
    return {
        "title": dto.title,
        "content": dto.content,
        "files": dto.files,
        "page": dto.page,
        "total_pages": dto.total_pages
    }


@router.get("/admission/specialties")
async def get_admission_specialties_table(page: int = Query(1, ge=1)):
    """Получить таблицу специальностей ПК (пагинированную)"""
    result = _admission_repo.get_specialties_table(page, PAGE_SIZE)
    
    return {
        "items": [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "profiles": [
                    {
                        "level": p.education_level,
                        "budget": p.budget_places,
                        "paid": p.paid_places
                    }
                    for p in s.profiles
                ]
            }
            for s in result.items
        ],
        "page": result.page,
        "total_pages": result.total_pages
    }


@router.get("/admission/dates")
async def get_admission_dates(page: int = Query(1, ge=1)):
    """Получить список важных дат"""
    result = _admission_repo.get_important_dates(page, PAGE_SIZE)
    
    return {
        "items": [
            {"id": d.id, "short_title": d.short_title}
            for d in result.items
        ],
        "page": result.page,
        "total_pages": result.total_pages
    }


@router.get("/admission/dates/{date_id}")
async def get_admission_date_detail(date_id: int, page: int = Query(1, ge=1)):
    """Получить детальную информацию о важной дате"""
    uc = get_admission_use_case()
    dto = uc.get_date_detail(date_id, page)
    
    if dto is None:
        raise HTTPException(status_code=404, detail="Дата не найдена")
    
    return {
        "title": dto.title,
        "content": dto.content,
        "files": dto.files,
        "page": dto.page,
        "total_pages": dto.total_pages
    }
