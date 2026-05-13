from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.use_cases.about_college import ViewAboutCollegeUseCase
from core.use_cases.specialties import ViewSpecialtiesUseCase
from core.use_cases.admission import ViewAdmissionUseCase
from core.use_cases.faq import ViewFaqUseCase
from core.entities.models import PaginatedResult


@dataclass
class BotResponse:
    text: str
    keyboard: list[list[str]]  # [[btn1, btn2], [btn3]]


# Настройки пагинации
ITEMS_PER_PAGE = 3
BUTTONS_PER_ROW = 3


def make_pagination_row(page: int, total_pages: int) -> list[str]:
    """Создаёт ряд кнопок пагинации: [<<] [<] [Стр. X/Y] [>] [>>]"""
    if total_pages <= 1:
        return []
    return ["<<", "<", f"Стр. {page}/{total_pages}", ">", ">>"]


def make_digit_buttons(items: list, page: int, total_pages: int) -> list[list[str]]:
    """Создаёт кнопки-цифры для выбора элемента из списка"""
    start_num = (page - 1) * ITEMS_PER_PAGE + 1
    buttons = []
    row = []
    for i, item in enumerate(items, start=start_num):
        row.append(str(i))
        if len(row) == BUTTONS_PER_ROW:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return buttons


class BotState(ABC):
    @abstractmethod
    def handle(self, ctx: "SessionContext", message: str) -> BotResponse:
        ...


class MainMenuState(BotState):
    def handle(self, ctx, message):
        return BotResponse(
            text="Добро пожаловать в чат-бот Колледжа! Выберите раздел:",
            keyboard=[
                ["📖 О колледже"],
                ["🎓 Специальности"],
                ["📋 Приёмная комиссия"],
                ["❓ Часто задаваемые вопросы"],
            ]
        )


class AboutCollegeState(BotState):
    def __init__(self, use_case: ViewAboutCollegeUseCase):
        self._uc = use_case
    
    def handle(self, ctx, message):
        page = ctx.context.get("page", 1)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message == ">":
            page += 1
        elif message == "<":
            page -= 1
        elif message == ">>":
            page = ctx.context.get("total_pages", 1)
        elif message == "<<":
            page = 1
        
        dto = self._uc.execute(page)
        if dto is None:
            return BotResponse("Информация не найдена.", [["🏠 Главное меню"]])
        
        ctx.context["page"] = dto.page
        ctx.context["total_pages"] = dto.total_pages
        
        text = f"<b>{dto.title}</b>\n{dto.content}"
        keyboard = []
        pagination = make_pagination_row(dto.page, dto.total_pages)
        if pagination:
            keyboard.append(pagination)
        keyboard.append(["🏠 Главное меню"])
        
        return BotResponse(text, keyboard)


class SpecialtiesListState(BotState):
    def __init__(self, use_case: ViewSpecialtiesUseCase):
        self._uc = use_case
    
    def handle(self, ctx, message):
        page = ctx.context.get("page", 1)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message.isdigit():
            num = int(message)
            start_idx = (page - 1) * ITEMS_PER_PAGE
            result = self._uc.get_list(page)
            item_idx = num - start_idx - 1
            if 0 <= item_idx < len(result.items):
                spec = result.items[item_idx]
                ctx.push_state("specialty_details", {"specialty_id": spec.id, "page": 1})
                return SpecialtyDetailsState(self._uc).handle(ctx, "")
        
        if message == ">":
            page += 1
        elif message == "<":
            page -= 1
        elif message == ">>":
            page = ctx.context.get("total_pages", 1)
        elif message == "<<":
            page = 1
        
        result = self._uc.get_list(page)
        ctx.context["page"] = result.page
        ctx.context["total_pages"] = result.total_pages
        
        lines = ["Выберите специальность:\n"]
        start_num = (result.page - 1) * ITEMS_PER_PAGE + 1
        for i, spec in enumerate(result.items, start=start_num):
            lines.append(f"{i}. {spec.code} {spec.name}")
        
        keyboard = make_digit_buttons(result.items, result.page, result.total_pages)
        pagination = make_pagination_row(result.page, result.total_pages)
        if pagination:
            keyboard.append(pagination)
        keyboard.append(["🏠 Главное меню"])
        
        return BotResponse("\n".join(lines), keyboard)


class SpecialtyDetailsState(BotState):
    def __init__(self, use_case: ViewSpecialtiesUseCase):
        self._uc = use_case
    
    def handle(self, ctx, message):
        spec_id = ctx.context.get("specialty_id", 0)
        page = ctx.context.get("page", 1)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message == "🔙 Назад":
            ctx.pop_state()
            return None  # Будет обработано как повторный вызов
        
        if message == "💡 Интересные факты":
            ctx.push_state("facts_list", {"specialty_id": spec_id, "page": 1})
            return None
        
        if message == ">":
            page += 1
        elif message == "<":
            page -= 1
        elif message == ">>":
            page = ctx.context.get("total_pages", 1)
        elif message == "<<":
            page = 1
        
        dto = self._uc.get_detail(spec_id, page)
        if dto is None:
            return BotResponse("Специальность не найдена.", [["🔙 Назад", "🏠 Главное меню"]])
        
        ctx.context["page"] = dto.page.page
        ctx.context["total_pages"] = dto.page.total_pages
        
        # Показываем профили на первой странице
        text = f"<b>{dto.code} {dto.name}</b>\n\n"
        if page == 1:
            for prof in dto.profiles:
                text += f"{prof['level']} кл.: бюджет {prof['budget']}, платно {prof['paid']}\n"
            text += f"\n{dto.page.title}\n{dto.page.content}"
        else:
            text = f"<b>{dto.page.title}</b>\n{dto.page.content}"
        
        keyboard = []
        pagination = make_pagination_row(dto.page.page, dto.page.total_pages)
        if pagination:
            keyboard.append(pagination)
        if dto.has_facts:
            keyboard.append(["💡 Интересные факты"])
        keyboard.append(["🔙 Назад", "🏠 Главное меню"])
        
        return BotResponse(text, keyboard)


class FactsListState(BotState):
    def __init__(self, fact_repo, page_size: int):
        self._fact_repo = fact_repo
        self._page_size = page_size
    
    def handle(self, ctx, message):
        spec_id = ctx.context.get("specialty_id", 0)
        page = ctx.context.get("page", 1)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message == "🔙 Назад":
            ctx.pop_state()
            return None
        
        result = self._fact_repo.get_list(spec_id, page, self._page_size)
        ctx.context["page"] = result.page
        ctx.context["total_pages"] = result.total_pages
        
        lines = ["Интересные факты:\n"]
        start_num = (result.page - 1) * self._page_size + 1
        for i, fact in enumerate(result.items, start=start_num):
            lines.append(f"{i}. {fact.title}")
        
        keyboard = make_digit_buttons(result.items, result.page, result.total_pages)
        pagination = make_pagination_row(result.page, result.total_pages)
        if pagination:
            keyboard.append(pagination)
        keyboard.append(["🔙 Назад", "🏠 Главное меню"])
        
        return BotResponse("\n".join(lines), keyboard)


class AdmissionMenuState(BotState):
    def handle(self, ctx, message):
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        return BotResponse(
            "Раздел Приёмной комиссии. Выберите подраздел:",
            [
                ["📝 Описание и правила"],
                ["📊 Специальности"],
                ["📅 Важные даты"],
                ["❓ Вопросы"],
                ["🏠 Главное меню"],
            ]
        )


class AdmissionQuestionsState(BotState):
    """Вопросы ПК — это FAQ с фильтром is_admission=True"""
    def __init__(self, faq_uc: ViewFaqUseCase):
        self._faq_uc = faq_uc
    
    def handle(self, ctx, message):
        page = ctx.context.get("page", 1)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message == "🔙 Назад":
            ctx.pop_state()
            return None
        
        result = self._faq_uc.get_questions(category_id=None, is_admission=True, page=page)
        ctx.context["page"] = result.page
        ctx.context["total_pages"] = result.total_pages
        
        lines = ["Вопросы приёмной комиссии:\n"]
        start_num = (result.page - 1) * ITEMS_PER_PAGE + 1
        for i, q in enumerate(result.items, start=start_num):
            lines.append(f"{i}. {q.question_text}")
        
        keyboard = make_digit_buttons(result.items, result.page, result.total_pages)
        pagination = make_pagination_row(result.page, result.total_pages)
        if pagination:
            keyboard.append(pagination)
        keyboard.append(["🔙 Назад", "🏠 Главное меню"])
        
        return BotResponse("\n".join(lines), keyboard)


class FaqCategoriesState(BotState):
    def __init__(self, uc: ViewFaqUseCase):
        self._uc = uc
    
    def handle(self, ctx, message):
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        categories = self._uc.get_categories()
        ctx.context["categories"] = {i+1: cat for i, cat in enumerate(categories)}
        
        lines = ["Выберите категорию:\n"]
        keyboard = []
        for i, cat in enumerate(categories, 1):
            lines.append(f"{i}. {cat.name}")
            keyboard.append([str(i)])
        keyboard.append(["📋 Все вопросы"])
        keyboard.append(["🏠 Главное меню"])
        
        return BotResponse("\n".join(lines), keyboard)


class FaqQuestionsState(BotState):
    def __init__(self, uc: ViewFaqUseCase):
        self._uc = uc
    
    def handle(self, ctx, message):
        page = ctx.context.get("page", 1)
        category_id = ctx.context.get("category_id")
        is_admission = ctx.context.get("is_admission", False)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message == "🔙 Назад":
            ctx.pop_state()
            return None
        
        result = self._uc.get_questions(category_id, is_admission, page)
        ctx.context["page"] = result.page
        ctx.context["total_pages"] = result.total_pages
        ctx.context["questions"] = {i+1: q for i, q in enumerate(result.items)}
        
        lines = ["Вопросы:\n"]
        start_num = (result.page - 1) * ITEMS_PER_PAGE + 1
        for i, q in enumerate(result.items, start=start_num):
            lines.append(f"{i}. {q.question_text}")
        
        keyboard = make_digit_buttons(result.items, result.page, result.total_pages)
        pagination = make_pagination_row(result.page, result.total_pages)
        if pagination:
            keyboard.append(pagination)
        keyboard.append(["🔙 Назад", "🏠 Главное меню"])
        
        return BotResponse("\n".join(lines), keyboard)


class FaqAnswerState(BotState):
    def __init__(self, uc: ViewFaqUseCase, page_size: int):
        self._uc = uc
        self._page_size = page_size
    
    def handle(self, ctx, message):
        question_id = ctx.context.get("question_id", 0)
        page = ctx.context.get("page", 1)
        
        if message == "🏠 Главное меню":
            ctx.clear_stack()
            return MainMenuState().handle(ctx, message)
        
        if message == "🔙 Назад":
            ctx.pop_state()
            return None
        
        dto = self._uc.get_answer(question_id, page)
        if dto is None:
            return BotResponse("Ответ не найден.", [["🔙 Назад", "🏠 Главное меню"]])
        
        ctx.context["page"] = dto.page
        ctx.context["total_pages"] = dto.total_pages
        
        text = f"<b>{dto.title}</b>\n{dto.content}"
        keyboard = []
        pagination = make_pagination_row(dto.page, dto.total_pages)
        if pagination:
            keyboard.append(pagination)
        keyboard.append(["🔙 Назад", "🏠 Главное меню"])
        
        return BotResponse(text, keyboard)