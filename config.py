"""
config.py
==========
[A sở hữu] Nơi DUY NHẤT chứa đường dẫn, hằng số giao diện, URL API, phân quyền.
Quy tắc: file này KHÔNG import file nào của nhóm (tránh import vòng).
"""

import sys
from pathlib import Path

# ---------- Thư mục gốc ----------
# Chạy từ mã nguồn: thư mục chứa config.py.
# Chạy từ .exe (PyInstaller): thư mục chứa file .exe (data/ nằm cạnh .exe,
# không dùng sys._MEIPASS vì thư mục đó bị xóa sau mỗi lần chạy).
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# ---------- Thư mục dữ liệu ----------
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backup"
EXPORT_DIR = DATA_DIR / "export"
SAMPLE_DIR = DATA_DIR / "sample"        # chứa mau_cau_hoi.txt (B dùng)
LOG_DIR = BASE_DIR / "logs"

# ---------- File dữ liệu ----------
SUBJECTS_TOPICS_FILE = DATA_DIR / "subjects_topics.json"
QUESTIONS_FILE = DATA_DIR / "questions.json"
USERS_FILE = DATA_DIR / "users.json"
EXAMS_FILE = DATA_DIR / "exams.json"
RESULTS_FILE = DATA_DIR / "results.json"
API_QUESTIONS_FILE = DATA_DIR / "api_questions.json"   # B yêu cầu bổ sung

# ---------- API (chốt lại với B khi chọn xong API) ----------
API_URL = "https://opentdb.com/api.php?amount=20&type=multiple"  # TODO: B xác nhận
API_TIMEOUT_SECONDS = 10

# ---------- Vai trò & phân quyền ----------
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# {khóa quyền: tập vai trò được phép} - đúng bảng 7.1 README A
PERMISSIONS = {
    "manage_subject_topic": {ROLE_ADMIN},
    "manage_question":      {ROLE_ADMIN},
    "import_question":      {ROLE_ADMIN},
    "create_exam":          {ROLE_ADMIN},
    "export_exam":          {ROLE_ADMIN},
    "backup_restore":       {ROLE_ADMIN},
    "view_all_stats":       {ROLE_ADMIN},
    "take_exam":            {ROLE_ADMIN, ROLE_USER},
    "view_own_stats":       {ROLE_ADMIN, ROLE_USER},
    "change_password":      {ROLE_ADMIN, ROLE_USER},
}

# ---------- Hằng số giao diện (mọi tab dùng chung) ----------
APP_TITLE = "Quản lý ngân hàng câu hỏi"
WINDOW_SIZE = "1100x700"
WINDOW_MIN_SIZE = (900, 600)

FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_TITLE = (FONT_FAMILY, 14, "bold")

COLOR_PRIMARY = "#2563eb"
COLOR_BG = "#f8fafc"
COLOR_TEXT = "#0f172a"
COLOR_SUCCESS = "#16a34a"
COLOR_ERROR = "#dc2626"
COLOR_CHART_BAR = "#3b82f6"

PADDING = 8


def ensure_data_dirs() -> None:
    """Tạo các thư mục dữ liệu nếu chưa có (main.py gọi lúc khởi động)."""
    for d in (DATA_DIR, BACKUP_DIR, EXPORT_DIR, SAMPLE_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)