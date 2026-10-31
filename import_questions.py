"""import_questions.py
===================
[B sở hữu] Đọc và nhập hàng loạt câu hỏi từ file văn bản (.txt) vào ngân hàng câu hỏi:
- Xử lý các trường hợp: file không tồn tại, file rỗng, dòng sai định dạng.
- Bỏ qua các dòng lỗi nhưng tiếp tục nạp các câu hợp lệ.
- Báo cáo chi tiết số lượng câu nạp thành công và danh sách dòng/câu bị lỗi.
- Lưu dữ liệu thông qua JsonDataRepository.add_questions.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

from base_models import DifficultyLevel, Option, Question
from data_repository import JsonDataRepository
from validators import validate_question


def parse_question_line(line: str, line_no: int,
                        default_topic_id: str = "") -> Tuple[Optional[Question], Optional[str]]:
    """
    Phân tích một dòng văn bản thành đối tượng Question.
    Định dạng hỗ trợ:
    1. topic_id|Nội dung|Mức độ (de/kho)|Phương án A|Phương án B|Phương án C|Phương án D|Đáp án đúng (A/B/C/D)
    2. Nội dung|Mức độ (de/kho)|Phương án A|Phương án B|Phương án C|Phương án D|Đáp án đúng (A/B/C/D) (dùng default_topic_id)
    """
    clean_line = line.strip()
    if not clean_line or clean_line.startswith("#"):
        return None, None  # Dòng trống hoặc chú thích, bỏ qua không báo lỗi

    parts = [p.strip() for p in clean_line.split("|")]
    
    if len(parts) == 8:
        topic_id, content, diff_str, opt_a, opt_b, opt_c, opt_d, correct_raw = parts
    elif len(parts) == 7:
        if not default_topic_id:
            return None, f"Dòng {line_no}: Thiếu mã chủ đề (topic_id) và chưa chọn chủ đề mặc định."
        topic_id = default_topic_id
        content, diff_str, opt_a, opt_b, opt_c, opt_d, correct_raw = parts
    else:
        return None, f"Dòng {line_no}: Sai định dạng ({len(parts)} trường). Yêu cầu 7 hoặc 8 trường cách nhau bởi ký tự '|'."

    # 1. Kiểm tra topic_id
    if not topic_id:
        return None, f"Dòng {line_no}: Mã chủ đề (topic_id) bị rỗng."

    # 2. Kiểm tra content
    if not content:
        return None, f"Dòng {line_no}: Nội dung câu hỏi bị rỗng."

    # 3. Kiểm tra difficulty
    diff_norm = diff_str.lower()
    if diff_norm in ("de", "dễ", "easy"):
        diff = DifficultyLevel.DE
    elif diff_norm in ("kho", "khó", "hard"):
        diff = DifficultyLevel.KHO
    else:
        return None, f"Dòng {line_no}: Mức độ '{diff_str}' không hợp lệ. Chỉ chấp nhận 'de' hoặc 'kho'."

    # 4. Kiểm tra 4 phương án
    option_texts = [opt_a, opt_b, opt_c, opt_d]
    for i, t in enumerate(option_texts):
        if not t:
            label = chr(ord('A') + i)
            return None, f"Dòng {line_no}: Phương án {label} bị để trống."

    # Kiểm tra trùng phương án
    normalized_opts = [t.lower() for t in option_texts]
    if len(set(normalized_opts)) != 4:
        return None, f"Dòng {line_no}: Các phương án câu hỏi bị trùng lặp nội dung."

    # 5. Xác định đáp án đúng
    correct_clean = correct_raw.strip().upper()
    valid_keys = {"A": 0, "B": 1, "C": 2, "D": 3, "1": 0, "2": 1, "3": 2, "4": 3}
    if correct_clean not in valid_keys:
        return None, f"Dòng {line_no}: Đáp án đúng '{correct_raw}' không hợp lệ. Hãy nhập A, B, C hoặc D."
    correct_idx = valid_keys[correct_clean]

    options = [Option.create(t, i == correct_idx) for i, t in enumerate(option_texts)]
    question = Question.create(topic_id, content, diff, options)
    
    ok, val_err = validate_question(question)
    if not ok:
        return None, f"Dòng {line_no}: {val_err}"

    return question, None


def import_questions_from_file(file_path: Union[str, Path],
                               repository: JsonDataRepository,
                               default_topic_id: str = "") -> Tuple[int, List[str]]:
    """
    Đọc câu hỏi từ file văn bản và thêm vào ngân hàng câu hỏi.
    - Xử lý file không tồn tại hoặc file rỗng.
    - Trả về tuple: (số câu thêm thành công, danh sách lỗi chi tiết).
    """
    p = Path(file_path)
    if not p.exists():
        return 0, [f"Lỗi: Không tìm thấy file dữ liệu tại đường dẫn '{file_path}'."]

    try:
        text = p.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return 0, [f"Lỗi: File '{p.name}' không phải định dạng văn bản UTF-8 hợp lệ."]
    except Exception as e:
        return 0, [f"Lỗi khi đọc file '{p.name}': {e}"]

    lines = text.splitlines()
    non_empty = [ln for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not non_empty:
        return 0, [f"Lỗi: File '{p.name}' rỗng hoặc không chứa dữ liệu câu hỏi nào."]

    questions_to_add: List[Question] = []
    parse_errors: List[str] = []

    for line_no, line in enumerate(lines, start=1):
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue

        q, err = parse_question_line(clean, line_no, default_topic_id)
        if err:
            parse_errors.append(err)
        elif q:
            questions_to_add.append(q)

    if not questions_to_add:
        return 0, parse_errors

    # Thêm câu hỏi qua JsonDataRepository.add_questions
    added_count, repo_errors = repository.add_questions(questions_to_add)
    all_errors = parse_errors + repo_errors

    return added_count, all_errors
