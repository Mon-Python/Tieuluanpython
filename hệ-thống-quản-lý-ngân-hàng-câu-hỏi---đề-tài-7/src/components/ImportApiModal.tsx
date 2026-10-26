import React, { useState } from 'react';
import { X, Globe, Download, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { Topic, Question, DifficultyLevel } from '../types';

interface ImportApiModalProps {
  isOpen: boolean;
  onClose: () => void;
  topics: Topic[];
  onImportSuccess: (importedCount: number, questions: Question[]) => void;
}

// Function to decode HTML entities like &quot;, &#039;, &amp;
function decodeHtml(html: string): string {
  const txt = document.createElement('textarea');
  txt.innerHTML = html;
  return txt.value;
}

export const ImportApiModal: React.FC<ImportApiModalProps> = ({
  isOpen,
  onClose,
  topics,
  onImportSuccess
}) => {
  const [topicId, setTopicId] = useState<string>(topics[0]?.id || '');
  const [category, setCategory] = useState<string>('18'); // 18 = Computers
  const [amount, setAmount] = useState<number>(5);
  const [difficulty, setDifficulty] = useState<string>('any');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [fetchedQuestions, setFetchedQuestions] = useState<any[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFetchFromApi = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      let url = `https://opentdb.com/api.php?amount=${amount}&type=multiple`;
      if (category && category !== 'any') {
        url += `&category=${category}`;
      }
      if (difficulty && difficulty !== 'any') {
        url += `&difficulty=${difficulty}`;
      }

      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`Máy chủ API phản hồi mã lỗi ${res.status}`);
      }
      const data = await res.json();
      if (data.response_code !== 0) {
        throw new Error(`API trả về response_code=${data.response_code}: Không tìm thấy câu hỏi phù hợp.`);
      }

      setFetchedQuestions(data.results || []);
    } catch (err: any) {
      setErrorMsg(err.message || 'Lỗi kết nối mạng khi gọi API.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveToBank = () => {
    if (!topicId) {
      setErrorMsg('Vui lòng chọn một chủ đề lưu trữ.');
      return;
    }
    if (fetchedQuestions.length === 0) {
      setErrorMsg('Chưa có câu hỏi nào được tải về từ API.');
      return;
    }

    const convertedQuestions: Question[] = fetchedQuestions.map(item => {
      const decodedQuestion = decodeHtml(item.question);
      const decodedCorrect = decodeHtml(item.correct_answer);
      const decodedIncorrect = item.incorrect_answers.map((x: string) => decodeHtml(x));

      // 4 options: 1 correct, 3 incorrect shuffled
      const allOpts = [
        { text: decodedCorrect, isCorrect: true },
        ...decodedIncorrect.map((x: string) => ({ text: x, isCorrect: false }))
      ].sort(() => Math.random() - 0.5);

      const diff: DifficultyLevel = item.difficulty === 'hard' ? 'kho' : 'de';

      return {
        id: `q_${Math.random().toString(16).substring(2, 10)}`,
        topicId,
        content: decodedQuestion,
        difficulty: diff,
        options: allOpts.map(o => ({
          id: `opt_${Math.random().toString(16).substring(2, 10)}`,
          content: o.text,
          isCorrect: o.isCorrect
        })),
        createdAt: new Date().toISOString()
      };
    });

    onImportSuccess(convertedQuestions.length, convertedQuestions);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-100 text-indigo-600 rounded-lg">
              <Globe className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-800">
                Nhập câu hỏi từ Web API (Open Trivia DB)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Chức năng Crawl/API bắt buộc: Tự động tải, giải mã HTML entities, ánh xạ 4 phương án
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

        {/* Body */}
        <div className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2.5 text-red-700 text-sm">
              <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Lỗi API:</span> {errorMsg}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
            {/* Target Topic */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Lưu vào Chủ đề:
              </label>
              <select
                value={topicId}
                onChange={e => setTopicId(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {topics.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Danh mục API:
              </label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="18">Khoa học máy tính (Computers)</option>
                <option value="19">Toán học (Mathematics)</option>
                <option value="17">Khoa học tự nhiên</option>
                <option value="9">Kiến thức tổng hợp</option>
              </select>
            </div>

            {/* Amount */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Số lượng câu:
              </label>
              <select
                value={amount}
                onChange={e => setAmount(Number(e.target.value))}
                className="w-full px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value={5}>5 câu</option>
                <option value={10}>10 câu</option>
                <option value={15}>15 câu</option>
              </select>
            </div>

            {/* Fetch Button */}
            <div className="flex items-end">
              <button
                type="button"
                onClick={handleFetchFromApi}
                disabled={isLoading}
                className="w-full py-1.5 px-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold transition flex items-center justify-center gap-1.5 shadow-xs disabled:opacity-50"
              >
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                {isLoading ? 'Đang gọi API...' : 'Tải câu hỏi'}
              </button>
            </div>
          </div>

          {/* Preview list */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase text-slate-700 tracking-wider">
                Danh sách câu hỏi tải về ({fetchedQuestions.length} câu)
              </span>
              {fetchedQuestions.length > 0 && (
                <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Đã giải mã HTML entities sạch sẽ
                </span>
              )}
            </div>

            <div className="max-h-64 overflow-y-auto space-y-2 border border-slate-200 rounded-lg p-3 bg-slate-50/50">
              {fetchedQuestions.length === 0 ? (
                <div className="text-center py-8 text-slate-400 text-sm">
                  Nhấn "Tải câu hỏi" để gửi request đến API Open Trivia DB và xem trước dữ liệu làm sạch.
                </div>
              ) : (
                fetchedQuestions.map((item, idx) => {
                  const qContent = decodeHtml(item.question);
                  const correct = decodeHtml(item.correct_answer);
                  const wrongs = item.incorrect_answers.map((x: string) => decodeHtml(x));
                  return (
                    <div key={idx} className="bg-white p-3 rounded-lg border border-slate-200 text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-800">
                          #{idx + 1}. {qContent}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-600">
                          {item.difficulty}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-1.5 pt-1 text-slate-600">
                        <span className="text-emerald-700 font-medium">✓ {correct} (Đáp án đúng)</span>
                        {wrongs.map((w: string, i: number) => (
                          <span key={i} className="text-slate-500">• {w}</span>
                        ))}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

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
              onClick={handleSaveToBank}
              disabled={fetchedQuestions.length === 0}
              className="px-5 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition flex items-center gap-2 disabled:opacity-50"
            >
              <CheckCircle2 className="w-4 h-4" />
              Lưu {fetchedQuestions.length} câu vào ngân hàng
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
