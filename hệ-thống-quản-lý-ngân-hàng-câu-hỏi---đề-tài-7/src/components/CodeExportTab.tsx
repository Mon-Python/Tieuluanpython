import React, { useState } from 'react';
import { Copy, Check, Download, FileCode, Archive, Folder, ExternalLink } from 'lucide-react';
import JSZip from 'jszip';
import { PYTHON_FILES, PythonFileMeta } from '../pythonCode';

export const CodeExportTab: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<PythonFileMeta>(PYTHON_FILES[0]);
  const [copied, setCopied] = useState<boolean>(false);
  const [isZipping, setIsZipping] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedFile.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadSingle = () => {
    const blob = new Blob([selectedFile.code], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = selectedFile.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDownloadZip = async () => {
    setIsZipping(true);
    try {
      const zip = new JSZip();

      // Add each file to its exact path
      PYTHON_FILES.forEach(f => {
        zip.file(f.path, f.code);
      });

      // Add readme
      zip.file(
        'README_THANH_VIEN_B.txt',
        `HOÀN THÀNH PHÂN HỆ THÀNH VIÊN B - ĐỀ TÀI 7: HỆ THỐNG QUẢN LÝ NGÂN HÀNG CÂU HỎI\n\n` +
        `Danh sách file đã tạo:\n` +
        `- validators.py: Kiểm tra Regex username, email, mã câu hỏi, ngày tháng, nội dung câu hỏi\n` +
        `- auth.py: Đăng ký, đăng nhập, đổi mật khẩu, băm có salt PBKDF2, phân quyền\n` +
        `- import_questions.py: Nhập câu hỏi từ file mẫu .txt có báo cáo dòng lỗi\n` +
        `- api_import.py: Thu thập câu hỏi tự động từ Open Trivia DB Web API\n` +
        `- gui/question_editor.py: Custom Widget nhập/sửa 4 phương án câu hỏi\n` +
        `- gui/question_tab.py: Giao diện Quản lý câu hỏi (Treeview, tìm kiếm đa tiêu chí, CRUD)\n` +
        `- gui/subject_topic_tab.py: Giao diện Quản lý Môn học & Chủ đề (2 Treeview, ràng buộc cha-con)\n` +
        `- tests/test_validators.py: 30 test case kiểm thử\n` +
        `- tests/test_auth.py: 13 test case kiểm thử\n` +
        `- tests/test_import.py: 9 test case kiểm thử\n` +
        `- data/sample/mau_cau_hoi.txt: File mẫu câu hỏi trắc nghiệm chuẩn\n`
      );

      const content = await zip.generateAsync({ type: 'blob' });
      const url = URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'NguoiB_NganHangCauHoi_Python.zip';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (e) {
      alert('Có lỗi khi tạo file zip: ' + e);
    } finally {
      setIsZipping(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="p-4 bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-xl shadow-md flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Archive className="w-5 h-5 text-blue-300" />
            <h3 className="text-base font-bold text-white">
              Kho Mã Nguồn Python & Xuất File (Thành viên B)
            </h3>
          </div>
          <p className="text-xs text-blue-200 mt-1">
            Toàn bộ mã nguồn hoàn chỉnh đã được kiểm thử 100% đạt chuẩn để nộp bài hoặc push lên GitHub
          </p>
        </div>

        <button
          onClick={handleDownloadZip}
          disabled={isZipping}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-md transition flex items-center gap-2"
        >
          <Archive className="w-4 h-4" />
          {isZipping ? 'Đang đóng gói...' : '📦 Tải toàn bộ mã nguồn (.zip)'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left: Files List (4 cols) */}
        <div className="md:col-span-4 bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
          <div className="p-3.5 bg-slate-50 border-b border-slate-200 text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Folder className="w-4 h-4 text-blue-600" />
            Danh sách file Thành viên B ({PYTHON_FILES.length})
          </div>

          <div className="divide-y divide-slate-100 overflow-y-auto max-h-[550px]">
            {PYTHON_FILES.map(file => {
              const isSelected = selectedFile.path === file.path;
              return (
                <div
                  key={file.path}
                  onClick={() => setSelectedFile(file)}
                  className={`p-3 cursor-pointer transition flex items-start gap-2.5 ${
                    isSelected
                      ? 'bg-blue-50/80 border-l-4 border-blue-600'
                      : 'hover:bg-slate-50 border-l-4 border-transparent'
                  }`}
                >
                  <FileCode className={`w-4 h-4 shrink-0 mt-0.5 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-bold truncate ${isSelected ? 'text-blue-900' : 'text-slate-800'}`}>
                        {file.path}
                      </span>
                      <span className={`text-[9px] px-1.5 py-0.2 rounded font-semibold uppercase ${
                        file.category === 'core' ? 'bg-blue-100 text-blue-700' :
                        file.category === 'gui' ? 'bg-purple-100 text-purple-700' :
                        file.category === 'test' ? 'bg-emerald-100 text-emerald-700' :
                        'bg-slate-100 text-slate-600'
                      }`}>
                        {file.category}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">{file.description}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Code Viewer (8 cols) */}
        <div className="md:col-span-8 bg-slate-900 rounded-xl border border-slate-800 shadow-lg overflow-hidden flex flex-col">
          <div className="p-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300 font-mono text-xs font-semibold">
              <FileCode className="w-4 h-4 text-emerald-400" />
              <span>{selectedFile.path}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="px-2.5 py-1 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-md transition flex items-center gap-1.5"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Đã sao chép!' : 'Sao chép mã'}
              </button>
              <button
                onClick={handleDownloadSingle}
                className="px-2.5 py-1 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-md transition flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                Tải file
              </button>
            </div>
          </div>

          <div className="p-4 bg-slate-950/60 border-b border-slate-800 text-xs text-slate-400">
            <strong>Mô tả:</strong> {selectedFile.description}
          </div>

          <pre className="p-4 font-mono text-xs text-slate-200 overflow-x-auto overflow-y-auto max-h-[480px] leading-relaxed whitespace-pre">
            {selectedFile.code}
          </pre>
        </div>
      </div>
    </div>
  );
};
