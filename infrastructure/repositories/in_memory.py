from core.entities.models import *
from core.ports.repositories import *

class InMemoryPageRepository(PageRepository):
    def __init__(self):
        self._pages = {
            "about": [
                Page(id=1, title="О нашем колледже", content="Мы лучший колледж в городе! Основаны в 1990 году...",
                     order=1, files=[File(uuid="img1", filename="college.jpg", minio_path="/img1", mime_type="image/jpeg")]),
                Page(id=2, title="Наша миссия", content="Готовим профессионалов с 1990 года.",
                     order=2),
                Page(id=3, title="Наши достижения", content="100500 победителей олимпиад.",
                     order=3),
            ],
            "admission-rules": [
                Page(id=10, title="Правила приёма 2026", content="Для поступления необходимо предоставить...",
                     order=1),
                Page(id=11, title="Необходимые документы", content="1. Аттестат\n2. Паспорт\n3. Фото 3×4",
                     order=2),
            ]
        }
    
    def get_by_section(self, section: str, page: int, page_size: int) -> PaginatedResult:
        pages = self._pages.get(section, [])
        total = len(pages)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=pages[start:end], total=total, page=page, page_size=page_size)


class InMemorySpecialtyRepository(SpecialtyRepository):
    def __init__(self):
        self._specialties = [
            Specialty(id=1, code="09.02.01", name="Компьютерные системы и комплексы",
                      profiles=[
                          SpecialtyProfile("9", 25, 5),
                          SpecialtyProfile("11", 10, 2),
                      ],
                      description_pages=[
                          Page(id=100, title="О специальности", content="Изучаем железо и софт.", order=1),
                          Page(id=101, title="Чему научитесь", content="Программирование, сети, администрирование.", order=2),
                      ]),
            Specialty(id=2, code="08.01.05", name="Строительство и эксплуатация зданий",
                      profiles=[
                          SpecialtyProfile("9", 20, 10),
                          SpecialtyProfile("11", 15, 5),
                      ],
                      description_pages=[
                          Page(id=200, title="О специальности", content="Проектируем и строим.", order=1),
                      ]),
            Specialty(id=3, code="38.02.01", name="Экономика и бухгалтерский учёт",
                      profiles=[
                          SpecialtyProfile("9", 30, 15),
                          SpecialtyProfile("11", 20, 10),
                      ],
                      description_pages=[
                          Page(id=300, title="О специальности", content="Финансы и учёт.", order=1),
                      ]),
        ]
    
    def get_list(self, page: int, page_size: int) -> PaginatedResult:
        total = len(self._specialties)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=self._specialties[start:end], total=total, page=page, page_size=page_size)
    
    def get_by_id(self, specialty_id: int) -> Specialty | None:
        for s in self._specialties:
            if s.id == specialty_id:
                return s
        return None
    
    def get_description_pages(self, specialty_id: int, page: int, page_size: int) -> PaginatedResult:
        spec = self.get_by_id(specialty_id)
        if spec is None:
            return PaginatedResult([], 0, page, page_size)
        pages = spec.description_pages
        total = len(pages)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=pages[start:end], total=total, page=page, page_size=page_size)


class InMemoryFactRepository(FactRepository):
    def __init__(self):
        self._facts = {
            1: [
                Fact(id=1, specialty_id=1, title="Первый компьютер",
                     pages=[Page(id=1000, title="Первый компьютер", content="ENIAC весил 27 тонн!", order=1)]),
                Fact(id=2, specialty_id=1, title="Самая дорогая клавиатура",
                     pages=[Page(id=1001, title="Happy Hacking Keyboard", content="Стоит $300+", order=1)]),
            ],
            2: [
                Fact(id=3, specialty_id=2, title="Самое высокое здание",
                     pages=[Page(id=2000, title="Бурдж-Халифа", content="828 метров!", order=1)]),
            ]
        }
    
    def get_list(self, specialty_id: int, page: int, page_size: int) -> PaginatedResult:
        facts = self._facts.get(specialty_id, [])
        total = len(facts)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=facts[start:end], total=total, page=page, page_size=page_size)
    
    def get_by_id(self, fact_id: int) -> Fact | None:
        for facts in self._facts.values():
            for f in facts:
                if f.id == fact_id:
                    return f
        return None
    
    def get_pages(self, fact_id: int, page: int, page_size: int) -> PaginatedResult:
        fact = self.get_by_id(fact_id)
        if fact is None:
            return PaginatedResult([], 0, page, page_size)
        pages = fact.pages
        total = len(pages)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=pages[start:end], total=total, page=page, page_size=page_size)


class InMemoryAdmissionRepository(AdmissionRepository):
    def __init__(self, specialty_repo):
        self._specialty_repo = specialty_repo
        self._dates = [
            ImportantDate(id=1, short_title="Начало приёма документов", order=1,
                          detail_pages=[Page(id=5001, title="Начало приёма", content="20 июня 2026 года.", order=1)]),
            ImportantDate(id=2, short_title="Заселение в общежитие", order=2,
                          detail_pages=[Page(id=5002, title="Заселение", content="25-30 августа.", order=1)]),
        ]
    
    def get_specialties_table(self, page: int, page_size: int) -> PaginatedResult:
        return self._specialty_repo.get_list(page, page_size)
    
    def get_important_dates(self, page: int, page_size: int) -> PaginatedResult:
        total = len(self._dates)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=self._dates[start:end], total=total, page=page, page_size=page_size)
    
    def get_date_by_id(self, date_id: int) -> ImportantDate | None:
        for d in self._dates:
            if d.id == date_id:
                return d
        return None
    
    def get_date_pages(self, date_id: int, page: int, page_size: int) -> PaginatedResult:
        date = self.get_date_by_id(date_id)
        if date is None:
            return PaginatedResult([], 0, page, page_size)
        pages = date.detail_pages
        total = len(pages)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=pages[start:end], total=total, page=page, page_size=page_size)


class InMemoryFaqRepository(FaqRepository):
    def __init__(self):
        self._categories = [
            FaqCategory(id=1, name="Поступление"),
            FaqCategory(id=2, name="Обучение"),
            FaqCategory(id=3, name="Приёмная комиссия"),
        ]
        self._questions = [
            FaqQuestion(id=1, category_id=1, question_text="Какие документы нужны для поступления?",
                        order=1, is_admission=True,
                        answer_pages=[Page(id=6001, title="Документы", content="Аттестат, паспорт, фото.", order=1)]),
            FaqQuestion(id=2, category_id=1, question_text="Как подать заявление?",
                        order=2, is_admission=True,
                        answer_pages=[Page(id=6002, title="Подача заявления", content="Онлайн или лично.", order=1)]),
            FaqQuestion(id=3, category_id=2, question_text="Сколько длится учебный год?",
                        order=1, is_admission=False,
                        answer_pages=[Page(id=6003, title="Учебный год", content="Сентябрь — июнь.", order=1)]),
        ]
    
    def get_categories(self) -> list[FaqCategory]:
        return self._categories
    
    def get_questions(self, category_id: int | None, is_admission: bool,
                      page: int, page_size: int) -> PaginatedResult:
        questions = self._questions
        if is_admission:
            questions = [q for q in questions if q.is_admission]
        if category_id is not None:
            questions = [q for q in questions if q.category_id == category_id]
        total = len(questions)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=questions[start:end], total=total, page=page, page_size=page_size)
    
    def get_question_by_id(self, question_id: int) -> FaqQuestion | None:
        for q in self._questions:
            if q.id == question_id:
                return q
        return None
    
    def get_answer_pages(self, question_id: int, page: int, page_size: int) -> PaginatedResult:
        q = self.get_question_by_id(question_id)
        if q is None:
            return PaginatedResult([], 0, page, page_size)
        pages = q.answer_pages
        total = len(pages)
        start = (page - 1) * page_size
        end = start + page_size
        return PaginatedResult(items=pages[start:end], total=total, page=page, page_size=page_size)