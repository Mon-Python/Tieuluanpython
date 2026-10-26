# Hướng dẫn Git Workflow — Đồ án Hệ thống quản lý ngân hàng câu hỏi

## 1. Cấu trúc nhánh (branch)

| Nhánh | Vai trò | Ai push trực tiếp |
|---|---|---|
| `main` | Code ổn định, đã chạy được | Không ai push trực tiếp — chỉ merge qua Pull Request |
| `feature/data-models` | A – Class design, CRUD, đọc/ghi JSON/CSV | A |
| `feature/exam-generator` | B – Tạo đề bằng `sample()`, trộn seed | B |
| `feature/question-ui` | C – Treeview, Text nội dung, QuestionEditor | C |
| `feature/exam-ui` | D – Form tạo đề, chấm điểm, Canvas, xuất file | D |

## 2. Thiết lập ban đầu (mỗi người làm 1 lần)

```bash
# Clone repo về máy
git clone <link-repo-github>
cd question_bank_app

# Cấu hình danh tính (nếu chưa từng làm)
git config user.name "Tên bạn"
git config user.email "email-github-cua-ban@example.com"

# Tạo nhánh riêng từ main
git checkout main
git pull origin main
git checkout -b feature/ten-nhanh-cua-ban
```

## 3. Quy trình làm việc hằng ngày

```bash
# Trước khi bắt đầu code mỗi buổi, cập nhật main mới nhất
git checkout main
git pull origin main
git checkout feature/ten-nhanh-cua-ban
git merge main          # đưa code mới nhất từ main vào nhánh mình

# Sau khi code xong 1 phần việc nhỏ
git add .
git commit -m "Mô tả ngắn gọn việc vừa làm"
git push origin feature/ten-nhanh-cua-ban
```

**Quy ước đặt tên commit:** mô tả rõ hành động, ví dụ:
- `"Thêm class Question và Exam"`
- `"Hoàn thiện CRUD đọc/ghi JSON"`
- `"Sửa lỗi trộn câu hỏi khi seed = None"`

## 4. Gửi Pull Request (PR) để merge vào `main`

1. Push nhánh của mình lên GitHub.
2. Vào GitHub → tab **Pull Requests** → **New Pull Request**.
3. Chọn: base = `main`, compare = `feature/ten-nhanh-cua-ban`.
4. Viết mô tả ngắn: đã làm gì, có phụ thuộc file nào của người khác không.
5. Nhờ 1 thành viên khác (không phải người tự merge) review trước khi bấm **Merge**.

## 5. Nguyên tắc tránh xung đột (conflict)

- Mỗi người chỉ sửa file thuộc phạm vi được phân công (xem bảng phân công module).
- **A hoàn thành và push `models.py` sớm nhất** (buổi đầu tiên) để B, C, D pull về dùng chung cấu trúc class ngay từ đầu — tránh mỗi người tự định nghĩa `Question` khác nhau.
- Nếu cần sửa file không thuộc phần mình (VD: `main.py` để ghép giao diện) → báo nhóm trước trong group chat, tránh 2 người sửa cùng lúc.
- Trước khi tạo PR, luôn `git merge main` vào nhánh mình để phát hiện conflict sớm, dễ xử lý hơn là để dồn đến cuối.

## 6. Nếu gặp conflict khi merge

```bash
git merge main
# Nếu báo CONFLICT, mở file bị conflict, tìm đoạn:
# <<<<<<< HEAD
# (code của bạn)
# =======
# (code từ main)
# >>>>>>> main
# Sửa lại cho đúng ý, xóa các dấu <<<<<<<, =======, >>>>>>>
git add .
git commit -m "Giải quyết conflict giữa X và Y"
git push origin feature/ten-nhanh-cua-ban
```

## 7. Người phụ trách tích hợp cuối cùng

Thành viên **A** đảm nhận:
- Tạo/hoàn thiện `main.py` ghép các view từ B, C, D lại.
- Review và duyệt Pull Request trước khi merge vào `main`.
- Kiểm tra ứng dụng chạy ổn định sau mỗi lần merge lớn.

## 8. Lịch mốc đề xuất

| Mốc | Nội dung |
|---|---|
| Tuần 1 | A push xong `models.py` + `data_manager.py` cơ bản; cả nhóm thống nhất interface contract |
| Tuần 2–3 | B, C, D code song song trên nhánh riêng, push thường xuyên |
| Tuần 4 | Gửi PR, review chéo, merge từng nhánh vào `main` |
| Tuần 5 | A tích hợp `main.py`, cả nhóm kiểm thử chung, sửa lỗi phát sinh |
| Tuần 6 | Hoàn thiện tài liệu (báo cáo, thiết kế lớp, kiểm thử, hướng dẫn sử dụng) |
