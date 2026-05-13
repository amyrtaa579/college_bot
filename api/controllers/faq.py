from fastapi import APIRouter, Query, HTTPException

from api.dependencies import get_faq_use_case

router = APIRouter(tags=["FAQ"])


@router.get("/faq/categories")
async def get_faq_categories():
    """Получить список категорий FAQ"""
    uc = get_faq_use_case()
    categories = uc.get_categories()
    
    return {
        "items": [
            {"id": c.id, "name": c.name}
            for c in categories
        ]
    }


@router.get("/faq/questions")
async def get_faq_questions(
    category_id: int | None = None,
    is_admission: bool = False,
    page: int = Query(1, ge=1)
):
    """Получить список вопросов FAQ (с фильтрами)"""
    uc = get_faq_use_case()
    result = uc.get_questions(category_id, is_admission, page)
    
    return {
        "items": [
            {"id": q.id, "question_text": q.question_text, "category_id": q.category_id}
            for q in result.items
        ],
        "page": result.page,
        "total_pages": result.total_pages
    }


@router.get("/faq/{question_id}")
async def get_faq_answer(question_id: int, page: int = Query(1, ge=1)):
    """Получить ответ на вопрос FAQ (страницы ответа)"""
    uc = get_faq_use_case()
    dto = uc.get_answer(question_id, page)
    
    if dto is None:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    
    return {
        "title": dto.title,
        "content": dto.content,
        "files": dto.files,
        "page": dto.page,
        "total_pages": dto.total_pages
    }
