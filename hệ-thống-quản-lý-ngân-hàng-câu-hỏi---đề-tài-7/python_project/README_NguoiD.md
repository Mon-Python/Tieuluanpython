# README – Thành viên D: Lưu đề/kết quả, xuất file, dữ liệu mẫu, thống kê, đăng nhập, tài liệu và đóng gói

**Đồ án:** Đề tài 7 – Hệ thống quản lý ngân hàng câu hỏi (Python, Tkinter, JSON)
**Vai trò:** D – phụ trách lưu trữ đề/kết quả, xuất đề và đáp án, dữ liệu mẫu, thống kê trực quan bằng Canvas, cửa sổ đăng nhập, toàn bộ tài liệu nộp và đóng gói ứng dụng.
**Phụ thuộc vào A:** `config.py`, `json_file_handler.py`, `to_dict`/`from_dict` trong `base_models.py`. **Phụ thuộc vào B:** `auth.py`. **Phụ thuộc vào C:** `grader.py` (kết quả thống kê). Nên bắt đầu bằng `exam_repository.py` vì C cần ngay để lưu đề và kết quả.

---

## 1. Nội dung chính của người làm

- Viết `exam_repository.py`: lưu và đọc `exams.json`, `results.json` thông qua `JsonFileHandler`, dùng `to_dict`/`from_dict` của A. Thêm hàm `is_question_used(question_id)` để A chặn/cảnh báo xóa câu hỏi đã nằm trong đề.
- Viết `exam_exporter.py`: lớp `ExamExporter` (implement ABC trong `base_models.py`) xuất đề (không kèm đáp án) và đáp án ra file văn bản.
- Viết `sample_data.py`: sinh dữ liệu mẫu bằng module `random`, tự tạo lại khi file dữ liệu bị mất; tạo sẵn tài khoản quản trị mặc định.
- Xây dựng `gui/login_window.py`: đăng nhập và tạo tài khoản, gọi `auth.py` của B.
- Xây dựng `gui/stats_tab.py` và `gui/bar_chart.py`: thống kê theo chủ đề, vẽ biểu đồ cột bằng Canvas.
- Viết toàn bộ tài liệu trong `docs/`: phân tích, thiết kế lớp, kiểm thử, hướng dẫn sử dụng, hướng dẫn cài đặt, bảng phân công và tỷ lệ đóng góp, báo cáo Word/PDF, slide.
- Viết `build.bat` (PyInstaller) và `README.md` gốc; kiểm tra file đóng gói trên máy khác.
- Tổng hợp bảng kiểm thử từ test của A, B, C và đối chiếu danh sách kiểm tra trước khi nộp (mục VII của quy định).
- Tổ chức chạy thử ứng dụng trên ít nhất 2 máy hoặc 2 tài khoản người dùng khác nhau và ghi kết quả vào `docs/testing.md` (mục 9 của quy định).
- Tổng hợp `docs/references.md`: nguồn thư viện, API, mã/dữ liệu tham khảo của cả nhóm và khai báo việc dùng công cụ AI theo quy định của giảng viên (mục 12).
- In quyển báo cáo theo mẫu và mang theo khi báo cáo ở Buổi 15 (mục 4 của quy định).
- Chốt với A, B, C: tên hàm của `exam_repository.py`, định dạng file xuất, cấu trúc dữ liệu thống kê.

---

## 2. File cần tạo / chỉnh sửa và mục đích chính

| File | Mục đích chính |
|---|---|
| `exam_repository.py` | Lưu và đọc đề thi, kết quả làm bài vào `exams.json`, `results.json`; có `is_question_used()` kiểm tra câu hỏi đã nằm trong đề nào chưa |
| `exam_exporter.py` | Xuất đề và đáp án ra file văn bản vào thư mục `data/export/` |
| `sample_data.py` | Sinh dữ liệu mẫu bằng `random`; tự tạo lại dữ liệu khi file mất; tạo tài khoản quản trị mặc định |
| `gui/login_window.py` | Cửa sổ đăng nhập và đăng ký; trả về đối tượng người dùng cho `main.py`/`app.py` |
| `gui/stats_tab.py` | Tab thống kê kết quả theo chủ đề; chọn đề/bài làm và hiển thị biểu đồ |
| `gui/bar_chart.py` | Widget vẽ biểu đồ cột bằng `tk.Canvas`, dùng lại được cho nhiều thống kê |
| `docs/analysis.md` | Phân tích yêu cầu: mục tiêu, phạm vi, dữ liệu, chức năng |
| `docs/class_design.md` | Bảng mô tả lớp, thuộc tính, phương thức và sơ đồ lớp |
| `docs/testing.md` | Bảng kiểm thử: đầu vào, kết quả mong đợi, kết quả thực tế, trạng thái; mục ghi lần chạy thử trên ≥ 2 máy hoặc 2 tài khoản |
| `docs/user_guide.md` | Hướng dẫn sử dụng theo từng chức năng và vai trò |
| `docs/install_guide.md` | Hướng dẫn cài đặt: phiên bản Python, thư viện, khởi tạo dữ liệu ban đầu |
| `docs/` – bảng phân công | Phân công công việc và tỷ lệ đóng góp của 4 thành viên |
| `docs/references.md` | Danh sách nguồn: thư viện, API, mã/dữ liệu tham khảo; khai báo việc dùng công cụ AI theo quy định của giảng viên |
| Quyển báo cáo in | Bản in báo cáo theo mẫu của giảng viên, mang theo khi báo cáo ở Buổi 15 |
| `docs/BaoCao.docx`, `BaoCao.pdf` | Báo cáo cuối kỳ theo mẫu của giảng viên |
| `docs/Slide.pptx` | Slide báo cáo và demo ở Buổi 15 |
| `build.bat` | Đóng gói ứng dụng thành file thực thi bằng PyInstaller |
| `README.md` | Giới thiệu dự án, cấu trúc thư mục, cách chạy nhanh |
| `tests/test_exam_repository.py`, `test_exam_exporter.py`, `test_sample_data.py` *(đề xuất bổ sung, cần nhóm đồng ý)* | Kiểm thử lưu/đọc đề, xuất file, sinh dữ liệu mẫu; quy định yêu cầu kiểm thử đọc/ghi file, xuất báo cáo và đăng nhập |

---

## 3. Nguồn nội dung của từng file

| File | Nội dung lấy từ đâu |
|---|---|
| `exam_repository.py` | Mục 2.3 của quy định (đọc/ghi JSON an toàn); `Exam`, `ExamResult` và `to_dict`/`from_dict` do A thêm vào `base_models.py`; `JsonFileHandler` của A |
| `exam_exporter.py` | ABC `ExamExporter` trong `base_models.py`; Đề tài 7 (xuất đề và đáp án ra file); mục 7 của quy định (xuất ra văn bản, CSV hoặc JSON); `Exam.shuffled_options` và `question_ids` để giữ đúng thứ tự đã trộn |
| `sample_data.py` | Mục 7 của quy định (dữ liệu mẫu bằng `random`); hàm `seed_sample_data` hiện có trong `data_repository.py` (chuyển sang đây và viết lại bằng `random`); mục VII.3 (dữ liệu mẫu tạo lại được khi file bị xóa) |
| `gui/login_window.py` | Mục 2.5 của quy định (tạo tài khoản, đăng nhập, mật khẩu không hiển thị trực tiếp); hàm trong `auth.py` của B |
| `gui/stats_tab.py` | Đề tài 7 (thống kê theo chủ đề, Canvas biểu đồ kết quả); `Grader.topic_statistics` của C; `exam_repository.py` |
| `gui/bar_chart.py` | Mục 6 của quy định (Canvas là thành phần nâng cao); hằng số màu/font trong `config.py` |
| `docs/analysis.md` | Đề tài 7 và mục 1, 2 của quy định; cây thư mục dự án |
| `docs/class_design.md` | Các lớp trong `base_models.py`, `data_repository.py`, `auth.py`, `exam_generator.py`, `grader.py`, `exam_exporter.py`; yêu cầu mục 2.6 và 2.3 (OOP, sơ đồ lớp) |
| `docs/testing.md` | Các file trong `tests/` của A, B, C (và D nếu bổ sung); mục 9 của quy định (≥ 10 trường hợp, có bảng; chạy thử trên ít nhất 2 máy hoặc 2 tài khoản nếu có điều kiện) |
| `docs/user_guide.md` | Giao diện thực tế của `app.py`, `question_tab.py`, `exam_tab.py`, `take_exam_window.py`, `stats_tab.py` |
| `docs/install_guide.md` | `requirements.txt` (A), `build.bat`, `config.py`; mục 2.8 của quy định |
| Bảng phân công | Mục 1 (hình thức thực hiện) của quy định: lập bảng phân công và ghi nhận đóng góp; README của 4 thành viên |
| `docs/references.md` | Mục 12 và mục 6 của quy định (ghi nguồn thư viện, API, mã tham khảo; dùng công cụ AI theo quy định giảng viên); danh sách nguồn do A, B, C gửi, nguồn API từ B |
| Quyển báo cáo in | Mục 4 của quy định (in quyển báo cáo theo mẫu, mang theo khi báo cáo); `BaoCao.docx` |
| `docs/BaoCao.docx`, `BaoCao.pdf` | Toàn bộ file trong `docs/`; mục VII.8 (nội dung báo cáo bắt buộc); mẫu báo cáo của giảng viên; ghi nguồn API/thư viện từ B |
| `docs/Slide.pptx` | `BaoCao.docx` và ảnh chụp giao diện từ ứng dụng chạy thật |
| `build.bat` | `main.py`, `config.py` (nhánh `sys.frozen`), `requirements.txt`; thư mục `data/` cần kèm theo khi đóng gói |
| `README.md` | Cây thư mục, `install_guide.md`, README của 4 thành viên |

---

## 4. Bảng phụ thuộc: file nào cần lấy gì từ file / class nào để chạy khớp nhau

| File của D | Lấy từ file | Class / hàm / hằng số cụ thể | Dùng để làm gì |
|---|---|---|---|
| `exam_repository.py` | `base_models.py` (A) | `Exam`, `ExamResult`, `to_dict`, `from_dict` | Chuyển đối tượng ↔ dict để lưu JSON |
| | `json_file_handler.py` (A) | `JsonFileHandler` | Đọc/ghi `exams.json`, `results.json` an toàn |
| | `config.py` (A) | `EXAMS_FILE`, `RESULTS_FILE` | Đường dẫn file |
| | `data_repository.py` (A) | Tham số `usage_checker` của `JsonDataRepository` | A truyền `is_question_used` vào để chặn/cảnh báo xóa câu hỏi đã nằm trong đề; D chỉ cung cấp hàm, không import `data_repository` để tránh import vòng |
| `exam_exporter.py` | `base_models.py` (A) | ABC `ExamExporter`; `Exam`, `Question`, `Option` | Kế thừa ABC, dựng nội dung đề |
| | `data_repository.py` (A) | `JsonDataRepository.get_question` | Lấy câu hỏi theo `question_ids` |
| | `config.py` (A) | `EXPORT_DIR` | Nơi lưu file xuất |
| `sample_data.py` | `data_repository.py` (A) | `JsonDataRepository.add_subject`, `add_topic`, `add_question`, `list_subjects` | Nạp dữ liệu mẫu; kiểm tra dữ liệu đã có chưa |
| | `base_models.py` (A) | `Subject`, `Topic`, `Question`, `Option`, `DifficultyLevel` | Dựng đối tượng mẫu |
| | `auth.py` (B) | Hàm đăng ký | Tạo tài khoản quản trị mặc định |
| | `config.py` (A) | Đường dẫn dữ liệu | Biết file nào cần tạo lại |
| `gui/login_window.py` | `auth.py` (B) | `register`, `login` (tên chốt với B) | Xử lý đăng nhập và đăng ký |
| | `base_models.py` (A) | `User`, `Admin` | Nhận về đối tượng người dùng và vai trò |
| | `config.py` (A) | Hằng số GUI | Giao diện thống nhất |
| | `main.py`, `gui/app.py` (A) | Hàm/callback mở cửa sổ chính | Chuyển sang `app.py` sau khi đăng nhập thành công |
| `gui/stats_tab.py` | `grader.py` (C) | `Grader.topic_statistics` | Lấy số liệu đúng/tổng/phần trăm theo chủ đề |
| | `exam_repository.py` (D) | Hàm đọc danh sách kết quả | Chọn bài làm cần xem |
| | `data_repository.py` (A) | `get_topic` | Đổi `topic_id` thành tên chủ đề để hiển thị |
| | `gui/bar_chart.py` (D) | `BarChart` | Vẽ biểu đồ |
| `gui/bar_chart.py` | `config.py` (A) | Hằng số màu, font | Thống nhất giao diện |
| | `gui/stats_tab.py` (D) | Dữ liệu `{nhãn: giá trị}` truyền vào | Vẽ cột; widget không phụ thuộc nghiệp vụ |
| `build.bat` | `main.py`, `config.py` (A) | Nhánh `sys.frozen`, đường dẫn dữ liệu | Đảm bảo file `.exe` tìm đúng thư mục `data/` |
| | `requirements.txt` (A) | Danh sách thư viện | Cài trước khi đóng gói |
| `docs/testing.md` | `tests/` của A, B, C | Kết quả chạy từng test | Điền bảng đầu vào, kết quả mong đợi, kết quả thực tế, trạng thái |
| `docs/class_design.md` | Tất cả file `.py` nghiệp vụ | Tên lớp, thuộc tính, phương thức | Bảng mô tả lớp và sơ đồ lớp |
| `docs/references.md` | README và danh sách nguồn của A, B, C | Thư viện, API, mã tham khảo, khai báo dùng công cụ AI | Tổng hợp một nơi để ghi vào báo cáo |

**Điểm phải chốt với nhóm trước khi viết code:**

1. **Tên hàm của `exam_repository.py`** (đề xuất: `save_exam`, `get_exam`, `list_exams`, `save_result`, `list_results`, `list_results_by_exam`) để C và `stats_tab.py` gọi đúng.
2. **Định dạng file xuất.** Docstring của `ExamExporter` nhắc `.docx/.pdf`, nhưng quy định chỉ yêu cầu văn bản, CSV hoặc JSON. Đề xuất chọn `.txt` (hoặc thêm CSV) để không phải đóng gói thêm thư viện.
3. **Cấu trúc `topic_stats`** (dict `{topic_id: {correct, total, percent}}`) đã chốt với C, để `stats_tab.py` đọc đúng.
4. **Tài khoản quản trị mặc định.** Quy định cấm mã nguồn chứa thông tin nhạy cảm, nên `sample_data.py` chỉ tạo tài khoản mặc định qua `auth.py` (lưu mật khẩu đã băm), mật khẩu ban đầu ghi trong `install_guide.md` và yêu cầu đổi sau lần đăng nhập đầu.
5. **Ai viết test cho phần của D.** Cây thư mục hiện chưa có file test của D; nếu bổ sung, cập nhật lại cây và `docs/testing.md`.
6. **Cách chặn xóa câu hỏi đã nằm trong đề.** D cung cấp `is_question_used(question_id)`; A truyền hàm này vào `JsonDataRepository` khi khởi tạo trong `app.py` (tránh import vòng giữa hai repository).
7. **Lịch chạy thử trên ≥ 2 máy hoặc 2 tài khoản** và hạn các thành viên gửi nguồn tham khảo cho D, để kịp hoàn thiện báo cáo trước Buổi 14.

---

## 5. Thứ tự làm đề xuất

1. `exam_repository.py` (C cần ngay), sau đó `exam_exporter.py`.
2. `sample_data.py` (cần `auth.py` của B để tạo tài khoản mặc định) rồi `gui/login_window.py`.
3. `gui/bar_chart.py`, rồi `gui/stats_tab.py` khi C đã có `topic_statistics`.
4. Tài liệu trong `docs/` viết dần theo tiến độ (phân tích và thiết kế lớp từ sớm, kiểm thử và hướng dẫn sử dụng ở cuối).
5. `build.bat`, đóng gói và kiểm tra trên máy khác trước hạn nộp (Buổi 14); chạy thử trên ≥ 2 máy hoặc 2 tài khoản và ghi vào `docs/testing.md`.
6. `docs/references.md`, `BaoCao.docx`, `BaoCao.pdf`, `Slide.pptx` sau khi sản phẩm ổn định; in quyển báo cáo; trình chiếu và demo ở Buổi 15.

## 6. Phụ thuộc với thành viên khác

- **A:** cần `JsonFileHandler`, `to_dict`/`from_dict`, `config.py` trước khi làm `exam_repository.py`; `main.py` và `app.py` gọi `login_window.py` và `sample_data.py`.
- **B:** `login_window.py` và `sample_data.py` gọi `auth.py`; `docs/` ghi nguồn API từ `api_import.py`.
- **C:** `exam_generator.py` và `grader.py` gọi `exam_repository.py`; `stats_tab.py` dùng `topic_statistics`; `exam_tab.py` gọi `ExamExporter`.
- **Cả nhóm:** mọi thành viên gửi cho D bảng kiểm thử, mô tả lớp, danh sách nguồn tham khảo và khai báo công cụ AI đã dùng của phần mình; cùng chạy thử ứng dụng trên máy/tài khoản của mình.
