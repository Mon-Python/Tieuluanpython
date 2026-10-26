import React, { useState } from 'react';
import { User, Role } from '../types';
import { X, Lock, User as UserIcon, Mail, ShieldCheck, KeyRound, CheckCircle } from 'lucide-react';

// ==========================================
// 1. MODAL QUẢN LÝ & ĐĂNG KÝ TÀI KHOẢN
// ==========================================
interface UserAccountsModalProps {
  isOpen: boolean;
  onClose: () => void;
  users: User[];
  currentUserId: string;
  onSelectUser: (user: User) => void;
  onRegisterUser: (user: Omit<User, 'createdAt'>) => void;
}

export const UserAccountsModal: React.FC<UserAccountsModalProps> = ({
  isOpen,
  onClose,
  users,
  currentUserId,
  onSelectUser,
  onRegisterUser,
}) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  // Cố định vai trò mặc định là Sinh viên ('user')
  const [role] = useState<Role>('user');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim()) {
      setError('Tên đăng nhập không được để trống.');
      return;
    }
    if (password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không trùng khớp!');
      return;
    }
    if (users.some((u) => u.username.toLowerCase() === username.trim().toLowerCase())) {
      setError('Tên đăng nhập này đã tồn tại.');
      return;
    }

    const newUser: Omit<User, 'createdAt'> = {
      id: `user_${Date.now()}`,
      username: username.trim(),
      email: email.trim(),
      passwordHash: 'hashed_' + password,
      salt: 'salt_123',
      role: role,
    };

    onRegisterUser(newUser);
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setIsRegistering(false);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-bold text-slate-800">
            {isRegistering ? 'Đăng ký tài khoản mới' : 'Danh sách tài khoản'}
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
              {error}
            </div>
          )}

          {!isRegistering ? (
            <div>
              <p className="text-sm text-slate-500 mb-3">Chọn tài khoản để đăng nhập:</p>
              <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                {users.map((u) => (
                  <button
                    key={u.id}
                    onClick={() => {
                      onSelectUser(u);
                      onClose();
                    }}
                    className={`w-full text-left p-3 rounded-xl border flex items-center justify-between transition-all ${
                      u.id === currentUserId
                        ? 'border-blue-500 bg-blue-50/50 ring-1 ring-blue-500'
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-slate-100 rounded-lg text-slate-600">
                        <UserIcon className="w-4 h-4" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-800">{u.username}</p>
                        <p className="text-xs text-slate-500">{u.email || 'Chưa cập nhật email'}</p>
                      </div>
                    </div>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        u.role === 'admin'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}
                    >
                      {u.role === 'admin' ? 'Quản lý' : 'Sinh viên'}
                    </span>
                  </button>
                ))}
              </div>

              <button
                onClick={() => {
                  setIsRegistering(true);
                  setError('');
                }}
                className="mt-4 w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm rounded-xl transition-all"
              >
                + Tạo tài khoản mới
              </button>
            </div>
          ) : (
            <form onSubmit={handleRegister} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Tên đăng nhập *</label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="nhap_username"
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="example@school.edu.vn"
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Mật khẩu *</label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Tối thiểu 6 ký tự"
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Xác nhận mật khẩu *</label>
                <div className="relative">
                  <ShieldCheck className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Nhập lại mật khẩu"
                    className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Chức vụ / Vai trò (Cố định)</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    disabled
                    className="py-2 text-xs font-bold rounded-lg border border-emerald-500 bg-emerald-50 text-emerald-700 cursor-not-allowed flex items-center justify-center space-x-1"
                  >
                    <span>🎓 Sinh viên</span>
                  </button>
                  <button
                    type="button"
                    disabled
                    className="py-2 text-xs font-medium rounded-lg border border-slate-200 text-slate-400 bg-slate-100 opacity-60 cursor-not-allowed flex items-center justify-center space-x-1"
                    title="Chức vụ quản lý không được phép đăng ký tự do"
                  >
                    <span>👑 Quản lý (Khóa)</span>
                  </button>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Tài khoản mới được phân quyền cố định là Sinh viên.
                </p>
              </div>

              <div className="flex space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsRegistering(false);
                    setError('');
                  }}
                  className="flex-1 py-2 text-xs font-medium border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
                >
                  Quay lại
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Đăng ký
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

// ==========================================
// 2. MODAL ĐỔI MẬT KHẨU
// ==========================================
interface ChangePasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUser: User;
  onChangePasswordSuccess: (newHash: string, newSalt: string) => void;
}

export const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
  isOpen,
  onClose,
  currentUser,
  onChangePasswordSuccess,
}) => {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // 1. Kiểm tra mật khẩu hiện tại với thông tin user
    const isOldPasswordValid =
      currentUser?.passwordHash === 'hashed_' + oldPassword ||
      currentUser?.passwordHash === oldPassword ||
      (currentUser as any)?.password === oldPassword;

    if (!isOldPasswordValid) {
      setError('Mật khẩu hiện tại không chính xác.');
      return;
    }

    // 2. Kiểm tra độ dài mật khẩu mới
    if (newPassword.length < 6) {
      setError('Mật khẩu mới phải có ít nhất 6 ký tự.');
      return;
    }

    // 3. Kiểm tra mật khẩu mới trùng khớp
    if (newPassword !== confirmPassword) {
      setError('Mật khẩu mới không trùng khớp!');
      return;
    }

    // 4. Tạo hash & salt mới và gọi handler từ App.tsx
    const newHash = 'hashed_' + newPassword;
    const newSalt = currentUser?.salt || 'salt_123';

    onChangePasswordSuccess(newHash, newSalt);

    setSuccess('Đổi mật khẩu thành công!');
    setTimeout(() => {
      onClose();
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setSuccess('');
    }, 1000);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
        <div className="flex justify-between items-center px-6 py-4 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <KeyRound className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold text-slate-800">Đổi mật khẩu</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
              {error}
            </div>
          )}
          {success && (
            <div className="p-3 bg-green-50 border border-green-200 text-green-600 text-sm rounded-lg flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>{success}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Mật khẩu hiện tại *</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="password"
                required
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                placeholder="Nhập mật khẩu hiện tại"
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Mật khẩu mới *</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Tối thiểu 6 ký tự"
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Xác nhận mật khẩu mới *</label>
            <div className="relative">
              <ShieldCheck className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Nhập lại mật khẩu mới"
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="flex space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 text-xs font-medium border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Hủy
            </button>
            <button
              type="submit"
              className="flex-1 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Cập nhật
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};