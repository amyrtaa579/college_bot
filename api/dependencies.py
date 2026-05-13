"""
Сборка зависимостей для API.
Единственное место, где создаются конкретные реализации.
"""
from core.use_cases.about_college import ViewAboutCollegeUseCase
from core.use_cases.specialties import ViewSpecialtiesUseCase
from core.use_cases.admission import ViewAdmissionUseCase
from core.use_cases.faq import ViewFaqUseCase

from infrastructure.repositories.in_memory import (
    InMemoryPageRepository,
    InMemorySpecialtyRepository,
    InMemoryFactRepository,
    InMemoryAdmissionRepository,
    InMemoryFaqRepository,
)

PAGE_SIZE = 3

# Синглтоны репозиториев (для MVP — в памяти)
_page_repo = InMemoryPageRepository()
_specialty_repo = InMemorySpecialtyRepository()
_fact_repo = InMemoryFactRepository()
_admission_repo = InMemoryAdmissionRepository(_specialty_repo)
_faq_repo = InMemoryFaqRepository()


def get_about_use_case() -> ViewAboutCollegeUseCase:
    return ViewAboutCollegeUseCase(_page_repo, PAGE_SIZE)


def get_specialties_use_case() -> ViewSpecialtiesUseCase:
    return ViewSpecialtiesUseCase(_specialty_repo, _fact_repo, PAGE_SIZE)


def get_admission_use_case() -> ViewAdmissionUseCase:
    return ViewAdmissionUseCase(_page_repo, _admission_repo, PAGE_SIZE)


def get_faq_use_case() -> ViewFaqUseCase:
    return ViewFaqUseCase(_faq_repo, PAGE_SIZE)