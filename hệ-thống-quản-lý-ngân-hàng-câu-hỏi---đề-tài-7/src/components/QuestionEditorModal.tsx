import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';
import { Question, Topic, DifficultyLevel, Option } from '../types';
import { validateQuestionForm } from '../validators';

interface QuestionEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (question: Omit<Question, 'createdAt'>) => void;
  editingQuestion?: Question | null;
  topics: Topic[];
  selectedTopicId?: string;
}

export const QuestionEditorModal: React.FC<QuestionEditorModalProps> = ({
  isOpen,
  onClose,
  onSave,
  editingQuestion,
  topics,
  selectedTopicId
}) => {
  const [topicId, setTopicId] = useState<string>('');
  const [difficulty, setDifficulty] = useState<DifficultyLevel>('de');
  const [content, setContent] = useState<string>('');
  const [options, setOptions] = useState<string[]>(['', '', '', '']);
  const [correctIndex, setCorrectIndex] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (editingQuestion) {
      setTopicId(editingQuestion.topicId);
      setDifficulty(editingQuestion.difficulty);
      setContent(editingQuestion.content);
      setOptions(editingQuestion.options.map(o => o.content));
      const idx = editingQuestion.options.findIndex(o => o.isCorrect);
      setCorrectIndex(idx >= 0 ? idx : 0);
    } else {
      setTopicId(selectedTopicId || (topics.length > 0 ? topics[0].id : ''));
      setDifficulty('de');
      setContent('');
      setOptions(['', '', '', '']);
      setCorrectIndex(0);
    }
    setErrorMsg(null);
  }, [editingQuestion, isOpen, selectedTopicId, topics]);

  if (!isOpen) return null;

  const handleOptionChange = (idx: number, val: string) => {
    const updated = [...options];
    updated[idx] = val;
    setOptions(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicId) {
      setErrorMsg('Vui lòng chọn một chủ đề cho câu hỏi.');
      return;
    }

    const val = validateQuestionForm(content, options, correctIndex);
    if (!val.isValid) {
      setErrorMsg(val.message);
      return;
    }

    const questionOptions: Option[] = options.map((optText, i) => ({
      id: editingQuestion?.options[i]?.id || `opt_${Math.random().toString(16).substring(2, 10)}`,
      content: optText.trim(),
      isCorrect: i === correctIndex
    }));

    onSave({
      id: editingQuestion?.id || `q_${Math.random().toString(16).substring(2, 10)}`,
      topicId,
      content: content.trim(),
      difficulty,
      options: questionOptions
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl border border-slate-200 w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
          <div>
            <h3 className="text-lg font-bold text-slate-800">
              {editingQuestion ? `Chỉnh sửa câu hỏi [${editingQuestion.id}]` : 'Thêm câu hỏi mới vào ngân hàng'}
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Custom QuestionEditor widget theo chuẩn đề tài (4 phương án, 1 đáp án đúng)
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2.5 text-red-700 text-sm">
              <AlertTriangle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Lỗi dữ liệu:</span> {errorMsg}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Topic Select */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Chủ đề trực thuộc (*)
              </label>
              <select
                value={topicId}
                onChange={e => setTopicId(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {topics.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} (Mã: {t.id})
                  </option>
                ))}
              </select>
            </div>

            {/* Difficulty Select */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Mức độ khó (*)
              </label>
              <select
                value={difficulty}
                onChange={e => setDifficulty(e.target.value as DifficultyLevel)}
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="de">Dễ (de) - Câu hỏi nhận biết, thông hiểu</option>
                <option value="kho">Khó (kho) - Câu hỏi vận dụng, nâng cao</option>
              </select>
            </div>
          </div>

          {/* Question Content */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              Nội dung câu hỏi (*)
            </label>
            <textarea
              rows={3}
              value={content}
              onChange={e => setContent(e.target.value)}
              placeholder="Nhập nội dung câu hỏi trắc nghiệm tại đây..."
              className="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* 4 Options with single correct radio button */}
          <div className="border border-slate-200 rounded-xl p-4 bg-slate-50/70">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase text-slate-700 tracking-wider">
                4 Phương án trả lời (Single Choice)
              </span>
              <span className="text-xs text-blue-600 flex items-center gap-1 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Chọn nút tròn để đánh dấu đáp án đúng
              </span>
            </div>

            <div className="space-y-2.5">
              {['A', 'B', 'C', 'D'].map((label, idx) => (
                <div
                  key={label}
                  className={`flex items-center gap-3 p-2 rounded-lg border transition ${
                    correctIndex === idx
                      ? 'bg-blue-50/70 border-blue-300 ring-1 ring-blue-300'
                      : 'bg-white border-slate-200'
                  }`}
                >
                  <label className="flex items-center gap-2 cursor-pointer shrink-0">
                    <input
                      type="radio"
                      name="correct_option"
                      checked={correctIndex === idx}
                      onChange={() => setCorrectIndex(idx)}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm font-bold text-slate-700 w-6">
                      {label}.
                    </span>
                  </label>
                  <input
                    type="text"
                    value={options[idx]}
                    onChange={e => handleOptionChange(idx, e.target.value)}
                    placeholder={`Nội dung phương án ${label}...`}
                    className="flex-1 px-3 py-1.5 bg-white border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  {correctIndex === idx && (
                    <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full shrink-0">
                      Đáp án đúng
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-lg transition"
            >
              Hủy bỏ
            </button>
            <button
              type="submit"
              className="px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              {editingQuestion ? 'Lưu thay đổi' : 'Thêm vào ngân hàng'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
