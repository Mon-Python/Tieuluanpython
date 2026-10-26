import React, { useState } from 'react';
import { Plus, Edit3, Trash2, BookOpen, Layers, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { Subject, Topic, Question, User } from '../types';

interface SubjectTopicTabProps {
  subjects: Subject[];
  topics: Topic[];
  questions: Question[];
  currentUser: User;
  onAddSubject: (subject: Omit<Subject, 'createdAt'>) => void;
  onUpdateSubject: (subject: Subject) => void;
  onDeleteSubject: (subjectId: string) => void;
  onAddTopic: (topic: Omit<Topic, 'createdAt'>) => void;
  onUpdateTopic: (topic: Topic) => void;
  onDeleteTopic: (topicId: string) => void;
}

export const SubjectTopicTab: React.FC<SubjectTopicTabProps> = ({
  subjects,
  topics,
  questions,
  currentUser,
  onAddSubject,
  onUpdateSubject,
  onDeleteSubject,
  onAddTopic,
  onUpdateTopic,
  onDeleteTopic,
}) => {
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>(subjects[0]?.id || '');
  const [subjectModal, setSubjectModal] = useState<{ isOpen: boolean; subject?: Subject | null }>({ isOpen: false });
  const [topicModal, setTopicModal] = useState<{ isOpen: boolean; topic?: Topic | null }>({ isOpen: false });
  const [constraintAlert, setConstraintAlert] = useState<{ title: string; message: string; hint: string } | null>(null);

  const canManage = currentUser.role === 'admin';

  // Subj form state
  const [subjName, setSubjName] = useState('');
  const [subjDesc, setSubjDesc] = useState('');

  // Topic form state
  const [topicName, setTopicName] = useState('');

  const selectedSubject = subjects.find(s => s.id === selectedSubjectId);
  const filteredTopics = topics.filter(t => t.subjectId === selectedSubjectId);

  // Subject actions
  const openSubjectModal = (subj?: Subject) => {
    if (subj) {
      setSubjectModal({ isOpen: true, subject: subj });
      setSubjName(subj.name);
      setSubjDesc(subj.description);
    } else {
      setSubjectModal({ isOpen: true, subject: null });
      setSubjName('');
      setSubjDesc('');
    }
  };

  const handleSaveSubject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!subjName.trim()) return;

    if (subjectModal.subject) {
      onUpdateSubject({
        ...subjectModal.subject,
        name: subjName.trim(),
        description: subjDesc.trim()
      });
    } else {
      const newSubj: Omit<Subject, 'createdAt'> = {
        id: `subj_${Math.random().toString(16).substring(2, 10)}`,
        name: subjName.trim(),
        description: subjDesc.trim()
      };
      onAddSubject(newSubj);
      setSelectedSubjectId(newSubj.id);
    }
    setSubjectModal({ isOpen: false });
  };

  const handleDeleteSubject = (subj: Subject) => {
    const childTopics = topics.filter(t => t.subjectId === subj.id);
    if (childTopics.length > 0) {
      // Catch ValueError from repository logic: cannot delete subject with child topics
      setConstraintAlert({
        title: 'Không thể xóa môn học (Ràng buộc toàn vẹn)',
        message: `Môn học '${subj.name}' vẫn còn ${childTopics.length} chủ đề con trực thuộc.`,
        hint: '💡 Hướng dẫn cách xử lý: Bạn phải xóa hoặc chuyển toàn bộ các chủ đề con trước khi được phép xóa môn học cha.'
      });
      return;
    }

    if (window.confirm(`Bạn có chắc chắn muốn xóa môn học '${subj.name}'?`)) {
      onDeleteSubject(subj.id);
      if (selectedSubjectId === subj.id) {
        const remaining = subjects.filter(s => s.id !== subj.id);
        setSelectedSubjectId(remaining[0]?.id || '');
      }
    }
  };

  // Topic actions
  const openTopicModal = (topic?: Topic) => {
    if (topic) {
      setTopicModal({ isOpen: true, topic });
      setTopicName(topic.name);
    } else {
      setTopicModal({ isOpen: true, topic: null });
      setTopicName('');
    }
  };

  const handleSaveTopic = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicName.trim() || !selectedSubjectId) return;

    if (topicModal.topic) {
      onUpdateTopic({
        ...topicModal.topic,
        name: topicName.trim()
      });
    } else {
      onAddTopic({
        id: `topic_${Math.random().toString(16).substring(2, 10)}`,
        subjectId: selectedSubjectId,
        name: topicName.trim()
      });
    }
    setTopicModal({ isOpen: false });
  };

  const handleDeleteTopic = (topic: Topic) => {
    const childQuestions = questions.filter(q => q.topicId === topic.id);
    if (childQuestions.length > 0) {
      // Catch ValueError from repository logic: cannot delete topic with questions
      setConstraintAlert({
        title: 'Không thể xóa chủ đề (Ràng buộc toàn vẹn)',
        message: `Chủ đề '${topic.name}' đang chứa ${childQuestions.length} câu hỏi trong ngân hàng đề.`,
        hint: '💡 Hướng dẫn cách xử lý: Bạn phải xóa hết hoặc chuyển các câu hỏi này sang chủ đề khác trước khi xóa chủ đề.'
      });
      return;
    }

    if (window.confirm(`Bạn có chắc chắn muốn xóa chủ đề '${topic.name}'?`)) {
      onDeleteTopic(topic.id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Constraint Alert Modal */}
      {constraintAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-red-200 max-w-md w-full p-6 animate-in fade-in zoom-in-95">
            <div className="flex items-start gap-3">
              <div className="p-2.5 bg-red-100 text-red-600 rounded-lg shrink-0">
                <AlertCircle className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-slate-900">{constraintAlert.title}</h4>
                <p className="text-sm text-slate-700 mt-1.5">{constraintAlert.message}</p>
                <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 leading-relaxed">
                  {constraintAlert.hint}
                </div>
              </div>
            </div>
            <div className="mt-5 flex justify-end">
              <button
                onClick={() => setConstraintAlert(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold rounded-lg transition"
              >
                Đã hiểu & Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Intro info banner */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-blue-600 text-white rounded-lg shadow-sm">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Quản lý Danh mục Môn học & Chủ đề (Phân hệ Thành viên B)
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Hỗ trợ 2 bảng liên kết cha - con, thực thi toàn vẹn dữ liệu (Bảo vệ không cho xóa khi còn dữ liệu con)
            </p>
          </div>
        </div>
        {!canManage && (
          <span className="text-xs px-2.5 py-1 bg-amber-100 text-amber-800 rounded-md font-medium">
            Chế độ chỉ xem (Học viên)
          </span>
        )}
      </div>

      {/* Two-Pane Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* LEFT COLUMN: SUBJECTS (5 cols) */}
        <div className="md:col-span-5 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col overflow-hidden">
          <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              <h4 className="text-sm font-bold text-slate-800">Danh mục Môn học ({subjects.length})</h4>
            </div>
            {canManage && (
              <button
                onClick={() => openSubjectModal()}
                className="px-2.5 py-1 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-1 shadow-xs transition"
              >
                <Plus className="w-3.5 h-3.5" />
                Thêm môn
              </button>
            )}
          </div>

          <div className="divide-y divide-slate-100 max-h-[460px] overflow-y-auto flex-1">
            {subjects.length === 0 ? (
              <div className="text-center py-10 text-slate-400 text-xs">Chưa có môn học nào</div>
            ) : (
              subjects.map(subj => {
                const isSelected = subj.id === selectedSubjectId;
                const subjTopicCount = topics.filter(t => t.subjectId === subj.id).length;
                return (
                  <div
                    key={subj.id}
                    onClick={() => setSelectedSubjectId(subj.id)}
                    className={`p-3.5 cursor-pointer transition flex items-center justify-between ${
                      isSelected
                        ? 'bg-blue-50/80 border-l-4 border-blue-600'
                        : 'hover:bg-slate-50 border-l-4 border-transparent'
                    }`}
                  >
                    <div className="pr-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-bold ${isSelected ? 'text-blue-900' : 'text-slate-800'}`}>
                          {subj.name}
                        </span>
                        <span className="text-[10px] font-mono bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded">
                          {subj.id}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{subj.description}</p>
                      <span className="inline-block text-[11px] font-medium text-blue-600 mt-1">
                        {subjTopicCount} chủ đề trực thuộc
                      </span>
                    </div>

                    {canManage && (
                      <div className="flex items-center gap-1 shrink-0" onClick={e => e.stopPropagation()}>
                        <button
                          onClick={() => openSubjectModal(subj)}
                          title="Sửa môn học"
                          className="p-1.5 text-slate-400 hover:text-blue-600 rounded-md hover:bg-white"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteSubject(subj)}
                          title="Xóa môn học"
                          className="p-1.5 text-slate-400 hover:text-red-600 rounded-md hover:bg-white"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: TOPICS (7 cols) */}
        <div className="md:col-span-7 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-col overflow-hidden">
          <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-600" />
                <h4 className="text-sm font-bold text-slate-800">
                  Chủ đề thuộc: <span className="text-indigo-600">{selectedSubject?.name || 'Chưa chọn'}</span>
                </h4>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Mỗi chủ đề chứa các câu hỏi tương ứng trong ngân hàng đề
              </p>
            </div>
            {canManage && selectedSubject && (
              <button
                onClick={() => openTopicModal()}
                className="px-2.5 py-1 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg flex items-center gap-1 shadow-xs transition"
              >
                <Plus className="w-3.5 h-3.5" />
                Thêm chủ đề
              </button>
            )}
          </div>

          <div className="p-4 flex-1 overflow-y-auto max-h-[460px]">
            {filteredTopics.length === 0 ? (
              <div className="text-center py-16 text-slate-400 text-sm">
                Môn học này chưa có chủ đề nào. Nhấn "+ Thêm chủ đề" để tạo chủ đề mới.
              </div>
            ) : (
              <div className="space-y-3">
                {filteredTopics.map(topic => {
                  const qCount = questions.filter(q => q.topicId === topic.id).length;
                  const easyCount = questions.filter(q => q.topicId === topic.id && q.difficulty === 'de').length;
                  const hardCount = questions.filter(q => q.topicId === topic.id && q.difficulty === 'kho').length;

                  return (
                    <div
                      key={topic.id}
                      className="p-3.5 bg-slate-50/70 border border-slate-200 rounded-xl flex items-center justify-between hover:border-slate-300 transition"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-slate-800">{topic.name}</span>
                          <span className="text-[10px] font-mono bg-white border border-slate-200 px-1.5 py-0.5 rounded text-slate-500">
                            {topic.id}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 mt-1.5 text-xs">
                          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 font-semibold rounded-full text-[11px]">
                            {qCount} câu hỏi
                          </span>
                          <span className="text-slate-500">
                            (Dễ: <strong className="text-emerald-700">{easyCount}</strong> | Khó: <strong className="text-amber-700">{hardCount}</strong>)
                          </span>
                        </div>
                      </div>

                      {canManage && (
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => openTopicModal(topic)}
                            title="Sửa tên chủ đề"
                            className="p-2 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-white border border-transparent hover:border-slate-200 transition"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteTopic(topic)}
                            title="Xóa chủ đề"
                            className="p-2 text-slate-400 hover:text-red-600 rounded-lg hover:bg-white border border-transparent hover:border-slate-200 transition"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Subject Modal */}
      {subjectModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-md w-full p-6 animate-in fade-in zoom-in-95">
            <h3 className="text-base font-bold text-slate-900 mb-4">
              {subjectModal.subject ? 'Chỉnh sửa Môn học' : 'Thêm Môn học mới'}
            </h3>
            <form onSubmit={handleSaveSubject} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Tên môn học (*)
                </label>
                <input
                  type="text"
                  required
                  value={subjName}
                  onChange={e => setSubjName(e.target.value)}
                  placeholder="Ví dụ: Lập trình Python..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Mô tả môn học
                </label>
                <input
                  type="text"
                  value={subjDesc}
                  onChange={e => setSubjDesc(e.target.value)}
                  placeholder="Mô tả tóm tắt nội dung..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSubjectModal({ isOpen: false })}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs"
                >
                  Lưu môn học
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Topic Modal */}
      {topicModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-md w-full p-6 animate-in fade-in zoom-in-95">
            <h3 className="text-base font-bold text-slate-900 mb-4">
              {topicModal.topic ? 'Sửa tên Chủ đề' : `Thêm Chủ đề cho [${selectedSubject?.name}]`}
            </h3>
            <form onSubmit={handleSaveTopic} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Tên chủ đề (*)
                </label>
                <input
                  type="text"
                  required
                  value={topicName}
                  onChange={e => setTopicName(e.target.value)}
                  placeholder="Ví dụ: Vòng lặp while, Đệ quy..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setTopicModal({ isOpen: false })}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-xs"
                >
                  Lưu chủ đề
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
