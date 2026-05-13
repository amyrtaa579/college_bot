import { config } from './config';

export interface PageDTO {
  title: string;
  content: string;
  files: Array<{ uuid: string; filename: string; mime_type: string }>;
  page: number;
  total_pages: number;
}

export interface SpecialtyListItem {
  id: number;
  code: string;
  name: string;
}

export interface PaginatedResult<T> {
  items: T[];
  page: number;
  total_pages: number;
  total: number;
}

export interface FaqCategory {
  id: number;
  name: string;
}

export interface FaqQuestion {
  id: number;
  question_text: string;
  category_id: number;
}

export interface ImportantDate {
  id: number;
  short_title: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = config.apiUrl;
  }

  private async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }
    
    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  // О колледже
  async getAboutPages(page: number): Promise<PageDTO> {
    return this.get<PageDTO>('/pages/about', { page: String(page) });
  }

  // Специальности
  async getSpecialties(page: number): Promise<PaginatedResult<SpecialtyListItem>> {
    return this.get<PaginatedResult<SpecialtyListItem>>('/specialties', { page: String(page) });
  }

  async getSpecialtyDetail(specialtyId: number, page: number): Promise<any> {
    return this.get<any>(`/specialties/${specialtyId}`, { page: String(page) });
  }

  async getSpecialtyFacts(specialtyId: number, page: number): Promise<PaginatedResult<{ id: number; title: string }>> {
    return this.get<PaginatedResult<{ id: number; title: string }>>(`/specialties/${specialtyId}/facts`, { page: String(page) });
  }

  // Приёмная комиссия
  async getAdmissionRules(page: number): Promise<PageDTO> {
    return this.get<PageDTO>('/admission/rules', { page: String(page) });
  }

  async getAdmissionSpecialties(page: number): Promise<PaginatedResult<any>> {
    return this.get<PaginatedResult<any>>('/admission/specialties', { page: String(page) });
  }

  async getAdmissionDates(page: number): Promise<PaginatedResult<ImportantDate>> {
    return this.get<PaginatedResult<ImportantDate>>('/admission/dates', { page: String(page) });
  }

  async getAdmissionDateDetail(dateId: number, page: number): Promise<PageDTO> {
    return this.get<PageDTO>(`/admission/dates/${dateId}`, { page: String(page) });
  }

  // FAQ
  async getFaqCategories(): Promise<{ items: FaqCategory[] }> {
    return this.get<{ items: FaqCategory[] }>('/faq/categories');
  }

  async getFaqQuestions(categoryId: number | null, isAdmission: boolean, page: number): Promise<PaginatedResult<FaqQuestion>> {
    const params: Record<string, string> = { page: String(page), is_admission: String(isAdmission) };
    if (categoryId !== null) {
      params.category_id = String(categoryId);
    }
    return this.get<PaginatedResult<FaqQuestion>>('/faq/questions', params);
  }

  async getFaqAnswer(questionId: number, page: number): Promise<PageDTO> {
    return this.get<PageDTO>(`/faq/${questionId}`, { page: String(page) });
  }
}

export const apiClient = new ApiClient();
