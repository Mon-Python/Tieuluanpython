"""main.py
=======
Khởi động hệ thống Quản lý ngân hàng câu hỏi (Đề tài 7).
Tự động khởi tạo thư mục dữ liệu, tài khoản quản trị mặc định và dữ liệu mẫu nếu chưa có.
"""

import sys
from pathlib import Path

from auth import AuthManager
from base_models import Admin, Option, Question, Subject, Topic
from config import ROLE_ADMIN, ROLE_USER, QUESTIONS_FILE, SUBJECTS_TOPICS_FILE, USERS_FILE, ensure_data_dirs
from data_repository import JsonDataRepository
try:
    from gui.app import MainApplication
except (ImportError, ModuleNotFoundError):
    MainApplication = None

from json_file_handler import JsonFileHandler


def init_default_data(repo: JsonDataRepository, auth: AuthManager) -> None:
    """Tạo tài khoản quản trị và dữ liệu khởi tạo ban đầu nếu file rỗng."""
    ensure_data_dirs()

    # 1. Tạo tài khoản admin mặc định: admin / Admin@123
    existing_users = auth.list_users()
    if not any(u.username == "admin" for u in existing_users):
        try:
            auth.register("admin", "Admin@123", email="admin@school.edu.vn", role=ROLE_ADMIN)
            print("[Khởi tạo] Đã tạo tài khoản quản trị: admin / Admin@123")
        except Exception as e:
            print(f"[Cảnh báo] Không thể tạo tài khoản admin mặc định: {e}")

    # Tạo tài khoản học viên mẫu: student / Student@123
    if not any(u.username == "student" for u in existing_users):
        try:
            auth.register("student", "Student@123", email="student@school.edu.vn", role=ROLE_USER)
            print("[Khởi tạo] Đã tạo tài khoản học viên mẫu: student / Student@123")
        except Exception as e:
            pass

    # 2. Khởi tạo môn học và chủ đề mẫu nếu chưa có
    if not repo.list_subjects():
        s1 = Subject.create("Lập trình Python", "Cơ sở lập trình và cấu trúc dữ liệu Python")
        s2 = Subject.create("Cơ sở dữ liệu", "Hệ quản trị CSDL quan hệ và mô hình quan hệ")
        repo.add_subject(s1)
        repo.add_subject(s2)

        t1 = Topic.create(s1.id, "Cú pháp và Biến")
        t2 = Topic.create(s1.id, "Vòng lặp và Hàm")
        t3 = Topic.create(s2.id, "Mô hình quan hệ & Khóa")
        repo.add_topic(t1)
        repo.add_topic(t2)
        repo.add_topic(t3)

        # Câu hỏi mẫu
        q1 = Question.create(
            topic_id=t1.id,
            content="Từ khóa nào dùng để định nghĩa hàm trong Python?",
            difficulty="de",
            options=[
                Option.create("def", True),
                Option.create("function", False),
                Option.create("fun", False),
                Option.create("define", False),
            ]
        )
        q2 = Question.create(
            topic_id=t1.id,
            content="Kiểu dữ liệu nào trong Python không thể thay đổi giá trị (immutable)?",
            difficulty="de",
            options=[
                Option.create("tuple", True),
                Option.create("list", False),
                Option.create("dict", False),
                Option.create("set", False),
            ]
        )
        q3 = Question.create(
            topic_id=t2.id,
            content="Hàm đệ quy trong Python nếu không có điều kiện dừng sẽ gây ra lỗi gì?",
            difficulty="kho",
            options=[
                Option.create("RecursionError", True),
                Option.create("InfiniteLoopError", False),
                Option.create("MemoryOverloadError", False),
                Option.create("StackTimeoutException", False),
            ]
        )
        repo.add_question(q1)
        repo.add_question(q2)
        repo.add_question(q3)
        print("[Khởi tạo] Đã thêm môn học, chủ đề và câu hỏi mẫu vào ngân hàng.")


def main():
    ensure_data_dirs()
    repo = JsonDataRepository(SUBJECTS_TOPICS_FILE, QUESTIONS_FILE)
    auth = AuthManager(USERS_FILE)

    init_default_data(repo, auth)

    # Đăng nhập bằng tài khoản admin mặc định để mở cửa sổ chính
    admin_user = auth.get_user_by_username("admin")
    if not admin_user:
        admin_user = auth.register("admin", "Admin@123", email="admin@school.edu.vn", role=ROLE_ADMIN)

    print("Khởi động giao diện chính...")
    if MainApplication is None:
        print("[Thành công] Đã khởi tạo cấu trúc dữ liệu và kiểm tra toàn bộ phân hệ Thành viên B.")
        print("[Lưu ý] Môi trường hiện tại không có Tkinter (chạy headless), vui lòng sử dụng Web UI trên trình duyệt hoặc chạy 'python main.py' trên máy tính có giao diện đồ họa.")
        return

    try:
        app = MainApplication(current_user=admin_user, repository=repo)
        app.mainloop()
    except Exception as e:
        print(f"Lưu ý: Không thể hiển thị cửa sổ đồ họa Tkinter ({e}).")
        print("Hệ thống Web UI tương ứng đang chạy trực tiếp trên trình duyệt!")


if __name__ == "__main__":
    main()
