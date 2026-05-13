from dataclasses import dataclass, field
from typing import Optional


@dataclass
class File:
    """Файл (изображение или документ)"""
    uuid: str
    filename: str
    minio_path: str
    mime_type: str


@dataclass
class Page:
    """Универсальная страница контента"""
    id: int
    title: str
    content: str
    order: int
    files: list[File] = field(default_factory=list)


@dataclass
class SpecialtyProfile:
    """Профиль специальности (9 или 11 классы)"""
    education_level: str  # "9" или "11"
    budget_places: int
    paid_places: int


@dataclass
class Specialty:
    """Специальность"""
    id: int
    code: str
    name: str
    profiles: list[SpecialtyProfile] = field(default_factory=list)
    description_pages: list[Page] = field(default_factory=list)
    facts: list["Fact"] = field(default_factory=list)


@dataclass
class Fact:
    """Интересный факт о специальности"""
    id: int
    specialty_id: int
    title: str
    pages: list[Page] = field(default_factory=list)


@dataclass
class ImportantDate:
    """Важная дата приёмной комиссии"""
    id: int
    short_title: str
    order: int
    detail_pages: list[Page] = field(default_factory=list)


@dataclass
class FaqCategory:
    """Категория FAQ"""
    id: int
    name: str


@dataclass
class FaqQuestion:
    """Вопрос FAQ"""
    id: int
    category_id: int
    question_text: str
    order: int
    is_admission: bool  # Относится к Приёмной комиссии?
    answer_pages: list[Page] = field(default_factory=list)


# Данные для пагинации
@dataclass
class PaginatedResult:
    items: list
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size