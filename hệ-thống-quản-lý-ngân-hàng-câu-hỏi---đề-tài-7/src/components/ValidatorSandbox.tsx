import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck, Terminal, Sparkles, BookOpen } from 'lucide-react';
import {
  validateUsername, validateEmail, validateQuestionId,
  validateDateString, validateNonNegativeNumber, validateQuestionForm,
  REGEX_USERNAME, REGEX_EMAIL, REGEX_QUESTION_ID, REGEX_DATE_ISO, REGEX_DATE_VN
} from '../validators';

export const ValidatorSandbox: React.FC = () => {
  // Test states
  const [usernameInput, setUsernameInput] = useState('admin_01');
  const [emailInput, setEmailInput] = useState('teacher@school.edu.vn');
  const [questionIdInput, setQuestionIdInput] = useState('q_a1b2c3d4');
  const [dateInput, setDateInput] = useState('2026-10-21');
  const [numberInput, setNumberInput] = useState('15');

  // Question test state
  const [qContent, setQContent] = useState('Đâu là thủ đô của Việt Nam?');
  const [qOptions, setQOptions] = useState(['Hà Nội', 'Đà Nẵng', 'TP. Hồ Chí Minh', 'Cần Thơ']);
  const [qCorrect, setQCorrect] = useState(0);

  // Validation results
  const uRes = validateUsername(usernameInput);
  const eRes = validateEmail(emailInput);
  const qIdRes = validateQuestionId(questionIdInput);
  const dRes = validateDateString(dateInput);
  const nRes = validateNonNegativeNumber(numberInput, 'Số lượng câu');
  const qFormRes = validateQuestionForm(qContent, qOptions, qCorrect);

  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="p-4 bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-600 text-white rounded-lg shadow-sm">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Phòng Thử Nghiệm Kiểm Tra Dữ Liệu (Validators Sandbox - Thành viên B)
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Tập trung toàn bộ Regular Expression và quy tắc nghiệp vụ theo mục 2.7 & VII.6 của quy định
            </p>
          </div>
        </div>
        <span className="text-xs font-mono px-3 py-1 bg-white border border-emerald-300 text-emerald-800 rounded-md font-semibold">
          validators.py
        </span>
      </div>

      {/* Grid of Validators */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* 1. Username Regex Validator */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-emerald-600" />
              1. Regex Username: <code className="font-mono text-emerald-700 font-normal">^[a-zA-Z_][a-zA-Z0-9_]&#123;2,19&#125;$</code>
            </span>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Thử nghiệm tên đăng nhập (3-20 ký tự, không bắt đầu bằng số):</label>
            <input
              type="text"
              value={usernameInput}
              onChange={e => setUsernameInput(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
            <button onClick={() => setUsernameInput('teacher_linh')} className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700">Mẫu đúng</button>
            <button onClick={() => setUsernameInput('ab')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Quá ngắn</button>
            <button onClick={() => setUsernameInput('1user')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Bắt đầu bằng số</button>
            <button onClick={() => setUsernameInput('user@name')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Ký tự đặc biệt</button>
          </div>
          <div className={`p-2.5 rounded-lg border text-xs flex items-start gap-2 ${uRes.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
            {uRes.isValid ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" /> : <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />}
            <span>{uRes.message}</span>
          </div>
        </div>

        {/* 2. Email Regex Validator */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-blue-600" />
              2. Regex Email RFC Standard
            </span>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Thử nghiệm địa chỉ email (username@domain.ext):</label>
            <input
              type="text"
              value={emailInput}
              onChange={e => setEmailInput(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
            <button onClick={() => setEmailInput('admin@school.edu.vn')} className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700">Mẫu đúng</button>
            <button onClick={() => setEmailInput('userdomain.com')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Thiếu @</button>
            <button onClick={() => setEmailInput('user@localhost')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Thiếu extension</button>
            <button onClick={() => setEmailInput('user name@test.com')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Chứa khoảng trắng</button>
          </div>
          <div className={`p-2.5 rounded-lg border text-xs flex items-start gap-2 ${eRes.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
            {eRes.isValid ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" /> : <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />}
            <span>{eRes.message}</span>
          </div>
        </div>

        {/* 3. Question ID Regex Validator */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-indigo-600" />
              3. Regex Mã câu hỏi: <code className="font-mono text-indigo-700 font-normal">^q_[0-9a-fA-F]&#123;8&#125;$</code>
            </span>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Mã câu hỏi tự sinh theo đề tài (q_ + 8 ký tự hex):</label>
            <input
              type="text"
              value={questionIdInput}
              onChange={e => setQuestionIdInput(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
            <button onClick={() => setQuestionIdInput('q_a1b2c3d4')} className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700">Mẫu đúng</button>
            <button onClick={() => setQuestionIdInput('question_12345678')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Sai prefix</button>
            <button onClick={() => setQuestionIdInput('q_1234567')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Chỉ 7 ký tự</button>
            <button onClick={() => setQuestionIdInput('q_1234567g')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Ký tự 'g' không phải hex</button>
          </div>
          <div className={`p-2.5 rounded-lg border text-xs flex items-start gap-2 ${qIdRes.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
            {qIdRes.isValid ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" /> : <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />}
            <span>{qIdRes.message}</span>
          </div>
        </div>

        {/* 4. Date & Calendar Validator */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-amber-600" />
              4. Ngày tháng (ISO & VN + Lịch thực tế)
            </span>
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">Nhập YYYY-MM-DD hoặc DD/MM/YYYY (kiểm tra năm nhuận & ngày thực):</label>
            <input
              type="text"
              value={dateInput}
              onChange={e => setDateInput(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-amber-500 focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
            <button onClick={() => setDateInput('2026-10-21')} className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700">ISO hợp lệ</button>
            <button onClick={() => setDateInput('21/10/2026')} className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 rounded text-slate-700">VN hợp lệ</button>
            <button onClick={() => setDateInput('2026-02-31')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">31/02 (không tồn tại)</button>
            <button onClick={() => setDateInput('21-10-2026')} className="px-2 py-0.5 bg-red-50 hover:bg-red-100 text-red-700 rounded">Sai dấu phân cách</button>
          </div>
          <div className={`p-2.5 rounded-lg border text-xs flex items-start gap-2 ${dRes.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
            {dRes.isValid ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" /> : <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />}
            <span>{dRes.message}</span>
          </div>
        </div>
      </div>

      {/* 5. Non-Negative Number & Question Structure Validator */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-purple-600" />
            5. Kiểm tra Cấu trúc Câu hỏi & Phương án (Question.is_valid())
          </span>
          <span className="text-xs text-slate-500">
            Yêu cầu: Đúng 4 phương án, không rỗng, không trùng nhau, đúng 1 đáp án đúng
          </span>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Nội dung câu hỏi:</label>
            <input
              type="text"
              value={qContent}
              onChange={e => setQContent(e.target.value)}
              className="w-full px-3 py-1.5 border border-slate-300 rounded-lg text-xs"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {qOptions.map((opt, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  type="radio"
                  name="sandbox_correct"
                  checked={qCorrect === i}
                  onChange={() => setQCorrect(i)}
                  className="w-4 h-4 text-purple-600"
                />
                <span className="text-xs font-bold text-slate-600 w-5">{String.fromCharCode(65 + i)}:</span>
                <input
                  type="text"
                  value={opt}
                  onChange={e => {
                    const next = [...qOptions];
                    next[i] = e.target.value;
                    setQOptions(next);
                  }}
                  className="flex-1 px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs"
                />
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-2 pt-1 text-[11px]">
            <button
              onClick={() => {
                setQContent('1 + 1 bằng mấy?');
                setQOptions(['2', '3', '4', '5']);
                setQCorrect(0);
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-slate-700"
            >
              Cấu hình chuẩn
            </button>
            <button
              onClick={() => {
                setQContent('');
              }}
              className="px-2.5 py-1 bg-red-50 hover:bg-red-100 text-red-700 rounded"
            >
              Câu hỏi rỗng
            </button>
            <button
              onClick={() => {
                setQOptions(['Giống nhau', 'giống nhau', 'Khác C', 'Khác D']);
              }}
              className="px-2.5 py-1 bg-red-50 hover:bg-red-100 text-red-700 rounded"
            >
              Phương án trùng lặp
            </button>
            <button
              onClick={() => {
                setQOptions(['Hà Nội', '', 'Huế', 'Đà Nẵng']);
              }}
              className="px-2.5 py-1 bg-red-50 hover:bg-red-100 text-red-700 rounded"
            >
              Phương án rỗng
            </button>
          </div>

          <div className={`p-3 rounded-lg border text-xs flex items-start gap-2 ${qFormRes.isValid ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-red-50 border-red-200 text-red-800'}`}>
            {qFormRes.isValid ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" /> : <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />}
            <div>
              <span className="font-semibold">{qFormRes.isValid ? 'Hợp lệ: ' : 'Không hợp lệ: '}</span>
              {qFormRes.message}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
