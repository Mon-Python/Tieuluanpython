import { ValidationResult } from './types';

// Regex constants from validators.py
export const REGEX_USERNAME = /^[a-zA-Z_][a-zA-Z0-9_]{2,19}$/;
export const REGEX_EMAIL = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+$/;
export const REGEX_QUESTION_ID = /^q_[0-9a-fA-F]{8}$/;
export const REGEX_DATE_ISO = /^\d{4}-\d{2}-\d{2}$/;
export const REGEX_DATE_VN = /^\d{2}\/\d{2}\/\d{4}$/;

export function validateUsername(username: string): ValidationResult {
  if (!username || !username.trim()) {
    return { isValid: false, message: 'Tên đăng nhập không được để trống. Vui lòng nhập từ 3 đến 20 ký tự.' };
  }
  const val = username.trim();
  if (val.length < 3) {
    return { isValid: false, message: `Tên đăng nhập '${val}' quá ngắn (${val.length} ký tự). Vui lòng nhập tối thiểu 3 ký tự.` };
  }
  if (val.length > 20) {
    return { isValid: false, message: `Tên đăng nhập '${val}' quá dài (${val.length} ký tự). Vui lòng nhập tối đa 20 ký tự.` };
  }
  if (!REGEX_USERNAME.test(val)) {
    if (/^\d/.test(val)) {
      return { isValid: false, message: 'Tên đăng nhập không được bắt đầu bằng chữ số. Hãy bắt đầu bằng chữ cái hoặc dấu _.' };
    }
    return { isValid: false, message: 'Tên đăng nhập chỉ được chứa chữ cái không dấu (a-z, A-Z), số (0-9) và dấu gạch dưới (_).' };
  }
  return { isValid: true, message: 'Tên đăng nhập hợp lệ (khớp Regex ^[a-zA-Z_][a-zA-Z0-9_]{2,19}$)' };
}

export function validateEmail(email: string): ValidationResult {
  if (!email || !email.trim()) {
    return { isValid: false, message: 'Email không được để trống. Vui lòng nhập email dạng: nguoidung@example.com.' };
  }
  const val = email.trim();
  if (!val.includes('@')) {
    return { isValid: false, message: `Email '${val}' thiếu ký tự '@'. Định dạng chuẩn phải có dạng: ten@domain.com.` };
  }
  const parts = val.split('@');
  if (parts.length !== 2) {
    return { isValid: false, message: 'Email chỉ được chứa đúng một ký tự \'@\'.' };
  }
  if (!parts[1] || !parts[1].includes('.')) {
    return { isValid: false, message: `Phần tên miền sau '@' (${parts[1]}) chưa hợp lệ. Cần có phần mở rộng như .com, .edu.vn.` };
  }
  if (!REGEX_EMAIL.test(val)) {
    return { isValid: false, message: `Email '${val}' không đúng định dạng. Hãy kiểm tra lại, không chứa dấu cách hoặc ký tự đặc biệt.` };
  }
  return { isValid: true, message: 'Email hợp lệ (khớp Regex RFC username@domain.ext)' };
}

export function validateQuestionId(qId: string): ValidationResult {
  if (!qId || !qId.trim()) {
    return { isValid: false, message: 'Mã câu hỏi không được để trống.' };
  }
  const val = qId.trim();
  if (!REGEX_QUESTION_ID.test(val)) {
    return { isValid: false, message: `Mã câu hỏi '${val}' không hợp lệ. Mã chuẩn có định dạng 'q_' kèm đúng 8 ký tự hex (ví dụ: q_a1b2c3d4).` };
  }
  return { isValid: true, message: 'Mã câu hỏi hợp lệ (khớp Regex ^q_[0-9a-fA-F]{8}$)' };
}

export function validateDateString(dateStr: string): ValidationResult {
  if (!dateStr || !dateStr.trim()) {
    return { isValid: false, message: 'Ngày tháng không được để trống. Vui lòng nhập theo định dạng YYYY-MM-DD hoặc DD/MM/YYYY.' };
  }
  const val = dateStr.trim();
  let day: number, month: number, year: number;

  if (REGEX_DATE_ISO.test(val)) {
    const parts = val.split('-');
    year = parseInt(parts[0], 10);
    month = parseInt(parts[1], 10);
    day = parseInt(parts[2], 10);
  } else if (REGEX_DATE_VN.test(val)) {
    const parts = val.split('/');
    day = parseInt(parts[0], 10);
    month = parseInt(parts[1], 10);
    year = parseInt(parts[2], 10);
  } else {
    return { isValid: false, message: `Định dạng ngày '${val}' không đúng. Vui lòng nhập theo dạng YYYY-MM-DD (VD: 2026-10-21) hoặc DD/MM/YYYY.` };
  }

  if (month < 1 || month > 12) {
    return { isValid: false, message: `Tháng ${month} không hợp lệ (phải từ 1 đến 12).` };
  }

  // Days in month checking
  const daysInMonth = new Date(year, month, 0).getDate();
  if (day < 1 || day > daysInMonth) {
    return { isValid: false, message: `Ngày '${val}' không tồn tại trong lịch thực tế (tháng ${month} năm ${year} chỉ có ${daysInMonth} ngày).` };
  }

  if (year < 1900 || year > 2100) {
    return { isValid: false, message: `Năm ${year} nằm ngoài phạm vi hợp lệ (1900 - 2100).` };
  }

  return { isValid: true, message: `Ngày tháng hợp lệ (${day}/${month}/${year})` };
}

export function validateNonNegativeNumber(value: string | number, fieldName = 'Giá trị'): ValidationResult {
  const num = Number(value);
  if (isNaN(num)) {
    return { isValid: false, message: `${fieldName} phải là một số hợp lệ.` };
  }
  if (num < 0) {
    return { isValid: false, message: `${fieldName} không được là số âm (nhận được: ${value}). Vui lòng nhập số >= 0.` };
  }
  return { isValid: true, message: `${fieldName} hợp lệ (${num} >= 0).` };
}

export function validateQuestionForm(content: string, options: string[], correctIndex: number): ValidationResult {
  if (!content || !content.trim()) {
    return { isValid: false, message: 'Nội dung câu hỏi không được để trống.' };
  }
  if (!options || options.length !== 4) {
    return { isValid: false, message: 'Câu hỏi bắt buộc phải có đúng 4 phương án trả lời (A, B, C, D).' };
  }
  for (let i = 0; i < options.length; i++) {
    if (!options[i] || !options[i].trim()) {
      const label = String.fromCharCode(65 + i);
      return { isValid: false, message: `Phương án ${label} không được để trống.` };
    }
  }
  const normalized = options.map(o => o.trim().toLowerCase());
  const set = new Set(normalized);
  if (set.size !== normalized.length) {
    return { isValid: false, message: 'Các phương án trả lời không được trùng lặp nội dung với nhau.' };
  }
  if (correctIndex < 0 || correctIndex >= 4) {
    return { isValid: false, message: 'Vui lòng chọn 1 phương án đúng trong 4 phương án (A, B, C, D).' };
  }
  return { isValid: true, message: 'Dữ liệu câu hỏi hợp lệ!' };
}
