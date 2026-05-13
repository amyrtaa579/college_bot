import { Bot } from '@maxhub/max-bot-api';
import { config } from './config';
import { apiClient } from './api-client';
import {
  mainMenuKeyboard,
  admissionMenuKeyboard,
  paginationRow,
  backAndMenu,
} from './keyboards';
import {
  getSession,
  pushState,
  popState,
  clearStack,
} from './navigation';

const bot = new Bot(config.botToken);

// ========== ФУНКЦИИ ПОСТРОЕНИЯ ОТВЕТОВ ==========

function formatPage(page: any): string {
  return `<b>${page.title}</b>\n${page.content}`;
}

// ========== КОМАНДА /start ==========

bot.command('start', async (ctx) => {
  const userId = String(ctx.user?.user_id || 'unknown');
  clearStack(userId);

  await ctx.reply('Добро пожаловать в чат-бот Колледжа! Выберите раздел:', {
    keyboard: mainMenuKeyboard(),
  });
});

// ========== ОБРАБОТЧИК CALLBACK'ОВ ==========

bot.on('callback', async (ctx) => {
  const userId = String(ctx.user?.user_id || 'unknown');
  const data = ctx.callback?.data || '';
  const session = getSession(userId);

  // Главное меню
  if (data === 'main_menu') {
    clearStack(userId);
    await ctx.editMessage('Добро пожаловать в чат-бот Колледжа! Выберите раздел:', {
      keyboard: mainMenuKeyboard(),
    });
    return;
  }

  // Назад
  if (data === 'back') {
    popState(userId);
    // Редиректим на обработку текущего раздела
    await handleSection(ctx, userId, session.currentSection, session.context);
    return;
  }

  // Пагинация
  if (data === 'page_next' || data === 'page_prev' || data === 'page_first' || data === 'page_last') {
    const currentPage = session.context.page || 1;
    const totalPages = session.context.totalPages || 1;
    let newPage = currentPage;

    if (data === 'page_next' && currentPage < totalPages) newPage = currentPage + 1;
    if (data === 'page_prev' && currentPage > 1) newPage = currentPage - 1;
    if (data === 'page_first') newPage = 1;
    if (data === 'page_last') newPage = totalPages;

    session.context.page = newPage;
    await handleSection(ctx, userId, session.currentSection, session.context);
    return;
  }

  // Разделы
  await handleSection(ctx, userId, data, { page: 1 });
});

// ========== ОБРАБОТЧИК РАЗДЕЛОВ ==========

async function handleSection(ctx: any, userId: string, section: string, context: Record<string, any>): Promise<void> {
  const session = getSession(userId);
  session.currentSection = section;
  session.context = context;
  const page = context.page || 1;

  try {
    switch (section) {
      // ===== ГЛАВНОЕ МЕНЮ =====
      case 'main_menu':
        await ctx.editMessage('Добро пожаловать в чат-бот Колледжа! Выберите раздел:', {
          keyboard: mainMenuKeyboard(),
        });
        break;

      // ===== О КОЛЛЕДЖЕ =====
      case 'about': {
        const result = await apiClient.getAboutPages(page);
        session.context.totalPages = result.total_pages;
        const keyboard: any[] = [];
        const pagination = paginationRow(page, result.total_pages);
        if (pagination.length > 0) keyboard.push(pagination);
        keyboard.push([{ text: '🏠 Главное меню', callback_data: 'main_menu' }]);
        await ctx.editMessage(formatPage(result), { keyboard });
        break;
      }

      // ===== СПЕЦИАЛЬНОСТИ (список) =====
      case 'specialties': {
        const result = await apiClient.getSpecialties(page);
        session.context.totalPages = result.total_pages;
        const lines = ['<b>Выберите специальность:</b>\n'];
        result.items.forEach((s, i) => {
          lines.push(`${(page - 1) * config.pageSize + i + 1}. ${s.code} ${s.name}`);
        });
        const keyboard: any[] = result.items.map((s, i) => [{
          text: `${(page - 1) * config.pageSize + i + 1}`,
          callback_data: `specialty_${s.id}`,
        }]);
        const pagination = paginationRow(page, result.total_pages);
        if (pagination.length > 0) keyboard.push(pagination);
        keyboard.push([{ text: '🏠 Главное меню', callback_data: 'main_menu' }]);
        await ctx.editMessage(lines.join('\n'), { keyboard });
        break;
      }

      // ===== СПЕЦИАЛЬНОСТЬ (детали) =====
      default: {
        if (section.startsWith('specialty_')) {
          const specialtyId = parseInt(section.replace('specialty_', ''));
          const result = await apiClient.getSpecialtyDetail(specialtyId, page);
          session.context.totalPages = result.page?.total_pages || 1;
          
          let text = `<b>${result.code} ${result.name}</b>\n\n`;
          if (page === 1 && result.profiles) {
            result.profiles.forEach((p: any) => {
              text += `${p.level} кл.: бюджет ${p.budget}, платно ${p.paid}\n`;
            });
            text += '\n';
          }
          text += `${result.page?.title || ''}\n${result.page?.content || ''}`;

          const keyboard: any[] = [];
          const pagination = paginationRow(page, session.context.totalPages);
          if (pagination.length > 0) keyboard.push(pagination);
          if (result.has_facts) {
            keyboard.push([{ text: '💡 Интересные факты', callback_data: `facts_${specialtyId}` }]);
          }
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'specialties' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(text, { keyboard });
          return;
        }

        // ===== ФАКТЫ (список) =====
        if (section.startsWith('facts_')) {
          const specialtyId = parseInt(section.replace('facts_', ''));
          const result = await apiClient.getSpecialtyFacts(specialtyId, page);
          session.context.totalPages = result.total_pages;
          
          const lines = ['<b>Интересные факты:</b>\n'];
          result.items.forEach((f, i) => {
            lines.push(`${(page - 1) * config.pageSize + i + 1}. ${f.title}`);
          });
          
          const keyboard: any[] = result.items.map((f, i) => [{
            text: `${(page - 1) * config.pageSize + i + 1}`,
            callback_data: `fact_${f.id}`,
          }]);
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: `specialty_${specialtyId}` },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(lines.join('\n'), { keyboard });
          return;
        }

        // ===== ПРИЁМНАЯ КОМИССИЯ (меню) =====
        if (section === 'admission') {
          await ctx.editMessage('Раздел Приёмной комиссии. Выберите подраздел:', {
            keyboard: admissionMenuKeyboard(),
          });
          return;
        }

        // ===== ПРИЁМНАЯ КОМИССИЯ: Описание и правила =====
        if (section === 'admission_rules') {
          const result = await apiClient.getAdmissionRules(page);
          session.context.totalPages = result.total_pages;
          const keyboard: any[] = [];
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'admission' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(formatPage(result), { keyboard });
          return;
        }

        // ===== ПРИЁМНАЯ КОМИССИЯ: Специальности =====
        if (section === 'admission_specialties') {
          const result = await apiClient.getAdmissionSpecialties(page);
          session.context.totalPages = result.total_pages;
          
          const lines = ['<b>Специальности (приём 2026):</b>\n'];
          result.items.forEach((s: any, i: number) => {
            const num = (page - 1) * config.pageSize + i + 1;
            lines.push(`${num}. ${s.code} | ${s.name}`);
            s.profiles?.forEach((p: any) => {
              lines.push(`   ${p.level} кл.: бюджет ${p.budget}, платно ${p.paid}`);
            });
            lines.push('');
          });
          
          const keyboard: any[] = result.items.map((s: any, i: number) => [{
            text: `${(page - 1) * config.pageSize + i + 1}`,
            callback_data: `specialty_${s.id}`,
          }]);
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'admission' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(lines.join('\n'), { keyboard });
          return;
        }

        // ===== ПРИЁМНАЯ КОМИССИЯ: Важные даты =====
        if (section === 'admission_dates') {
          const result = await apiClient.getAdmissionDates(page);
          session.context.totalPages = result.total_pages;
          
          const lines = ['<b>Важные даты:</b>\n'];
          result.items.forEach((d, i) => {
            lines.push(`${(page - 1) * config.pageSize + i + 1}. ${d.short_title}`);
          });
          
          const keyboard: any[] = result.items.map((d, i) => [{
            text: `${(page - 1) * config.pageSize + i + 1}`,
            callback_data: `admission_date_${d.id}`,
          }]);
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'admission' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(lines.join('\n'), { keyboard });
          return;
        }

        // ===== ПРИЁМНАЯ КОМИССИЯ: FAQ =====
        if (section === 'admission_faq') {
          const result = await apiClient.getFaqQuestions(null, true, page);
          session.context.totalPages = result.total_pages;
          
          const lines = ['<b>Вопросы приёмной комиссии:</b>\n'];
          result.items.forEach((q, i) => {
            lines.push(`${(page - 1) * config.pageSize + i + 1}. ${q.question_text}`);
          });
          
          const keyboard: any[] = result.items.map((q, i) => [{
            text: `${(page - 1) * config.pageSize + i + 1}`,
            callback_data: `faq_${q.id}`,
          }]);
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'admission' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(lines.join('\n'), { keyboard });
          return;
        }

        // ===== FAQ (категории) =====
        if (section === 'faq') {
          const result = await apiClient.getFaqCategories();
          
          const lines = ['<b>Выберите категорию:</b>\n'];
          const keyboard: any[] = result.items.map((c, i) => {
            lines.push(`${i + 1}. ${c.name}`);
            return [{ text: `${i + 1}`, callback_data: `faq_cat_${c.id}` }];
          });
          keyboard.push([{ text: '📋 Все вопросы', callback_data: 'faq_all' }]);
          keyboard.push([{ text: '🏠 Главное меню', callback_data: 'main_menu' }]);
          await ctx.editMessage(lines.join('\n'), { keyboard });
          return;
        }

        // ===== FAQ (вопросы категории) =====
        if (section.startsWith('faq_cat_') || section === 'faq_all') {
          const categoryId = section.startsWith('faq_cat_') 
            ? parseInt(section.replace('faq_cat_', '')) 
            : null;
          const result = await apiClient.getFaqQuestions(categoryId, false, page);
          session.context.totalPages = result.total_pages;
          
          const lines = ['<b>Вопросы:</b>\n'];
          result.items.forEach((q, i) => {
            lines.push(`${(page - 1) * config.pageSize + i + 1}. ${q.question_text}`);
          });
          
          const keyboard: any[] = result.items.map((q, i) => [{
            text: `${(page - 1) * config.pageSize + i + 1}`,
            callback_data: `faq_${q.id}`,
          }]);
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'faq' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(lines.join('\n'), { keyboard });
          return;
        }

        // ===== FAQ (ответ) =====
        if (section.startsWith('faq_')) {
          const questionId = parseInt(section.replace('faq_', ''));
          const result = await apiClient.getFaqAnswer(questionId, page);
          session.context.totalPages = result.total_pages;
          
          const keyboard: any[] = [];
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'faq' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(formatPage(result), { keyboard });
          return;
        }

        // ===== ВАЖНАЯ ДАТА (детали) =====
        if (section.startsWith('admission_date_')) {
          const dateId = parseInt(section.replace('admission_date_', ''));
          const result = await apiClient.getAdmissionDateDetail(dateId, page);
          session.context.totalPages = result.total_pages;
          
          const keyboard: any[] = [];
          const pagination = paginationRow(page, result.total_pages);
          if (pagination.length > 0) keyboard.push(pagination);
          keyboard.push([
            { text: '🔙 Назад', callback_data: 'admission_dates' },
            { text: '🏠 Главное меню', callback_data: 'main_menu' },
          ]);
          await ctx.editMessage(formatPage(result), { keyboard });
          return;
        }

        break;
      }
    }
  } catch (error) {
    console.error('Error handling section:', error);
    await ctx.editMessage('Произошла ошибка. Попробуйте позже.', {
      keyboard: [[{ text: '🏠 Главное меню', callback_data: 'main_menu' }]],
    });
  }
}

// Запуск
bot.start();
console.log('Max бот запущен!');
