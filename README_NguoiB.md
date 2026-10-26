# README – Thành viên B: Tài khoản, kiểm tra dữ liệu, nhập câu hỏi và tab Câu hỏi

**Đồ án:** Đề tài 7 – Hệ thống quản lý ngân hàng câu hỏi (Python, Tkinter, JSON)
**Vai trò:** B – phụ trách tài khoản, kiểm tra dữ liệu (Regex), nhập câu hỏi từ file/API và giao diện quản lý câu hỏi.
**Phụ thuộc vào A:** `config.py`, `base_models.py` (`User`, `Admin`), `json_file_handler.py`, `data_repository.py`. Nên bắt đầu bằng `validators.py` và `auth.py` vì ít phụ thuộc nhất.

---

## 1. Nội dung chính của người làm

- Xây dựng `auth.py`: đăng ký, đăng nhập, đổi mật khẩu, băm mật khẩu có salt; lưu tài khoản vào `users.json`; phân biệt vai trò Quản trị viên / Người dùng.
- Xây dựng `validators.py`: kiểm tra bằng Regular Expression (email, username, mã câu hỏi, ngày) và kiểm tra nội dung/đáp án câu hỏi.
- Vá `import_questions.py`: đọc câu hỏi từ file mẫu `.txt`, xử lý dòng sai định dạng, báo lỗi rõ ràng, lưu qua `JsonDataRepository`.
- Viết `api_import.py`: lấy câu hỏi từ API, xử lý lỗi kết nối/timeout/dữ liệu thiếu, làm sạch dữ liệu và lưu vào JSON (chức năng Crawl/API bắt buộc).
- Xây dựng `gui/question_tab.py`: Treeview hiển thị câu hỏi, tìm kiếm theo ít nhất 2 tiêu chí, lọc theo môn/chủ đề/mức độ, CRUD có hộp thoại xác nhận khi xóa, bắt `ValueError` từ repository (ví dụ xóa câu hỏi đã nằm trong đề) và hiển thị thông báo hướng dẫn cách xử lý.
- Xây dựng `gui/question_editor.py`: Custom Widget `QuestionEditor` kế thừa `tk.Frame` để nhập/sửa nội dung và 4 phương án.
- Xây dựng `gui/subject_topic_tab.py`: giao diện CRUD Môn học và Chủ đề (2 Treeview, form thêm/sửa/xóa), hiển thị thông báo khi xóa môn còn chủ đề hoặc chủ đề còn câu hỏi.
- Chỉ hiện tab Câu hỏi và tab Môn học/Chủ đề cho Quản trị viên (dùng `User.can(...)` của A).
- Gửi D danh sách nguồn thư viện, API, mã tham khảo và việc có dùng công cụ AI của phần mình để D ghi vào `docs/references.md`.
- Viết kiểm thử cho phần của mình: `test_validators.py`, `test_auth.py`, `test_import.py`.
- Chốt với A và D: các trường của `User`, tên hàm trong `auth.py` (D gọi từ `login_window.py`).

---

## 2. File cần tạo / chỉnh sửa và mục đích chính

| File | Mục đích chính |
|---|---|
| `auth.py` | Đăng ký, đăng nhập, đổi mật khẩu, băm mật khẩu; đọc/ghi `users.json`; trả về `User` hoặc `Admin` theo vai trò |
| `validators.py` | Tập trung toàn bộ kiểm tra dữ liệu nhập: Regex email, username, mã câu hỏi, ngày; kiểm tra nội dung và đáp án |
| `import_questions.py` (vá) | Nhập hàng loạt câu hỏi từ file văn bản mẫu vào ngân hàng câu hỏi, bỏ qua và báo cáo dòng lỗi |
| `api_import.py` | Lấy câu hỏi từ API bên ngoài, làm sạch, chuyển đổi và lưu vào JSON |
| `gui/question_tab.py` | Tab quản lý câu hỏi: Treeview, ô tìm kiếm, bộ lọc, nút Thêm/Sửa/Xóa, nút Nhập file / Nhập từ API |
| `gui/question_editor.py` | Custom Widget `QuestionEditor` (kế thừa `tk.Frame`): form nhập nội dung, 4 phương án, chọn đáp án đúng, mức độ |
| `gui/subject_topic_tab.py` | Tab CRUD Môn học và Chủ đề: 2 Treeview, form thêm/sửa/xóa, hiển thị lỗi ràng buộc cha–con (bổ sung để đủ ≥ 8 chức năng nghiệp vụ) |
| `tests/test_validators.py` | Kiểm thử Regex và kiểm tra đáp án: hợp lệ, không hợp lệ, trường hợp biên |
| `tests/test_auth.py` | Kiểm thử đăng ký, đăng nhập, đổi mật khẩu, trùng username, sai mật khẩu, băm mật khẩu |
| `tests/test_import.py` | Kiểm thử nhập file: file thiếu, file rỗng, dòng sai định dạng, câu hỏi trùng |

---

## 3. Nguồn nội dung của từng file

| File | Nội dung lấy từ đâu |
|---|---|
| `auth.py` | Mục 2.5 của quy định (tạo tài khoản, đăng nhập, đổi mật khẩu, hai vai trò, mật khẩu không hiển thị, khuyến khích băm); `User`/`Admin` do A thêm vào `base_models.py`; module `hashlib`, `secrets` của Python |
| `validators.py` | Mục 2.7 của quy định (Regex ≥ 2 loại, thông báo lỗi hướng dẫn cách sửa); mục VII.6 (trùng mã, dữ liệu rỗng, số âm, ngày không hợp lệ); `Question.is_valid()` trong `base_models.py` cho phần kiểm tra đáp án |
| `import_questions.py` | File hiện có của nhóm (cần vá); file mẫu `data/sample/mau_cau_hoi.txt`; mục 2.3 của quy định (xử lý file thiếu/rỗng/sai định dạng) |
| `api_import.py` | Mục 2.4 của quy định (thư viện `requests`/`urllib`, xử lý lỗi kết nối, timeout, dữ liệu thiếu, ghi rõ nguồn trong báo cáo, tuân thủ điều khoản sử dụng); `API_URL` trong `config.py` của A; tài liệu của API đã chọn |
| `gui/question_tab.py` | Mục 6 (Tkinter) và 2.1, 2.2 của quy định; Đề tài 7 (Treeview câu hỏi, Text nội dung); `JsonDataRepository` của A; hằng số GUI trong `config.py` |
| `gui/question_editor.py` | Đề tài 7 (nâng cao: Custom QuestionEditor); mục 8 của quy định (Custom Widget kế thừa widget Tkinter); `Question`, `Option`, `DifficultyLevel` trong `base_models.py` |
| `gui/subject_topic_tab.py` | Mục 7 của quy định (≥ 8 chức năng nghiệp vụ, có CRUD); mục 6 (Treeview, Messagebox); các hàm CRUD Môn/Chủ đề và ràng buộc xóa cha–con trong `data_repository.py` của A |
| `tests/test_validators.py` | Mục 9 của quy định (≥ 10 trường hợp: hợp lệ, không hợp lệ, biên); các hàm trong `validators.py` |
| `tests/test_auth.py` | Mục 9 của quy định (kiểm thử đăng nhập); các hàm trong `auth.py` |
| `tests/test_import.py` | Mục 9 của quy định; hành vi của `import_questions.py` |

---

## 4. Bảng phụ thuộc: file nào cần lấy gì từ file / class nào để chạy khớp nhau

| File của B | Lấy từ file | Class / hàm / hằng số cụ thể | Dùng để làm gì |
|---|---|---|---|
| `validators.py` | `base_models.py` (A) | `Question.is_valid()`, `Option` | Kiểm tra đáp án bằng một nguồn duy nhất, không viết lại luật |
| | `config.py` (A) | Hằng số mẫu Regex nếu đặt chung | Dễ chỉnh mẫu ở một nơi |
| `auth.py` | `base_models.py` (A) | `User`, `Admin` (trường `username`, `password_hash`, `role`, `email`) | Tạo đối tượng người dùng sau khi đăng nhập |
| | `json_file_handler.py` (A) | `JsonFileHandler` | Đọc/ghi `users.json` an toàn |
| | `config.py` (A) | `USERS_FILE` | Đường dẫn file tài khoản |
| | `validators.py` (B) | Hàm kiểm tra email, username | Kiểm tra khi đăng ký |
| `import_questions.py` | `data_repository.py` (A) | `JsonDataRepository.add_question`, `get_topic` | Lưu câu hỏi đã nhập |
| | `base_models.py` (A) | `Question.create`, `Option.create`, `DifficultyLevel` | Dựng đối tượng từ dòng văn bản |
| | `validators.py` (B) | Hàm kiểm tra câu hỏi | Loại dòng sai trước khi lưu |
| | `config.py` (A) | Đường dẫn `data/sample/` | Tìm file mẫu |
| `api_import.py` | `config.py` (A) | `API_URL`, `API_QUESTIONS_FILE` (**cần nhờ A bổ sung hằng số này**) | Nguồn API và file JSON đích |
| | `json_file_handler.py` (A) | `JsonFileHandler` | Ghi kết quả API vào JSON |
| | `data_repository.py` (A), `validators.py` (B) | `add_question`, hàm kiểm tra câu hỏi | Nạp dữ liệu API vào ngân hàng câu hỏi sau khi làm sạch |
| `gui/question_tab.py` | `data_repository.py` (A) | `JsonDataRepository`: `list_questions`, `add_question`, `update_question`, `delete_question`, `list_subjects`, `list_topics`, và hàm tìm kiếm A sẽ thêm | Nguồn dữ liệu cho Treeview và các nút CRUD |
| | `gui/question_editor.py` (B) | `QuestionEditor` | Form thêm/sửa |
| | `import_questions.py`, `api_import.py` (B) | Hàm nhập file, hàm nhập API | Nút Nhập file / Nhập từ API |
| | `base_models.py`, `config.py` (A) | `Question`, `DifficultyLevel`; hằng số GUI | Hiển thị và giao diện thống nhất |
| | `gui/app.py`, `base_models.py` (A) | Người dùng hiện tại do `app.py` truyền vào; `User.can("manage_question")` | Chỉ hiện tab và nút Thêm/Sửa/Xóa với Quản trị viên |
| `gui/question_editor.py` | `base_models.py` (A) | `Question`, `Option`, `DifficultyLevel` | Nạp câu hỏi vào form và trả về `Question` |
| | `validators.py` (B) | Hàm kiểm tra câu hỏi | Báo lỗi ngay trên form |
| `gui/subject_topic_tab.py` | `data_repository.py` (A) | `add_subject`, `update_subject`, `delete_subject`, `add_topic`, `update_topic`, `delete_topic`, `list_subjects`, `list_topics` | CRUD; bắt `ValueError` khi xóa môn còn chủ đề hoặc chủ đề còn câu hỏi |
| | `base_models.py` (A) | `Subject`, `Topic` | Dựng đối tượng từ form |
| | `config.py`, `gui/app.py` (A) | Hằng số GUI; `User.can("manage_subject_topic")` | Giao diện thống nhất; chỉ Quản trị viên thấy tab; `app.py` nhúng `SubjectTopicTab` vào Notebook |
| `tests/test_validators.py` | `validators.py` (B) | Mọi hàm kiểm tra | Kiểm thử |
| `tests/test_auth.py` | `auth.py` (B), `json_file_handler.py` (A) | Hàm đăng ký/đăng nhập; `JsonFileHandler` | Kiểm thử trên file `users.json` tạm |
| `tests/test_import.py` | `import_questions.py` (B), `data_repository.py` (A) | Hàm nhập file; `JsonDataRepository` | Kiểm thử trên dữ liệu JSON tạm |

**Điểm phải chốt với nhóm trước khi viết code:**

1. Tên hàm trong `auth.py` (đề xuất: `register`, `login`, `change_password`, `hash_password`) để D gọi đúng từ `login_window.py` và A gọi từ `app.py`.
2. Hàm tìm kiếm trong `data_repository.py` (đề xuất: `search_questions(keyword, topic_id, difficulty)`) để `question_tab.py` dùng.
3. Mã câu hỏi là `q_` + 8 ký tự hex do hệ thống sinh; Regex mã câu hỏi trong `validators.py` phải khớp mẫu này.
4. Nhờ A thêm hằng số `API_QUESTIONS_FILE` (ví dụ `data/api_questions.json`) vào `config.py`.
5. Thông báo khi xóa câu hỏi đã nằm trong đề: A ném `ValueError`, `question_tab.py` hiển thị nguyên văn thông báo đó.

---

## 5. Thứ tự làm đề xuất

1. `validators.py` và `tests/test_validators.py` (gần như độc lập).
2. `auth.py` và `tests/test_auth.py` (cần `User`/`Admin` và `JsonFileHandler` của A; có thể dùng bản tạm trong lúc chờ).
3. Vá `import_questions.py` và `tests/test_import.py`.
4. `gui/question_editor.py`, `gui/question_tab.py`, rồi `gui/subject_topic_tab.py` (cùng khuôn với tab câu hỏi).
5. `api_import.py` sau cùng (cần chọn API và đọc điều khoản sử dụng).

## 6. Phụ thuộc với thành viên khác

- **A:** `auth.py` cần `User`/`Admin`; `question_tab.py` cần hàm tìm kiếm; `app.py` nhúng `QuestionTab` vào Notebook.
- **C:** `exam_tab.py` dùng chung `list_questions`/`count_questions`; thống nhất cách hiển thị mức độ (`DifficultyLevel`).
- **D:** `login_window.py` gọi `auth.py`; `sample_data.py` tạo dữ liệu mẫu mà `import_questions.py` có thể tái sử dụng.
