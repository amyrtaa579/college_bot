from core.use_cases.about_college import PageDTO


class ViewFaqUseCase:
    """Просмотр Часто задаваемых вопросов"""
    
    def __init__(self, faq_repo, page_size: int):
        self._faq_repo = faq_repo
        self._page_size = page_size
    
    def get_categories(self) -> list["FaqCategory"]:
        return self._faq_repo.get_categories()
    
    def get_questions(self, category_id: int | None, is_admission: bool,
                      page: int = 1) -> "PaginatedResult":
        return self._faq_repo.get_questions(category_id, is_admission, 
                                            page, self._page_size)
    
    def get_answer(self, question_id: int, page: int = 1) -> PageDTO | None:
        question = self._faq_repo.get_question_by_id(question_id)
        if question is None:
            return None
        
        result = self._faq_repo.get_answer_pages(question_id, page, self._page_size)
        if not result.items:
            return None
        
        p = result.items[0]
        return PageDTO(
            title=question.question_text,
            content=p.content,
            files=[{"uuid": f.uuid, "filename": f.filename,
                    "mime_type": f.mime_type} for f in p.files],
            page=result.page, total_pages=result.total_pages
        )
