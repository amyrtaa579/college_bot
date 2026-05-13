from abc import ABC, abstractmethod


class PageRepository(ABC):
    """Порт для доступа к страницам"""
    @abstractmethod
    def get_by_section(self, section: str, page: int, page_size: int) -> "PaginatedResult":
        ...


class SpecialtyRepository(ABC):
    """Порт для доступа к специальностям"""
    @abstractmethod
    def get_list(self, page: int, page_size: int) -> "PaginatedResult":
        ...
    
    @abstractmethod
    def get_by_id(self, specialty_id: int) -> "Specialty | None":
        ...
    
    @abstractmethod
    def get_description_pages(self, specialty_id: int, page: int, page_size: int) -> "PaginatedResult":
        ...


class FactRepository(ABC):
    """Порт для доступа к фактам"""
    @abstractmethod
    def get_list(self, specialty_id: int, page: int, page_size: int) -> "PaginatedResult":
        ...
    
    @abstractmethod
    def get_by_id(self, fact_id: int) -> "Fact | None":
        ...
    
    @abstractmethod
    def get_pages(self, fact_id: int, page: int, page_size: int) -> "PaginatedResult":
        ...


class AdmissionRepository(ABC):
    """Порт для доступа к данным приёмной комиссии"""
    @abstractmethod
    def get_specialties_table(self, page: int, page_size: int) -> "PaginatedResult":
        ...
    
    @abstractmethod
    def get_important_dates(self, page: int, page_size: int) -> "PaginatedResult":
        ...
    
    @abstractmethod
    def get_date_by_id(self, date_id: int) -> "ImportantDate | None":
        ...
    
    @abstractmethod
    def get_date_pages(self, date_id: int, page: int, page_size: int) -> "PaginatedResult":
        ...


class FaqRepository(ABC):
    """Порт для доступа к FAQ"""
    @abstractmethod
    def get_categories(self) -> list["FaqCategory"]:
        ...
    
    @abstractmethod
    def get_questions(self, category_id: int | None, is_admission: bool,
                      page: int, page_size: int) -> "PaginatedResult":
        ...
    
    @abstractmethod
    def get_question_by_id(self, question_id: int) -> "FaqQuestion | None":
        ...
    
    @abstractmethod
    def get_answer_pages(self, question_id: int, page: int, page_size: int) -> "PaginatedResult":
        ...