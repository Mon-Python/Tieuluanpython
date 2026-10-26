import React, { useState } from 'react';
import {
  Search, Plus, Edit, Trash2, FileText, Globe, Filter,
  CheckCircle2, AlertTriangle, AlertCircle, HelpCircle, RotateCcw
} from 'lucide-react';
import { Question, Subject, Topic, DifficultyLevel, User, Exam } from '../types';
import { QuestionEditorModal } from './QuestionEditorModal';
import { ImportFileModal } from './ImportFileModal';
import { ImportApiModal } from './ImportApiModal';

interface QuestionTabProps {
  questions: Question[];
  subjects: Subject[];
  topics: Topic[];
  currentUser: User;
  exams: Exam[];
  onAddQuestion: (q: Omit<Question, 'createdAt'>) => void;
  onUpdateQuestion: (q: Question) => void;
  onDeleteQuestion: (qId: string) => void;
}

export const QuestionTab: React.FC<QuestionTabProps> = ({
  questions,
  subjects,
  topics,
  currentUser,
  exams,
  onAddQuestion,
  onUpdateQuestion,
  onDeleteQuestion
}) => {
  // Filter states (Multi-criteria search >= 2 criteria as required by assignment)
  const [keyword, setKeyword] = useState<string>('');
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>('');
  const [selectedTopicId, setSelectedTopicId] = useState<string>('');
  const [selectedDiff, setSelectedDiff] = useState<string>('');

  // Modals
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [isFileModalOpen, setIsFileModalOpen] = useState(false);
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [deleteBlockedError, setDeleteBlockedError] = useState<{ id: string; message: string; hint: string } | null>(null);

  const canManage = currentUser.role === 'admin';

  // Topics for selected subject
  const availableTopics = selectedSubjectId
    ? topics.filter(t => t.subjectId === selectedSubjectId)
    : topics;

  // Filter logic
  const filteredQuestions = questions.filter(q => {
    // 1. Keyword search (in question content OR any option content, case-insensitive)
    if (keyword.trim()) {
      const kw = keyword.trim().toLowerCase();
      const inContent = q.content.toLowerCase().includes(kw);
      const inOptions = q.options.some(o => o.content.toLowerCase().includes(kw));
      if (!inContent && !inOptions) return false;
    }

    // 2. Subject filter
    if (selectedSubjectId) {
      const topicObj = topics.find(t => t.id === q.topicId);
      if (!topicObj || topicObj.subjectId !== selectedSubjectId) return false;
    }

    // 3. Topic filter
    if (selectedTopicId && q.topicId !== selectedTopicId) {
      return false;
    }

    // 4. Difficulty filter
    if (selectedDiff && q.difficulty !== selectedDiff) {
      return false;
    }

    return true;
  });

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleResetFilters = () => {
    setKeyword('');
    setSelectedSubjectId('');
    setSelectedTopicId('');
    setSelectedDiff('');
  };

  const handleDelete = (q: Question) => {
    // Check if question is used in any exams (repository integrity check)
    const isUsedInExam = exams.some(e => e.questionIds.includes(q.id));
    if (isUsedInExam) {
      setDeleteBlockedError({
        id: q.id,
        message: 'Không thể xóa câu hỏi vì đã nằm trong đề thi đã tạo (xóa sẽ làm hỏng cấu trúc đề và kết quả làm bài của học viên).',
        hint: '💡 Hướng dẫn xử lý: Hãy chỉnh sửa nội dung câu hỏi thay vì xóa, hoặc xóa các đề thi chứa câu hỏi này trước.'
      });
      return;
    }

    if (window.confirm(`Bạn có chắc chắn muốn xóa câu hỏi mã '${q.id}'?`)) {
      onDeleteQuestion(q.id);
      showToast(`Đã xóa câu hỏi '${q.id}' thành công.`);
    }
  };

  return (
    <div className="space-y-5">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 z-50 bg-emerald-700 text-white px-4 py-2.5 rounded-lg shadow-xl text-xs font-semibold flex items-center gap-2 animate-in slide-in-from-bottom-5">
          <CheckCircle2 className="w-4 h-4" />
          {toastMessage}
        </div>
      )}

      {/* Delete Blocked Dialog */}
      {deleteBlockedError && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-red-200 max-w-md w-full p-6 animate-in fade-in zoom-in-95">
            <div className="flex items-start gap-3">
              <div className="p-2.5 bg-red-100 text-red-600 rounded-lg shrink-0">
                <AlertCircle className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-slate-900">
                  Lỗi ràng buộc: Không thể xóa câu hỏi [{deleteBlockedError.id}]
                </h4>
                <p className="text-sm text-slate-700 mt-2">{deleteBlockedError.message}</p>
                <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 leading-relaxed">
                  {deleteBlockedError.hint}
                </div>
              </div>
            </div>
            <div className="mt-5 flex justify-end">
              <button
                onClick={() => setDeleteBlockedError(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition"
              >
                Đã hiểu
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 1. FILTER & SEARCH BOX (Multi-criteria search >= 2 criteria) */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
        <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
          <div className="flex items-center gap-2 text-slate-800 font-bold text-sm">
            <Filter className="w-4 h-4 text-blue-600" />
            <span>Tìm kiếm & Bộ lọc câu hỏi (Đa tiêu chí: Từ khóa, Môn học, Chủ đề, Mức độ)</span>
          </div>
          <button
            onClick={handleResetFilters}
            className="text-xs text-slate-500 hover:text-blue-600 flex items-center gap-1 font-medium transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Đặt lại bộ lọc
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
          {/* Keyword Search (5 cols) */}
          <div className="md:col-span-5 relative">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              placeholder="Nhập từ khóa trong nội dung câu hỏi hoặc đáp án..."
              className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Subject Filter (2.5 cols) */}
          <div className="md:col-span-3">
            <select
              value={selectedSubjectId}
              onChange={e => {
                setSelectedSubjectId(e.target.value);
                setSelectedTopicId('');
              }}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Tất cả Môn học --</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Topic Filter (2.5 cols) */}
          <div className="md:col-span-2">
            <select
              value={selectedTopicId}
              onChange={e => setSelectedTopicId(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Tất cả Chủ đề --</option>
              {availableTopics.map(t => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          {/* Difficulty Filter (2 cols) */}
          <div className="md:col-span-2">
            <select
              value={selectedDiff}
              onChange={e => setSelectedDiff(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Mức độ --</option>
              <option value="de">Dễ (de)</option>
              <option value="kho">Khó (kho)</option>
            </select>
          </div>
        </div>
      </div>

      {/* 2. ACTION BAR & STATS */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
            Tổng cộng: <strong className="text-slate-900">{questions.length}</strong> câu
          </span>
          <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1.5 rounded-lg border border-emerald-200">
            Dễ: {questions.filter(q => q.difficulty === 'de').length}
          </span>
          <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-2.5 py-1.5 rounded-lg border border-amber-200">
            Khó: {questions.filter(q => q.difficulty === 'kho').length}
          </span>
          {filteredQuestions.length !== questions.length && (
            <span className="text-xs text-blue-700 font-medium">
              (Khớp bộ lọc: {filteredQuestions.length} câu)
            </span>
          )}
        </div>

        {canManage && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setEditingQuestion(null);
                setIsEditorOpen(true);
              }}
              className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              Thêm câu hỏi
            </button>

            <button
              onClick={() => setIsFileModalOpen(true)}
              className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
            >
              <FileText className="w-3.5 h-3.5 text-blue-600" />
              Nhập file (.txt)
            </button>

            <button
              onClick={() => setIsApiModalOpen(true)}
              className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
            >
              <Globe className="w-3.5 h-3.5 text-indigo-600" />
              Nhập từ API (OpenTDB)
            </button>
          </div>
        )}
      </div>

      {/* 3. QUESTIONS TABLE / TREEVIEW */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-600">
                <th className="py-3 px-4 w-28">Mã câu</th>
                <th className="py-3 px-3 w-40">Môn học / Chủ đề</th>
                <th className="py-3 px-3 w-20 text-center">Mức độ</th>
                <th className="py-3 px-4">Nội dung câu hỏi & 4 phương án</th>
                <th className="py-3 px-3 w-48">Đáp án đúng</th>
                {canManage && <th className="py-3 px-4 w-24 text-right">Thao tác</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {filteredQuestions.length === 0 ? (
                <tr>
                  <td colSpan={canManage ? 6 : 5} className="py-12 text-center text-slate-400">
                    Không tìm thấy câu hỏi nào phù hợp với điều kiện tìm kiếm.
                  </td>
                </tr>
              ) : (
                filteredQuestions.map(q => {
                  const topicObj = topics.find(t => t.id === q.topicId);
                  const subjectObj = topicObj ? subjects.find(s => s.id === topicObj.subjectId) : null;
                  const correctOpt = q.options.find(o => o.isCorrect);

                  return (
                    <tr key={q.id} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4 font-mono font-semibold text-slate-600 whitespace-nowrap">
                        {q.id}
                      </td>
                      <td className="py-3 px-3">
                        <div className="font-semibold text-slate-800">{subjectObj?.name || '---'}</div>
                        <div className="text-[11px] text-blue-600 mt-0.5">{topicObj?.name || q.topicId}</div>
                      </td>
                      <td className="py-3 px-3 text-center">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            q.difficulty === 'kho'
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          }`}
                        >
                          {q.difficulty === 'kho' ? 'Khó' : 'Dễ'}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-medium text-slate-900 leading-snug">{q.content}</div>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100">
                          {q.options.map((opt, i) => (
                            <div
                              key={opt.id}
                              className={`truncate ${
                                opt.isCorrect ? 'font-bold text-emerald-700' : 'text-slate-600'
                              }`}
                            >
                              <span className="font-semibold">{String.fromCharCode(65 + i)}.</span>{' '}
                              {opt.content}
                            </div>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        {correctOpt ? (
                          <div className="flex items-center gap-1.5 text-emerald-700 font-semibold bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
                            <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                            <span className="truncate">{correctOpt.content}</span>
                          </div>
                        ) : (
                          <span className="text-red-500 text-xs">Chưa có</span>
                        )}
                      </td>
                      {canManage && (
                        <td className="py-3 px-4 text-right whitespace-nowrap">
                          <button
                            onClick={() => {
                              setEditingQuestion(q);
                              setIsEditorOpen(true);
                            }}
                            title="Sửa câu hỏi"
                            className="p-1.5 text-slate-400 hover:text-blue-600 rounded-md hover:bg-white transition"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(q)}
                            title="Xóa câu hỏi"
                            className="p-1.5 text-slate-400 hover:text-red-600 rounded-md hover:bg-white transition"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      )}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals */}
      <QuestionEditorModal
        isOpen={isEditorOpen}
        onClose={() => setIsEditorOpen(false)}
        editingQuestion={editingQuestion}
        topics={topics}
        selectedTopicId={selectedTopicId || topics[0]?.id}
        onSave={qData => {
          if (editingQuestion) {
            onUpdateQuestion({ ...editingQuestion, ...qData });
            showToast(`Đã cập nhật câu hỏi [${qData.id}] thành công.`);
          } else {
            onAddQuestion(qData);
            showToast(`Đã thêm câu hỏi [${qData.id}] vào ngân hàng đề.`);
          }
        }}
      />

      <ImportFileModal
        isOpen={isFileModalOpen}
        onClose={() => setIsFileModalOpen(false)}
        topics={topics}
        onImportSuccess={(cnt, newQs) => {
          newQs.forEach(q => onAddQuestion(q));
          showToast(`Đã nạp thành công ${cnt} câu hỏi từ file vào ngân hàng.`);
        }}
      />

      <ImportApiModal
        isOpen={isApiModalOpen}
        onClose={() => setIsApiModalOpen(false)}
        topics={topics}
        onImportSuccess={(cnt, newQs) => {
          newQs.forEach(q => onAddQuestion(q));
          showToast(`Đã nhập thành công ${cnt} câu hỏi từ Open Trivia DB.`);
        }}
      />
    </div>
  );
};
