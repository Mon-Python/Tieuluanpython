import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertTriangle, Info } from 'lucide-react';
import { Topic, Question, DifficultyLevel } from '../types';

interface ImportFileModalProps {
  isOpen: boolean;
  onClose: () => void;
  topics: Topic[];
  onImportSuccess: (importedCount: number, questions: Question[]) => void;
}

const SAMPLE_FILE_TEXT = `# FILE MẪU CÂU HỎI TRẮC NGHIỆM (mau_cau_hoi.txt)
# Định dạng: topic_id|Nội dung câu hỏi|Mức độ (de/kho)|Phương án A|Phương án B|Phương án C|Phương án D|Đáp án đúng (A/B/C/D)

topic_py_basic|Hàm nào dùng để chuyển đổi một chuỗi thành số nguyên trong Python?|de|int()|str()|float()|to_int()|A
topic_py_basic|Trong Python, chỉ số (index) đầu tiên của một danh sách bắt đầu từ số mấy?|de|0|1|-1|None|A
topic_py_loops|Cú pháp nào sau đây đúng để duyệt các số từ 0 đến 4 trong Python?|de|for i in range(5):|for i in range(1, 5):|for i in range(0, 4):|for i in 5:|A
topic_py_funcs|Biến được khai báo bên trong một hàm thuộc phạm vi nào?|de|Cục bộ (Local)|Toàn cục (Global)|Built-in|Hằng số|A
topic_py_funcs|Một hàm đệ quy trong Python nếu không có điều kiện dừng sẽ gây ra lỗi gì?|kho|RecursionError|MemoryOverload|TimeoutError|StackFault|A
# Dòng cố ý sai định dạng để kiểm thử bắt lỗi:
topic_py_basic|Câu hỏi này thiếu phương án|de|Chỉ có A|Chỉ có B|A
`;

export const ImportFileModal: React.FC<ImportFileModalProps> = ({
  isOpen,
  onClose,
  topics,
  onImportSuccess
}) => {
  const [fileText, setFileText] = useState<string>(SAMPLE_FILE_TEXT);
  const [defaultTopicId, setDefaultTopicId] = useState<string>(topics[0]?.id || '');
  const [report, setReport] = useState<{
    successCount: number;
    errors: string[];
    parsedQuestions: Question[];
  } | null>(null);

  if (!isOpen) return null;

  const handleParseAndImport = () => {
    const lines = fileText.split('\n');
    const validQuestions: Question[] = [];
    const errorList: string[] = [];

    const nonBlank = lines.filter(l => l.trim() && !l.trim().startsWith('#'));
    if (nonBlank.length === 0) {
      setReport({
        successCount: 0,
        errors: ['File rỗng hoặc chỉ chứa chú thích (#). Vui lòng nhập dữ liệu câu hỏi.'],
        parsedQuestions: []
      });
      return;
    }

    lines.forEach((line, index) => {
      const lineNo = index + 1;
      const clean = line.trim();
      if (!clean || clean.startsWith('#')) return;

      const parts = clean.split('|').map(p => p.trim());
      let tId = '';
      let content = '';
      let diffStr = '';
      let optA = '', optB = '', optC = '', optD = '';
      let correctRaw = '';

      if (parts.length === 8) {
        [tId, content, diffStr, optA, optB, optC, optD, correctRaw] = parts;
      } else if (parts.length === 7) {
        tId = defaultTopicId;
        [content, diffStr, optA, optB, optC, optD, correctRaw] = parts;
      } else {
        errorList.push(`Dòng ${lineNo}: Sai định dạng (${parts.length} trường). Yêu cầu 7 hoặc 8 trường cách nhau bởi '|'.`);
        return;
      }

      if (!tId) {
        errorList.push(`Dòng ${lineNo}: Mã chủ đề (topic_id) bị để trống.`);
        return;
      }
      if (!content) {
        errorList.push(`Dòng ${lineNo}: Nội dung câu hỏi bị rỗng.`);
        return;
      }

      const diffLower = diffStr.toLowerCase();
      let diff: DifficultyLevel = 'de';
      if (['de', 'dễ', 'easy'].includes(diffLower)) {
        diff = 'de';
      } else if (['kho', 'khó', 'hard'].includes(diffLower)) {
        diff = 'kho';
      } else {
        errorList.push(`Dòng ${lineNo}: Mức độ '${diffStr}' không hợp lệ (chỉ chấp nhận 'de' hoặc 'kho').`);
        return;
      }

      const opts = [optA, optB, optC, optD];
      for (let i = 0; i < opts.length; i++) {
        if (!opts[i]) {
          const l = String.fromCharCode(65 + i);
          errorList.push(`Dòng ${lineNo}: Phương án ${l} bị để trống.`);
          return;
        }
      }

      // Check duplicates
      const lowerOpts = opts.map(o => o.toLowerCase());
      if (new Set(lowerOpts).size !== 4) {
        errorList.push(`Dòng ${lineNo}: Các phương án câu hỏi bị trùng lặp nội dung.`);
        return;
      }

      // Check correct
      const corr = correctRaw.toUpperCase();
      const mapping: Record<string, number> = { A: 0, B: 1, C: 2, D: 3, '1': 0, '2': 1, '3': 2, '4': 3 };
      if (!(corr in mapping)) {
        errorList.push(`Dòng ${lineNo}: Đáp án đúng '${correctRaw}' không hợp lệ. Vui lòng nhập A, B, C hoặc D.`);
        return;
      }
      const correctIdx = mapping[corr];

      const questionObj: Question = {
        id: `q_${Math.random().toString(16).substring(2, 10)}`,
        topicId: tId,
        content,
        difficulty: diff,
        options: opts.map((text, i) => ({
          id: `opt_${Math.random().toString(16).substring(2, 10)}`,
          content: text,
          isCorrect: i === correctIdx
        })),
        createdAt: new Date().toISOString()
      };

      validQuestions.push(questionObj);
    });

    setReport({
      successCount: validQuestions.length,
      errors: errorList,
      parsedQuestions: validQuestions
    });

    if (validQuestions.length > 0) {
      onImportSuccess(validQuestions.length, validQuestions);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = evt => {
        setFileText(String(evt.target?.result || ''));
        setReport(null);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">
                Nhập câu hỏi từ file văn bản (.txt)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Đọc file mẫu `mau_cau_hoi.txt`, kiểm tra cú pháp từng dòng, bỏ qua dòng lỗi và lưu câu hợp lệ
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-blue-50/70 border border-blue-200 rounded-lg text-xs text-blue-800">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600 shrink-0" />
              <span>
                <strong>Cấu trúc chuẩn:</strong> topic_id | Nội dung câu hỏi | Mức độ (de/kho) | PA A | PA B | PA C | PA D | Đáp án (A/B/C/D)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <label className="cursor-pointer px-3 py-1 bg-white hover:bg-blue-100/50 text-blue-700 border border-blue-300 rounded-md font-medium transition flex items-center gap-1.5">
                <UploadCloud className="w-3.5 h-3.5" />
                Tải file .txt lên
                <input
                  type="file"
                  accept=".txt,.csv"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
              <button
                type="button"
                onClick={() => setFileText(SAMPLE_FILE_TEXT)}
                className="px-2.5 py-1 text-slate-600 hover:text-slate-800 underline"
              >
                Mẫu mặc định
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Chủ đề mặc định (dành cho dòng không có topic_id ở đầu):
            </label>
            <select
              value={defaultTopicId}
              onChange={e => setDefaultTopicId(e.target.value)}
              className="w-full md:w-80 px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {topics.map(t => (
                <option key={t.id} value={t.id}>
                  {t.name} (id: {t.id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Nội dung văn bản câu hỏi:
            </label>
            <textarea
              rows={8}
              value={fileText}
              onChange={e => setFileText(e.target.value)}
              className="w-full font-mono text-xs p-3 bg-slate-900 text-slate-100 rounded-lg border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 leading-relaxed"
            />
          </div>

          {/* Validation & Parsing Report */}
          {report && (
            <div className="space-y-2 p-3.5 rounded-lg border bg-slate-50">
              <div className="flex items-center justify-between text-sm font-semibold">
                <span className="flex items-center gap-1.5 text-emerald-700">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Đã nhập thành công: {report.successCount} câu hỏi
                </span>
                {report.errors.length > 0 && (
                  <span className="flex items-center gap-1.5 text-amber-700">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    Phát hiện {report.errors.length} dòng lỗi
                  </span>
                )}
              </div>

              {report.errors.length > 0 && (
                <div className="max-h-32 overflow-y-auto space-y-1 mt-2 text-xs text-red-700 bg-red-50 p-2.5 rounded border border-red-200">
                  {report.errors.map((err, i) => (
                    <div key={i} className="flex items-start gap-1.5">
                      <span className="font-bold">•</span>
                      <span>{err}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Footer actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
            >
              Đóng
            </button>
            <button
              type="button"
              onClick={handleParseAndImport}
              className="px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Kiểm tra & Nhập dữ liệu
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
