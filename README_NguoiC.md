# README – Thành viên C: Tạo đề, chấm điểm và làm bài

**Đồ án:** Đề tài 7 – Hệ thống quản lý ngân hàng câu hỏi (Python, Tkinter, JSON)
**Vai trò:** C – phụ trách nghiệp vụ cốt lõi của đề tài: sinh đề theo ma trận mức độ (có seed), chấm điểm, thống kê theo chủ đề và giao diện tạo đề / làm bài.
**Phụ thuộc vào A:** `base_models.py` (các ABC `ExamGenerator`, `Grader` đã định nghĩa sẵn), `data_repository.py`. **Phụ thuộc vào D:** `exam_repository.py` để lưu đề và kết quả.

---

## 1. Nội dung chính của người làm

- Viết `exam_generator.py`: lớp `ExamGenerator` (implement ABC trong `base_models.py`) tạo đề theo ma trận bằng `rng.sample()`, trộn thứ tự câu và phương án bằng `random.Random(seed)` riêng cho từng lần tạo, hỗ trợ tái lập đề (`rebuild_exam`).
- Kiểm tra đủ số câu theo ma trận (gọi `count_questions`) trước khi `sample()`, báo lỗi rõ ràng khi thiếu.
- Viết `grader.py`: lớp `Grader` (implement ABC) chấm điểm bài làm và thống kê đúng/tổng/phần trăm theo chủ đề.
- Xây dựng `gui/exam_tab.py`: form tạo đề (chọn môn, nhập ma trận theo chủ đề và mức độ, nhập seed, đặt tên đề), Treeview ma trận, nút Tạo đề / Tái lập đề / Xuất đề.
- Xây dựng `gui/take_exam_window.py` (file mới): cửa sổ làm bài, hiển thị từng câu theo thứ tự đã trộn, chọn đáp án, nộp bài, chấm và hiện kết quả.
- Trong `take_exam_window.py`: hộp thoại xác nhận trước khi nộp bài (cảnh báo còn câu chưa trả lời) và khi đóng cửa sổ giữa chừng.
- Trong `exam_tab.py`: Quản trị viên thấy form Tạo / Tái lập / Xuất đề; người dùng thường chỉ thấy danh sách đề và nút Làm bài (dùng `User.can(...)` của A).
- Gửi D danh sách nguồn thư viện, mã tham khảo và việc có dùng công cụ AI của phần mình để D ghi vào `docs/references.md`.
- Viết kiểm thử: `test_exam_generator.py` (gồm kiểm thử tái lập theo seed) và `test_grader.py`.
- Chốt với A và D: định dạng `exams.json` / `results.json`, cấu trúc `topic_stats`, hàm lưu đề và kết quả trong `exam_repository.py`.

---

## 2. File cần tạo / chỉnh sửa và mục đích chính

| File | Mục đích chính |
|---|---|
| `exam_generator.py` | Sinh đề theo ma trận mức độ bằng `sample()`; trộn câu và phương án theo seed; tái lập đề từ seed đã lưu |
| `grader.py` | Chấm bài làm của học sinh, tính điểm, thống kê đúng/tổng/phần trăm theo chủ đề |
| `gui/exam_tab.py` | Tab tạo đề: form ma trận, nhập seed, danh sách đề đã tạo, nút Tạo / Tái lập / Mở làm bài |
| `gui/take_exam_window.py` | Cửa sổ làm bài: hiển thị câu hỏi, chọn đáp án, nộp bài, chấm điểm, xem kết quả; xác nhận trước khi nộp và khi đóng cửa sổ giữa chừng |
| `tests/test_exam_generator.py` | Kiểm thử sinh đề: đủ/thiếu câu, ma trận rỗng, số câu bằng 0 hoặc âm, cùng seed ra cùng đề, khác seed ra đề khác |
| `tests/test_grader.py` | Kiểm thử chấm điểm: đúng hết, sai hết, bỏ trống, đúng một phần, thống kê theo chủ đề, bài rỗng (tránh chia cho 0) |

---

## 3. Nguồn nội dung của từng file

| File | Nội dung lấy từ đâu |
|---|---|
| `exam_generator.py` | Đề tài 7 trong quy định (ma trận mức độ bằng `sample()`, trộn câu/phương án với seed, tái lập đề); docstring của ABC `ExamGenerator` trong `base_models.py` (dùng `random.Random(seed)` riêng, không dùng `random.seed()` toàn cục); `count_questions` trong `data_repository.py` |
| `grader.py` | ABC `Grader` trong `base_models.py` (kiểu tham số và giá trị trả về); Đề tài 7 (chấm điểm, thống kê theo chủ đề); mục VII.6 (chia cho 0) |
| `gui/exam_tab.py` | Đề tài 7 (form tạo đề, Treeview); mục 6 của quy định (widget, Layout Manager, không trộn `pack()` và `grid()`); `get_question_bank_summary` trong `data_repository.py` để biết chủ đề nào thiếu câu |
| `gui/take_exam_window.py` | Mục 6 của quy định (Radiobutton, Messagebox xác nhận khi nộp bài); `Exam`, `StudentAnswer`, `ExamResult` trong `base_models.py`; vai trò/tên người dùng từ `gui/app.py` (A) |
| `tests/test_exam_generator.py` | Mục 9 của quy định (≥ 10 trường hợp, có trường hợp biên); hành vi của `exam_generator.py` |
| `tests/test_grader.py` | Mục 9 của quy định; hành vi của `grader.py` |

---

## 4. Bảng phụ thuộc: file nào cần lấy gì từ file / class nào để chạy khớp nhau

| File của C | Lấy từ file | Class / hàm / hằng số cụ thể | Dùng để làm gì |
|---|---|---|---|
| `exam_generator.py` | `base_models.py` (A) | ABC `ExamGenerator`; `ExamMatrixItem`, `Exam`, `Question`, `Option`, `DifficultyLevel` | Kế thừa ABC, nhận ma trận, trả về `Exam` |
| | `data_repository.py` (A) | `JsonDataRepository.count_questions`, `list_questions` | Kiểm tra đủ câu trước khi `sample()` và lấy câu hỏi ứng viên |
| | `exam_repository.py` (D) | Hàm lưu đề (tên chốt với D) | Lưu `Exam` vào `exams.json` |
| `grader.py` | `base_models.py` (A) | ABC `Grader`; `Exam`, `Question`, `StudentAnswer`, `ExamResult` | Kế thừa ABC, nhận đề, câu hỏi và đáp án, trả về `ExamResult` |
| | `exam_repository.py` (D) | Hàm lưu kết quả | Lưu `ExamResult` vào `results.json` |
| `gui/exam_tab.py` | `exam_generator.py` (C) | `ExamGenerator.generate_exam`, `rebuild_exam` | Nút Tạo đề / Tái lập đề |
| | `data_repository.py` (A) | `list_subjects`, `list_topics`, `get_question_bank_summary` | Combobox môn, danh sách chủ đề, hiển thị số câu còn có |
| | `exam_repository.py` (D) | Hàm đọc danh sách đề | Treeview các đề đã tạo |
| | `exam_exporter.py` (D) | `ExamExporter.export_exam`, `export_answer_key` | Nút Xuất đề và đáp án |
| | `gui/take_exam_window.py` (C) | `TakeExamWindow` | Nút Làm bài mở cửa sổ làm bài |
| | `config.py`, `gui/app.py`, `base_models.py` (A) | Hằng số GUI; instance repository dùng chung; `User.can("create_exam")`, `User.can("export_exam")` | Giao diện thống nhất; nhận repository từ `app.py`; chỉ Quản trị viên thấy form Tạo / Tái lập / Xuất đề, người dùng thường chỉ thấy danh sách đề và nút Làm bài |
| `gui/take_exam_window.py` | `grader.py` (C) | `Grader.grade` | Chấm khi nộp bài |
| | `exam_repository.py` (D) | Hàm đọc đề, lưu kết quả | Tải đề đã tạo, lưu kết quả sau khi chấm |
| | `data_repository.py` (A) | `get_question` | Lấy nội dung câu hỏi theo `question_ids` của đề |
| | `base_models.py` (A) | `Exam.shuffled_options`, `StudentAnswer`, `ExamResult` | Hiển thị phương án theo thứ tự đã trộn và gói bài làm |
| | `gui/app.py` (A) | Tên người dùng đang đăng nhập (`User.username`) | Điền `student_name` cho `ExamResult` |
| | `gui/stats_tab.py`, `bar_chart.py` (D) | Kết quả của `topic_statistics` | D vẽ biểu đồ từ dữ liệu C trả về |
| `tests/test_exam_generator.py` | `exam_generator.py` (C), `data_repository.py` (A), `base_models.py` (A) | `ExamGenerator`, `JsonDataRepository`, `ExamMatrixItem` | Kiểm thử trên dữ liệu JSON tạm |
| `tests/test_grader.py` | `grader.py` (C), `base_models.py` (A) | `Grader`, `Exam`, `Question`, `Option`, `StudentAnswer` | Kiểm thử bằng dữ liệu dựng tay trong bộ nhớ |

**Điểm phải chốt với nhóm trước khi viết code:**

1. **Cấu trúc `topic_stats`.** `ExamResult` đang ghi chú `{topic_id: (đúng, tổng)}`, còn `Grader.topic_statistics` trả `{'correct', 'total', 'percent'}`. Nên thống nhất dùng dict ở cả hai nơi (tuple sẽ thành list khi lưu JSON) và báo D để vẽ biểu đồ.
2. **Dữ liệu cần để tái lập đề.** `Exam` hiện chỉ lưu `seed`, `question_ids`, `shuffled_options`, không lưu ma trận. Chọn một trong hai: nhờ A thêm trường `matrix` vào `Exam`, hoặc coi `rebuild_exam` là dựng lại đề từ `question_ids` và `shuffled_options` đã lưu cộng seed.
3. **Tên hàm lưu/đọc đề và kết quả** trong `exam_repository.py` của D.
4. **Một đáp án đúng mỗi câu.** `StudentAnswer.selected_option_ids` là list nhưng hệ thống chỉ có single choice; chốt quy ước (list có đúng 1 phần tử, hoặc rỗng nếu bỏ trống).

---

## 5. Thứ tự làm đề xuất

1. `exam_generator.py` và `tests/test_exam_generator.py` (cần `count_questions` của A, có sẵn).
2. `grader.py` và `tests/test_grader.py` (độc lập, chỉ cần `base_models.py`).
3. `gui/exam_tab.py` khi D đã có `exam_repository.py`.
4. `gui/take_exam_window.py` sau cùng.

## 6. Phụ thuộc với thành viên khác

- **A:** `app.py` nhúng `ExamTab` vào Notebook cho cả hai vai trò và truyền repository (`ExamTab` tự ẩn form tạo/xuất đề với người dùng thường); có thể phải thêm trường vào `Exam`.
- **B:** dùng chung `list_questions`, `DifficultyLevel`; hiển thị mức độ giống `question_tab.py`.
- **D:** `exam_repository.py` lưu đề và kết quả; `exam_exporter.py` xuất đề và đáp án; `stats_tab.py`, `bar_chart.py` dùng kết quả `topic_statistics`.
