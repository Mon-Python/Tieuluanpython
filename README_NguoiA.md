# README – Thành viên A: Hạ tầng, dữ liệu lõi và cửa sổ chính

**Đồ án:** Đề tài 7 – Hệ thống quản lý ngân hàng câu hỏi (Python, Tkinter, JSON)
**Vai trò:** A – nền tảng mà B, C, D đều phụ thuộc. Cần hoàn thành sớm `config.py`, `base_models.py` và `json_file_handler.py` để cả nhóm không bị chặn.

---

## 1. Nội dung chính của người làm

- Khởi động ứng dụng từ `main.py`, dùng `sys.argv` (tham số dòng lệnh) và `sys.exit` (mã thoát).
- Xây dựng `config.py`: đường dẫn dữ liệu (không dùng đường dẫn tuyệt đối, có nhánh `sys.frozen` khi đóng gói bằng PyInstaller), hằng số giao diện (font, màu, khoảng cách), URL API.
- Bổ sung `base_models.py`: lớp `User`, `Admin` (kế thừa, ghi đè phương thức phân quyền) và `from_dict` (kèm `to_dict`) cho `Exam`, `ExamResult`.
- Viết `json_file_handler.py`: đọc/ghi JSON an toàn (dùng `with`, ghi file tạm rồi thay thế), xử lý file không tồn tại, file rỗng, sai định dạng, không có quyền; có `backup()` và `restore()`.
- Vá `data_repository.py`: chuyển sang gọi `JsonFileHandler`, lấy đường dẫn từ `config.py`, bổ sung tìm kiếm theo ít nhất 2 tiêu chí.
- Xây dựng `gui/app.py`: cửa sổ chính, Menu (Sao lưu / Khôi phục / Đăng xuất / Đổi mật khẩu), Notebook chứa các tab của B, C, D, phân quyền Quản trị viên và Người dùng.
- Lập bảng phân quyền (mục 7.1) và hiện thực bằng `PERMISSIONS` trong `config.py` cùng phương thức `User.can(action)`; `app.py` dùng để ẩn/hiện tab và nút theo vai trò.
- Thêm hộp thoại xác nhận khi thoát ứng dụng, đăng xuất và khôi phục dữ liệu (ghi đè dữ liệu hiện tại) trong `gui/app.py`.
- Chặn hoặc cảnh báo khi xóa câu hỏi đã nằm trong đề: `JsonDataRepository` nhận tham số tùy chọn `usage_checker` (hàm `is_question_used` do D cung cấp).
- Viết kiểm thử cho phần của mình: `test_json_file_handler.py`, `test_data_repository.py`.
- Tạo `requirements.txt` và `.gitignore`.
- Gửi D danh sách nguồn thư viện, mã tham khảo và việc có dùng công cụ AI của phần mình để D ghi vào `docs/references.md`.
- Chốt và thông báo cho nhóm: tên hàm và định dạng JSON của `JsonFileHandler`, `to_dict`/`from_dict`.

---

## 2. File cần tạo / chỉnh sửa và mục đích chính

| File | Mục đích chính |
|---|---|
| `main.py` | Điểm khởi động ứng dụng; đọc `sys.argv`, gọi cửa sổ đăng nhập rồi `app.py`, thoát bằng `sys.exit` |
| `config.py` | Tập trung đường dẫn dữ liệu, hằng số giao diện, URL API; tự nhận biết chạy từ mã nguồn hay từ file `.exe`; chứa bảng phân quyền `PERMISSIONS` |
| `base_models.py` (bổ sung) | Thêm `User`, `Admin`; thêm `to_dict`/`from_dict` cho `Exam`, `ExamResult` để D lưu `exams.json`, `results.json`; thêm `User.can(action)` kiểm tra quyền |
| `json_file_handler.py` | Lớp đọc/ghi JSON an toàn, sao lưu và khôi phục; mọi file lưu trữ khác đều dùng lớp này |
| `data_repository.py` (vá) | CRUD Môn học, Chủ đề, Câu hỏi qua `JsonFileHandler`; thêm tìm kiếm, bỏ đường dẫn cứng; chặn/cảnh báo xóa câu hỏi đã nằm trong đề |
| `gui/__init__.py` | Đánh dấu thư mục `gui` là package (tên thật là `__init__.py`) |
| `gui/app.py` | Cửa sổ chính, Menu, Notebook, phân quyền hiển thị chức năng theo vai trò; xác nhận khi thoát/đăng xuất/khôi phục |
| `tests/test_json_file_handler.py` | Kiểm thử đọc/ghi, file thiếu, file rỗng, sai định dạng, backup/restore |
| `tests/test_data_repository.py` | Kiểm thử CRUD, ràng buộc xóa cha–con, tìm kiếm, dữ liệu không hợp lệ |
| `requirements.txt` | Danh sách thư viện phụ thuộc và phiên bản Python |
| `.gitignore` | Loại `__pycache__`, `build/`, `dist/`, `data/backup/`, `logs/`, file tạm |

---

## 3. Nguồn nội dung của từng file

| File | Nội dung lấy từ đâu |
|---|---|
| `main.py` | Mục 8 (kỹ thuật) của quy định: dùng module `sys`; `config.py` để lấy đường dẫn; `gui/login_window.py` (D) và `gui/app.py` (A) để mở giao diện |
| `config.py` | Mục 8 của quy định (file cấu hình riêng, không đường dẫn tuyệt đối) và mục VII.8 (danh sách kiểm tra); URL API thống nhất với B (`api_import.py`); tên file dữ liệu theo cây thư mục `data/`; bảng phân quyền theo mục 2.5 của quy định (Quản trị viên dùng đầy đủ, người dùng thường chỉ dùng chức năng được phân quyền) |
| `base_models.py` (User, Admin) | Mục 2.5 của quy định (hai vai trò, mật khẩu không hiển thị trực tiếp); mục 2.6 (kế thừa/ghi đè); trường `password_hash`, `role` thống nhất với B (`auth.py`) |
| `base_models.py` (from_dict) | Định nghĩa `Exam`, `ExamResult` đã có trong `base_models.py`; mẫu viết theo `_question_from_dict` trong `data_repository.py`; định dạng `exams.json`/`results.json` chốt cùng C và D |
| `json_file_handler.py` | Mục 2.3 của quy định (dùng `with`, xử lý file thiếu/rỗng/sai định dạng/không quyền, sao lưu trước khi ghi đè); hàm `_load_json`/`_save_json` hiện có trong `data_repository.py` làm điểm xuất phát |
| `data_repository.py` (vá) | Giữ nguyên toàn bộ CRUD hiện có; thay `_load_json`/`_save_json` bằng `JsonFileHandler`; mục 2.2 của quy định (Search theo ít nhất 2 tiêu chí); `seed_sample_data` chuyển sang `sample_data.py` của D |
| `gui/app.py` | Mục 6 (Tkinter) và 2.5 của quy định; các tab do B (`question_tab.py`), C (`exam_tab.py`, `take_exam_window.py`), D (`stats_tab.py`) cung cấp; `User`/`Admin` trong `base_models.py` để phân quyền |
| `tests/test_json_file_handler.py` | Mục 9 của quy định (≥ 10 trường hợp: hợp lệ, không hợp lệ, biên); hành vi của `json_file_handler.py` |
| `tests/test_data_repository.py` | Mục 9 của quy định; hành vi `JsonDataRepository` và các ràng buộc xóa trong `data_repository.py` hiện có |
| `requirements.txt` | Thư viện thực tế mà cả nhóm import (hỏi B về `requests`, `tkcalendar` nếu dùng DateEntry, PyInstaller cho D); mục 2.8 của quy định (hướng dẫn cài đặt) |
| `.gitignore` | Cây thư mục: `data/backup/`, `data/export/`, `logs/` |

---

## 4. Bảng phụ thuộc: file nào cần lấy gì từ file / class nào để chạy khớp nhau

| File của A | Lấy từ file | Class / hàm / hằng số cụ thể | Dùng để làm gì |
|---|---|---|---|
| `config.py` | Không phụ thuộc file nào của nhóm (chỉ dùng `pathlib`, `sys`) | Cung cấp: `BASE_DIR`, `DATA_DIR`, `BACKUP_DIR`, `EXPORT_DIR`, `LOG_DIR`, `SUBJECTS_TOPICS_FILE`, `QUESTIONS_FILE`, `USERS_FILE`, `EXAMS_FILE`, `RESULTS_FILE`, `API_URL`, hằng số font/màu | Mọi file khác `import` từ đây, không tự viết đường dẫn |
| `base_models.py` (User, Admin) | Chính `base_models.py` | `BaseEntity`, `generate_id("user")` | `User` kế thừa `BaseEntity`; `Admin` kế thừa `User` và ghi đè phương thức kiểm tra quyền |
| `base_models.py` (to_dict / from_dict) | Chính `base_models.py` | `Exam`, `ExamResult`, `StudentAnswer`, `BaseEntity.created_at` (đổi `datetime` ↔ chuỗi ISO) | D dùng trong `exam_repository.py` để lưu và đọc `exams.json`, `results.json`; viết theo mẫu `_question_from_dict` |
| `json_file_handler.py` | `config.py` | `BACKUP_DIR`, `DATA_DIR` | Biết nơi đặt file sao lưu; tự tạo thư mục khi thiếu |
| `data_repository.py` | `base_models.py` | `Subject`, `Topic`, `Question`, `Option`, `DifficultyLevel`, `SubjectTopicRepository`, `QuestionRepository`, `generate_id` | Kế thừa hai lớp trừu tượng, dựng object từ dict |
| | `json_file_handler.py` | `JsonFileHandler` (đọc, ghi, backup, restore) | Thay `_load_json` / `_save_json` hiện có |
| | `exam_repository.py` (D) | `is_question_used(question_id)` | Truyền vào `JsonDataRepository` qua tham số `usage_checker` để chặn/cảnh báo xóa câu hỏi đã nằm trong đề (A nhận hàm từ bên ngoài, không import `exam_repository` để tránh import vòng) |
| | `config.py` | `SUBJECTS_TOPICS_FILE`, `QUESTIONS_FILE` | Thay đường dẫn cứng `"data/..."` |
| `gui/app.py` | `config.py` | Hằng số GUI (font, màu, kích thước cửa sổ) | Giao diện thống nhất |
| | `base_models.py`, `config.py` | `User`, `Admin`, `User.can(action)`, `PERMISSIONS` | Quyết định tab / nút nào hiện theo vai trò |
| | `json_file_handler.py` | `JsonFileHandler.backup()`, `restore()` | Gắn vào Menu Sao lưu / Khôi phục |
| | `data_repository.py` | `JsonDataRepository` | Tạo một instance dùng chung, truyền xuống các tab |
| | `auth.py` (B) | Lớp / hàm đổi mật khẩu và đăng xuất | Mục Đổi mật khẩu trong Menu |
| | `gui/login_window.py` (D) | Lớp cửa sổ đăng nhập | Quay lại đăng nhập khi đăng xuất |
| | `gui/question_tab.py` (B) | `QuestionTab` | Tab Câu hỏi trong Notebook |
| | `gui/exam_tab.py`, `gui/take_exam_window.py` (C) | `ExamTab`, `TakeExamWindow` | Tab Tạo đề và cửa sổ làm bài |
| | `gui/stats_tab.py` (D) | `StatsTab` | Tab Thống kê |
| | `gui/subject_topic_tab.py` (B) | `SubjectTopicTab` | Tab Môn học / Chủ đề (chỉ Quản trị viên) |
| | `exam_repository.py` (D) | Repository của đề và kết quả | Truyền cho tab của C và D |
| `main.py` | `config.py` | Đường dẫn, hằng số | Khởi tạo thư mục dữ liệu |
| | `sample_data.py` (D) | Hàm tạo lại dữ liệu mẫu khi file mất | Gọi lúc khởi động nếu thiếu dữ liệu |
| | `gui/login_window.py` (D), `gui/app.py` (A) | Cửa sổ đăng nhập, cửa sổ chính | Luồng: đăng nhập thành công thì mở `app.py` |
| `tests/test_json_file_handler.py` | `json_file_handler.py` | `JsonFileHandler` | Kiểm thử trên thư mục tạm, không đụng dữ liệu thật |
| `tests/test_data_repository.py` | `data_repository.py`, `base_models.py`, `json_file_handler.py` | `JsonDataRepository`, `Subject`, `Topic`, `Question`, `Option`, `DifficultyLevel` | Kiểm thử CRUD, ràng buộc xóa, tìm kiếm với file JSON tạm |
| `requirements.txt` | Các file import thư viện ngoài của B, C, D | Ví dụ `requests` (B), `tkcalendar` nếu dùng DateEntry, PyInstaller (D) | Liệt kê đủ để máy khác chạy được |
| `.gitignore` | `config.py` | `BACKUP_DIR`, `EXPORT_DIR`, `LOG_DIR` | Loại đúng các thư mục sinh ra khi chạy |

**Ba điểm phải chốt với nhóm trước khi viết code:**

1. Tên hằng số trong `config.py` (bảng trên là đề xuất; B, C, D import đúng các tên này).
2. Tên hàm của `JsonFileHandler` (ví dụ `read`, `write`, `backup`, `restore`) và kiểu trả về khi file thiếu hoặc rỗng.
3. Các trường của `User` (`username`, `password_hash`, `role`, `email`) để `auth.py` của B và `login_window.py` của D dùng đúng.

---

## 5. Thứ tự làm đề xuất

1. `config.py` rồi `json_file_handler.py` (cả nhóm cần ngay).
2. `base_models.py` (User, Admin, from_dict/to_dict) và thông báo định dạng cho B, C, D.
3. Vá `data_repository.py`, viết hai file test tương ứng.
4. `gui/app.py` khi các tab của B, C, D đã có khung.
5. `main.py`, `requirements.txt`, `.gitignore`.

## 6. Phụ thuộc với thành viên khác

- **B:** `auth.py` cần `User`/`Admin`; `question_tab.py` cần hàm tìm kiếm của `data_repository.py`.
- **C:** `exam_generator.py` dùng `count_questions`/`list_questions`.
- **D:** `exam_repository.py` dùng `JsonFileHandler` và `from_dict` và cung cấp `is_question_used`; `login_window.py` được `app.py` gọi.

---

## 7. Bổ sung theo rà soát yêu cầu quy định

### 7.1 Bảng phân quyền đề xuất (cần cả nhóm xác nhận)

Người dùng thường không thấy tab Câu hỏi và Môn học/Chủ đề để tránh lộ đáp án.

| Khóa quyền (`PERMISSIONS`) | Chức năng | Quản trị viên | Người dùng thường |
|---|---|---|---|
| `manage_subject_topic` | CRUD Môn học, Chủ đề | ✅ | ❌ |
| `manage_question` | CRUD câu hỏi | ✅ | ❌ |
| `import_question` | Nhập câu hỏi từ file / API | ✅ | ❌ |
| `create_exam` | Tạo / tái lập đề | ✅ | ❌ |
| `export_exam` | Xuất đề và đáp án | ✅ | ❌ |
| `backup_restore` | Sao lưu / khôi phục dữ liệu | ✅ | ❌ |
| `take_exam` | Chọn đề từ danh sách và làm bài | ✅ | ✅ |
| `view_all_stats` | Thống kê toàn bộ kết quả | ✅ | ❌ |
| `view_own_stats` | Xem kết quả của chính mình | ✅ | ✅ |
| `change_password` | Đổi mật khẩu, đăng xuất | ✅ | ✅ |

### 7.2 Xác nhận thao tác quan trọng (mục 6 của quy định)

| Thao tác | Nơi xử lý | Người làm |
|---|---|---|
| Xóa câu hỏi, môn học, chủ đề | `question_tab.py`, `subject_topic_tab.py` | B |
| Thoát ứng dụng, đăng xuất | `gui/app.py` | A |
| Khôi phục dữ liệu (ghi đè dữ liệu hiện tại) | `gui/app.py` | A |
| Nộp bài, đóng cửa sổ làm bài giữa chừng | `gui/take_exam_window.py` | C |

### 7.3 Ghi chú

- Tìm kiếm theo ít nhất 2 tiêu chí: A thêm `search_questions` vào `data_repository.py` (đã có ở bảng file cần chỉnh sửa).
- Môn học/Chủ đề có giao diện CRUD riêng (`subject_topic_tab.py`, B) nên `app.py` phải nhúng thêm tab này.
