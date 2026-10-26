import React from 'react';
import { User } from '../types';
import { KeyRound, Users, BookOpen } from 'lucide-react';

interface HeaderProps {
  currentUser: User;
  activeTab: string;
  onTabChange: (tab: string) => void;
  onOpenChangePassword: () => void;
  onOpenUserAccounts: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentUser,
  activeTab,
  onTabChange,
  onOpenChangePassword,
  onOpenUserAccounts,
}) => {
  const isAdmin = currentUser.role === 'admin';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          
          {/* Logo & Tên hệ thống */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg text-white">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-slate-900 leading-tight">
                Ngân Hàng Câu Hỏi
              </h1>
              <p className="text-xs text-slate-500">Phân hệ Quản lý & Thi Trắc Nghiệm</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 bg-slate-100 p-1 rounded-xl">
            {isAdmin && (
              <>
                <button
                  onClick={() => onTabChange('questions')}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    activeTab === 'questions'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Ngân hàng câu hỏi
                </button>
                <button
                  onClick={() => onTabChange('subjects')}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    activeTab === 'subjects'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Môn học & Chủ đề
                </button>
              </>
            )}
            <button
              onClick={() => onTabChange('exam')}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                activeTab === 'exam'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {isAdmin ? 'Tạo & Quản lý đề thi' : 'Làm bài thi'}
            </button>
          </nav>

          {/* Thông tin tài khoản & Badge Vai trò Cố định */}
          <div className="flex items-center space-x-3">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-semibold text-slate-800">{currentUser.username}</p>
              <span
                className={`inline-block px-2 py-0.5 text-xs font-medium rounded-full ${
                  isAdmin
                    ? 'bg-purple-100 text-purple-700 border border-purple-200'
                    : 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                }`}
              >
                {isAdmin ? 'Quản lý (Admin)' : 'Sinh viên'}
              </span>
            </div>

            <div className="flex items-center space-x-1 border-l border-slate-200 pl-3">
              <button
                onClick={onOpenChangePassword}
                title="Đổi mật khẩu"
                className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg"
              >
                <KeyRound className="w-5 h-5" />
              </button>
              <button
                onClick={onOpenUserAccounts}
                title="Chuyển tài khoản / Đăng ký"
                className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg"
              >
                <Users className="w-5 h-5" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
};