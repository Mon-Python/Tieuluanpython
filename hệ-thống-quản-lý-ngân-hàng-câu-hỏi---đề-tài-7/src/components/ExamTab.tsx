import React, { useState } from 'react';
import { Award, RefreshCw, FileCheck } from 'lucide-react';
import { Question, Subject, Topic } from '../types';

interface ExamTabProps {
  questions: Question[];
  subjects: Subject[];
  topics: Topic[];
}

export const ExamTab: React.FC<ExamTabProps> = ({ questions, subjects, topics }) => {
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>(subjects[0]?.id || '');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('de');
  const [examStarted, setExamStarted] = useState<boolean>(false);
  const [examQuestions, setExamQuestions] = useState<Question[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [score, setScore] = useState<number>(0);

  const startExam = () => {
    const subjectTopics = topics.filter(t => t.subjectId === selectedSubjectId).map(t => t.id);

    const pool = questions.filter(q => {
      const isCorrectSubject = subjectTopics.includes(q.topicId);
      const isCorrectDifficulty = selectedDifficulty === 'all' || q.difficulty === selectedDifficulty;
      return isCorrectSubject && isCorrectDifficulty;
    });

    if (pool.length === 0) {
      alert('Chưa có câu hỏi nào thuộc môn học và độ khó này trong ngân hàng đề.');
      return;
    }

    const picked = [...pool].sort(() => Math.random() - 0.5).slice(0, 5);
    setExamQuestions(picked);
    setSelectedAnswers({});
    setSubmitted(false);
    setScore(0);
    setExamStarted(true);
  };

  const handleSelectAnswer = (qId: string, optId: string) => {
    if (submitted) return;
    setSelectedAnswers(prev => ({
      ...prev,
      [qId]: optId
    }));
  };

  // Hàm chuyển trạng thái về màn hình chọn môn & độ khó
  const handleResetToSelection = () => {
    setExamStarted(false);
    setSubmitted(false);
    setSelectedAnswers({});
    setExamQuestions([]);
  };

  const handleSubmitExam = () => {
    const answeredCount = Object.keys(selectedAnswers).length;
    if (answeredCount < examQuestions.length) {
      if (!window.confirm(`Bạn mới trả lời ${answeredCount}/${examQuestions.length} câu hỏi. Bạn có chắc chắn muốn nộp bài ngay không?`)) {
        return;
      }
    }

    let correctCount = 0;
    examQuestions.forEach(q => {
      const chosenOptId = selectedAnswers[q.id];
      const correctOpt = q.options.find(o => o.isCorrect);
      if (chosenOptId && correctOpt && chosenOptId === correctOpt.id) {
        correctCount++;
      }
    });

    const calculatedScore = (correctCount / examQuestions.length) * 10;
    setScore(Number(calculatedScore.toFixed(1)));
    setSubmitted(true);
  };

  return (
    <div className="space-y-6">
      {/* Intro */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-600 text-white rounded-lg shadow-sm">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Mô Phỏng Làm Bài Kiểm Tra (Trực quan hóa đề thi từ ngân hàng câu hỏi)
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Kiểm tra tính toàn vẹn câu hỏi, phân loại độ khó và thuật toán chấm điểm tự động
            </p>
          </div>
        </div>
      </div>

      {!examStarted ? (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center max-w-lg mx-auto shadow-xs space-y-4">
          <FileCheck className="w-12 h-12 text-purple-600 mx-auto" />
          <h4 className="text-base font-bold text-slate-800">Bắt đầu bài thi trắc nghiệm</h4>
          <p className="text-xs text-slate-500 leading-relaxed">
            Hệ thống sẽ tự động trích xuất danh sách câu hỏi theo đúng môn học và độ khó đề thi được chọn.
          </p>

          <div className="text-left space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Chọn Môn thi:
              </label>
              <select
                value={selectedSubjectId}
                onChange={e => setSelectedSubjectId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-purple-500"
              >
                {subjects.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                Chọn Độ khó đề thi:
              </label>
              <select
                value={selectedDifficulty}
                onChange={e => setSelectedDifficulty(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-purple-500"
              >
                <option value="de">🟢 Đề Dễ (Chỉ lấy câu hỏi dễ)</option>
                <option value="kho">🔴 Đề Khó (Chỉ lấy câu hỏi khó)</option>
                <option value="all">🟡 Tất cả độ khó (Ngẫu nhiên)</option>
              </select>
            </div>
          </div>

          <button
            onClick={startExam}
            className="w-full py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold text-xs shadow-md transition"
          >
            Bắt đầu làm bài thi
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Header test bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 flex items-center justify-between shadow-xs">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-800">
                  Bài thi: {subjects.find(s => s.id === selectedSubjectId)?.name}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-purple-100 text-purple-700">
                  Mức độ: {selectedDifficulty === 'kho' ? 'Khó' : selectedDifficulty === 'de' ? 'Dễ' : 'Hỗn hợp'}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Đã hoàn thành: {Object.keys(selectedAnswers).length} / {examQuestions.length} câu
              </p>
            </div>

            <div className="flex items-center gap-2">
              {/* ĐÃ SỬA: Thay onClick={startExam} bằng handleResetToSelection */}
              <button
                onClick={handleResetToSelection}
                className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium flex items-center gap-1 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Làm đề khác
              </button>
              {!submitted && (
                <button
                  onClick={handleSubmitExam}
                  className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-xs transition"
                >
                  Nộp bài thi
                </button>
              )}
            </div>
          </div>

          {/* Results banner */}
          {submitted && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between animate-in fade-in">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-emerald-600 text-white rounded-xl font-black text-lg">
                  {score}/10
                </div>
                <div>
                  <h4 className="text-sm font-bold text-emerald-900">
                    Kết quả bài thi: {score >= 5 ? 'ĐẠT YÊU CẦU' : 'CHƯA ĐẠT'}
                  </h4>
                  <p className="text-xs text-emerald-700 mt-0.5">
                    Bạn trả lời đúng{' '}
                    {
                      examQuestions.filter(
                        q => selectedAnswers[q.id] === q.options.find(o => o.isCorrect)?.id
                      ).length
                    }{' '}
                    trên {examQuestions.length} câu hỏi.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Questions list */}
          <div className="space-y-4">
            {examQuestions.map((q, idx) => {
              const selectedOptId = selectedAnswers[q.id];

              return (
                <div key={q.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <span className="text-xs font-bold text-slate-800">
                      Câu {idx + 1}: {q.content}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase shrink-0 ${
                        q.difficulty === 'kho'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {q.difficulty === 'kho' ? 'Khó' : 'Dễ'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                    {q.options.map((opt, i) => {
                      const isSelected = selectedOptId === opt.id;
                      let optClass = 'bg-white border-slate-200 hover:border-slate-300';

                      if (isSelected) {
                        optClass = 'bg-purple-50/80 border-purple-400 ring-1 ring-purple-400';
                      }

                      if (submitted) {
                        if (opt.isCorrect) {
                          optClass = 'bg-emerald-50 border-emerald-400 text-emerald-900 font-bold';
                        } else if (isSelected && !opt.isCorrect) {
                          optClass = 'bg-red-50 border-red-300 text-red-800';
                        }
                      }

                      return (
                        <div
                          key={opt.id}
                          onClick={() => handleSelectAnswer(q.id, opt.id)}
                          className={`p-3 rounded-lg border text-xs cursor-pointer flex items-center justify-between transition ${optClass}`}
                        >
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-600">
                              {String.fromCharCode(65 + i)}.
                            </span>
                            <span>{opt.content}</span>
                          </div>
                          {submitted && opt.isCorrect && (
                            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded">
                              Đúng
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};