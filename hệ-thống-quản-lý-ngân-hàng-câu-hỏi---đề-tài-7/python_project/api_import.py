"""api_import.py
=============
[B sở hữu] Lấy câu hỏi từ Web API bên ngoài (Open Trivia DB hoặc API tương đương):
- Sử dụng urllib.request (hoặc requests) với cấu hình timeout an toàn từ config.py.
- Xử lý đầy đủ ngoại lệ: kết nối mạng, timeout, HTTP lỗi, JSON sai định dạng.
- Làm sạch dữ liệu: giải mã ký tự HTML entities (ví dụ: &quot;, &#039;, &amp;).
- Chuẩn hóa về đúng 4 phương án trắc nghiệm (1 đáp án đúng, 3 đáp án sai, xáo trộn).
- Lưu kết quả thô vào API_QUESTIONS_FILE và thêm các câu hợp lệ vào JsonDataRepository.
"""

import html
import json
import random
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from base_models import DifficultyLevel, Option, Question
from config import API_QUESTIONS_FILE, API_TIMEOUT_SECONDS, API_URL
from data_repository import JsonDataRepository
from json_file_handler import JsonFileHandler
from validators import validate_question


def clean_html_text(text: str) -> str:
    """Giải mã các ký tự HTML entities thành văn bản thuần."""
    if not text:
        return ""
    # Giải mã hai lần phòng trường hợp double-escaped
    return html.unescape(html.unescape(str(text))).strip()


def fetch_questions_from_api(url: Optional[str] = None,
                             amount: int = 10,
                             category: Optional[int] = None,
                             difficulty: Optional[str] = None,
                             timeout: int = API_TIMEOUT_SECONDS) -> Tuple[List[dict], Optional[str]]:
    """
    Gửi request đến API lấy danh sách câu hỏi.
    Trả về: (danh sách câu hỏi thô từ API, thông báo lỗi nếu có).
    """
    target_url = url or API_URL

    # Bổ sung tham số truy vấn nếu dùng OpenTDB
    if "opentdb.com" in target_url:
        parsed = urllib.parse.urlparse(target_url)
        params = urllib.parse.parse_qs(parsed.query)
        params["amount"] = [str(amount)]
        params["type"] = ["multiple"]  # 4 phương án
        if category:
            params["category"] = [str(category)]
        if difficulty and difficulty in ("easy", "medium", "hard"):
            params["difficulty"] = [difficulty]
        new_query = urllib.parse.urlencode(params, doseq=True)
        target_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

    req = urllib.request.Request(
        target_url,
        headers={"User-Agent": "QuestionBankManager/1.0 (Student Python Project)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            if status != 200:
                return [], f"Máy chủ API trả về mã lỗi HTTP {status}."
            raw_data = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return [], f"Lỗi HTTP từ máy chủ API: {e.code} - {e.reason}."
    except urllib.error.URLError as e:
        return [], f"Không thể kết nối đến máy chủ API: {e.reason}. Vui lòng kiểm tra kết nối mạng Internet."
    except TimeoutError:
        return [], f"Kết nối đến API bị quá thời gian (timeout {timeout} giây). Vui lòng thử lại sau."
    except Exception as e:
        return [], f"Lỗi không xác định khi gọi API: {e}"

    try:
        payload = json.loads(raw_data)
    except json.JSONDecodeError as e:
        return [], f"Dữ liệu nhận từ API không phải JSON hợp lệ: {e}"

    # OpenTDB trả về: {"response_code": 0, "results": [...]}
    if isinstance(payload, dict) and "results" in payload:
        resp_code = payload.get("response_code", 0)
        if resp_code != 0:
            code_messages = {
                1: "Không đủ số lượng câu hỏi phù hợp với yêu cầu trên hệ thống API.",
                2: "Tham số truyền vào API không hợp lệ.",
                3: "Token phiên API không tìm thấy.",
                4: "Token phiên đã dùng hết câu hỏi."
            }
            return [], code_messages.get(resp_code, f"API thông báo lỗi response_code={resp_code}.")
        return payload["results"], None

    if isinstance(payload, list):
        return payload, None

    return [], "Cấu trúc dữ liệu phản hồi từ API không tương thích."


def transform_api_item_to_question(item: dict, topic_id: str,
                                   default_difficulty: DifficultyLevel = DifficultyLevel.DE) -> Optional[Question]:
    """
    Chuyển đổi một phần tử thô từ API thành đối tượng Question hợp lệ:
    - Làm sạch HTML entities.
    - Tạo 4 phương án trả lời (1 đáp án đúng, 3 đáp án sai).
    - Xáo trộn ngẫu nhiên thứ tự phương án.
    - Ánh xạ độ khó (easy -> de, hard/medium -> kho).
    """
    raw_question = item.get("question") or item.get("content") or ""
    content = clean_html_text(raw_question)
    if not content:
        return None

    correct_text = clean_html_text(item.get("correct_answer") or item.get("answer") or "")
    raw_incorrect = item.get("incorrect_answers") or item.get("wrong_answers") or []
    incorrect_texts = [clean_html_text(x) for x in raw_incorrect if clean_html_text(x)]

    if not correct_text or len(incorrect_texts) < 3:
        return None

    # Lấy đúng 3 phương án sai đầu tiên
    incorrect_texts = incorrect_texts[:3]

    # Kiểm tra không bị trùng với đáp án đúng
    if any(t.lower() == correct_text.lower() for t in incorrect_texts):
        return None

    # Tạo danh sách 4 phương án
    option_specs = [(correct_text, True)] + [(t, False) for t in incorrect_texts]
    random.shuffle(option_specs)

    options = [Option.create(content=t, is_correct=is_corr) for t, is_corr in option_specs]

    # Ánh xạ độ khó
    api_diff = str(item.get("difficulty", "")).lower()
    if api_diff == "hard":
        difficulty = DifficultyLevel.KHO
    elif api_diff == "easy":
        difficulty = DifficultyLevel.DE
    else:
        difficulty = default_difficulty

    question = Question.create(
        topic_id=topic_id,
        content=content,
        difficulty=difficulty,
        options=options
    )

    ok, _ = validate_question(question)
    return question if ok else None


def import_questions_from_api(topic_id: str,
                              repository: JsonDataRepository,
                              amount: int = 10,
                              category: Optional[int] = None,
                              difficulty: Optional[str] = None,
                              api_url: Optional[str] = None,
                              save_raw_file: Optional[Union[str, Path]] = None,
                              file_handler: Optional[JsonFileHandler] = None) -> Tuple[int, List[str]]:
    """
    Chức năng nghiệp vụ hoàn chỉnh nhập câu hỏi từ API:
    1. Gọi API lấy dữ liệu thô.
    2. Lưu bản sao thô vào file api_questions.json (phục vụ đối soát/báo cáo).
    3. Chuyển đổi và làm sạch từng câu hỏi.
    4. Thêm các câu hợp lệ vào JsonDataRepository.
    5. Báo cáo số lượng thành công và chi tiết các câu lỗi/bỏ qua.
    """
    if not topic_id:
        return 0, ["Vui lòng chọn một chủ đề trước khi nhập câu hỏi từ API."]

    raw_items, err = fetch_questions_from_api(
        url=api_url,
        amount=amount,
        category=category,
        difficulty=difficulty
    )

    if err:
        return 0, [err]

    if not raw_items:
        return 0, ["API không trả về câu hỏi nào."]

    # Lưu dữ liệu thô vào file
    handler = file_handler or JsonFileHandler()
    raw_file_path = save_raw_file or API_QUESTIONS_FILE
    try:
        handler.write(raw_file_path, raw_items)
    except Exception as e:
        # Không làm gián đoạn import nếu lưu file thô thất bại
        pass

    questions_to_add: List[Question] = []
    skipped_count = 0

    for idx, item in enumerate(raw_items, start=1):
        q = transform_api_item_to_question(item, topic_id=topic_id)
        if q:
            questions_to_add.append(q)
        else:
            skipped_count += 1

    if not questions_to_add:
        return 0, [f"Đã tải {len(raw_items)} câu từ API nhưng không có câu nào đủ 4 phương án hợp lệ."]

    added_count, repo_errors = repository.add_questions(questions_to_add)
    all_errors = repo_errors
    if skipped_count > 0:
        all_errors.append(f"Đã bỏ qua {skipped_count} câu từ API do không tương thích hoặc thiếu phương án.")

    return added_count, all_errors
