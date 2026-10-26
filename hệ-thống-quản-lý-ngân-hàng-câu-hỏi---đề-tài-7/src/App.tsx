/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  INITIAL_SUBJECTS, INITIAL_TOPICS, INITIAL_QUESTIONS,
  INITIAL_USERS, INITIAL_EXAMS
} from './mockData';
import { Subject, Topic, Question, User, Exam } from './types';
import { Header } from './components/Header';
import { QuestionTab } from './components/QuestionTab';
import { SubjectTopicTab } from './components/SubjectTopicTab';
import { ExamTab } from './components/ExamTab';
import { ChangePasswordModal, UserAccountsModal } from './components/AuthModals';

export default function App() {
  const [subjects, setSubjects] = useState<Subject[]>(INITIAL_SUBJECTS);
  const [topics, setTopics] = useState<Topic[]>(INITIAL_TOPICS);
  const [questions, setQuestions] = useState<Question[]>(INITIAL_QUESTIONS);
  const [users, setUsers] = useState<User[]>(INITIAL_USERS);
  const [currentUser, setCurrentUser] = useState<User>(INITIAL_USERS[0]);
  const [exams] = useState<Exam[]>(INITIAL_EXAMS);

  const [activeTab, setActiveTab] = useState<string>('questions');
  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState<boolean>(false);
  const [isUserAccountsOpen, setIsUserAccountsOpen] = useState<boolean>(false);

  // Subject Handlers
  const handleAddSubject = (s: Omit<Subject, 'createdAt'>) => {
    const newSubj: Subject = {
      ...s,
      createdAt: new Date().toISOString()
    };
    setSubjects(prev => [...prev, newSubj]);
  };

  const handleUpdateSubject = (updated: Subject) => {
    setSubjects(prev => prev.map(s => s.id === updated.id ? updated : s));
  };

  const handleDeleteSubject = (subjId: string) => {
    setSubjects(prev => prev.filter(s => s.id !== subjId));
  };

  // Topic Handlers
  const handleAddTopic = (t: Omit<Topic, 'createdAt'>) => {
    const newTopic: Topic = {
      ...t,
      createdAt: new Date().toISOString()
    };
    setTopics(prev => [...prev, newTopic]);
  };

  const handleUpdateTopic = (updated: Topic) => {
    setTopics(prev => prev.map(t => t.id === updated.id ? updated : t));
  };

  const handleDeleteTopic = (topicId: string) => {
    setTopics(prev => prev.filter(t => t.id !== topicId));
  };

  // Question Handlers
  const handleAddQuestion = (q: Omit<Question, 'createdAt'>) => {
    const newQuestion: Question = {
      ...q,
      createdAt: new Date().toISOString()
    };
    setQuestions(prev => [newQuestion, ...prev]);
  };

  const handleUpdateQuestion = (updated: Question) => {
    setQuestions(prev => prev.map(q => q.id === updated.id ? updated : q));
  };

  const handleDeleteQuestion = (qId: string) => {
    setQuestions(prev => prev.filter(q => q.id !== qId));
  };

  // Auth Handlers
  const handleChangePasswordSuccess = (newHash: string, newSalt: string) => {
    const updated = { ...currentUser, passwordHash: newHash, salt: newSalt };
    setCurrentUser(updated);
    setUsers(prev => prev.map(u => u.id === updated.id ? updated : u));
  };

  const handleRegisterUser = (newUser: Omit<User, 'createdAt'>) => {
    const fullUser: User = {
      ...newUser,
      createdAt: new Date().toISOString()
    };
    setUsers(prev => [...prev, fullUser]);
    setCurrentUser(fullUser);
    // Sinh viên mới đăng ký tự động chuyển sang tab Làm bài thi
    if (fullUser.role !== 'admin') {
      setActiveTab('exam');
    }
  };

  const handleSelectUser = (selectedUser: User) => {
    setCurrentUser(selectedUser);
    // Nếu chuyển sang tài khoản Sinh viên mà đang đứng ở các tab Admin thì chuyển về tab Làm bài thi
    if (selectedUser.role !== 'admin' && (activeTab === 'questions' || activeTab === 'subjects')) {
      setActiveTab('exam');
    }
  };

  return (
    <div className="min-h-screen bg-slate-100/70 text-slate-800 flex flex-col font-sans">
      <Header
        currentUser={currentUser}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onOpenChangePassword={() => setIsChangePasswordOpen(true)}
        onOpenUserAccounts={() => setIsUserAccountsOpen(true)}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 w-full">
        {activeTab === 'questions' && currentUser.role === 'admin' && (
          <QuestionTab
            questions={questions}
            subjects={subjects}
            topics={topics}
            currentUser={currentUser}
            exams={exams}
            onAddQuestion={handleAddQuestion}
            onUpdateQuestion={handleUpdateQuestion}
            onDeleteQuestion={handleDeleteQuestion}
          />
        )}

        {activeTab === 'subjects' && currentUser.role === 'admin' && (
          <SubjectTopicTab
            subjects={subjects}
            topics={topics}
            questions={questions}
            currentUser={currentUser}
            onAddSubject={handleAddSubject}
            onUpdateSubject={handleUpdateSubject}
            onDeleteSubject={handleDeleteSubject}
            onAddTopic={handleAddTopic}
            onUpdateTopic={handleUpdateTopic}
            onDeleteTopic={handleDeleteTopic}
          />
        )}

        {activeTab === 'exam' && (
          <ExamTab
            questions={questions}
            subjects={subjects}
            topics={topics}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Đề tài 7: Hệ thống quản lý ngân hàng câu hỏi (Python, Tkinter, JSON) - Phân hệ Thành viên B
          </span>
          <span className="font-mono text-slate-400">
            Repository: https://github.com/Mon-Python/Tieuluanpython
          </span>
        </div>
      </footer>

      {/* Modals */}
      <ChangePasswordModal
        isOpen={isChangePasswordOpen}
        onClose={() => setIsChangePasswordOpen(false)}
        currentUser={currentUser}
        onChangePasswordSuccess={handleChangePasswordSuccess}
      />

      <UserAccountsModal
        isOpen={isUserAccountsOpen}
        onClose={() => setIsUserAccountsOpen(false)}
        users={users}
        currentUserId={currentUser.id}
        onSelectUser={handleSelectUser}
        onRegisterUser={handleRegisterUser}
      />
    </div>
  );
}