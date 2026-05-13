export interface KeyboardButton {
  text: string;
  callback_data: string;
}

export function buildKeyboard(buttons: KeyboardButton[][]): KeyboardButton[][] {
  return buttons;
}

export function paginationRow(page: number, totalPages: number): KeyboardButton[] {
  if (totalPages <= 1) return [];
  return [
    { text: '<<', callback_data: 'page_first' },
    { text: '<', callback_data: 'page_prev' },
    { text: `Стр. ${page}/${totalPages}`, callback_data: 'page_info' },
    { text: '>', callback_data: 'page_next' },
    { text: '>>', callback_data: 'page_last' },
  ];
}

export function backAndMenu(backCallback?: string): KeyboardButton[][] {
  const row: KeyboardButton[] = [];
  if (backCallback) {
    row.push({ text: '🔙 Назад', callback_data: backCallback });
  }
  row.push({ text: '🏠 Главное меню', callback_data: 'main_menu' });
  return [row];
}

export function mainMenuKeyboard(): KeyboardButton[][] {
  return [
    [{ text: '📖 О колледже', callback_data: 'about' }],
    [{ text: '🎓 Специальности', callback_data: 'specialties' }],
    [{ text: '📋 Приёмная комиссия', callback_data: 'admission' }],
    [{ text: '❓ Часто задаваемые вопросы', callback_data: 'faq' }],
  ];
}

export function admissionMenuKeyboard(): KeyboardButton[][] {
  return [
    [{ text: '📝 Описание и правила', callback_data: 'admission_rules' }],
    [{ text: '📊 Специальности', callback_data: 'admission_specialties' }],
    [{ text: '📅 Важные даты', callback_data: 'admission_dates' }],
    [{ text: '❓ Вопросы', callback_data: 'admission_faq' }],
    [{ text: '🏠 Главное меню', callback_data: 'main_menu' }],
  ];
}
