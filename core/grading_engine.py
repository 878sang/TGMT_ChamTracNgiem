"""
Module: grading_engine.py
Chức năng 5: Chấm điểm tự động linh hoạt theo số lượng câu hỏi (20, 40, 50 câu).
- Thang điểm 10.0 (Mỗi câu = 10.0 / total_questions)
- So sánh chi tiết từng câu: Đúng, Sai, Bỏ trống, Tô trùng
- Xếp loại học lực
- Phân tích chuỗi đáp án nhập nhanh và tạo đáp án mẫu theo số câu
"""

from typing import Dict, Any, Tuple, Optional
import re


def grade_submission(
    student_answers: Dict[int, Any], 
    answer_key: Dict[int, str], 
    max_score: float = 10.0,
    total_questions: Optional[int] = None
) -> Dict[str, Any]:
    """
    So sánh đáp án của học sinh với đáp án chuẩn.
    Hỗ trợ linh hoạt số câu hỏi (20, 40, 50 câu).
    """
    num_q = total_questions or len(answer_key) or 50
    correct_count = 0
    wrong_count = 0
    blank_count = 0
    multiple_count = 0
    details = {}

    for q_num in range(1, num_q + 1):
        correct_ans = str(answer_key.get(q_num, "")).strip().upper()
        st_ans = student_answers.get(q_num)

        # 1. Bỏ trống
        if st_ans is None or st_ans == "":
            blank_count += 1
            is_correct = False
            disp_st = "Trống"

        # 2. Tô nhiều ô
        elif isinstance(st_ans, (list, tuple)):
            multiple_count += 1
            wrong_count += 1
            is_correct = False
            disp_st = ",".join(st_ans)

        # 3. Tô 1 ô
        else:
            disp_st = str(st_ans).strip().upper()
            if disp_st == correct_ans and correct_ans:
                correct_count += 1
                is_correct = True
            else:
                wrong_count += 1
                is_correct = False

        details[q_num] = {
            "student": disp_st,
            "key": correct_ans,
            "is_correct": is_correct
        }

    # Tính điểm: (số câu đúng / tổng số câu) * 10.0
    score = round((correct_count / max(num_q, 1)) * max_score, 2)

    # Xếp loại học lực
    if score >= 8.0:
        rank = "Giỏi"
    elif score >= 6.5:
        rank = "Khá"
    elif score >= 5.0:
        rank = "Trung bình"
    else:
        rank = "Yếu"

    return {
        "score": score,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "blank_count": blank_count,
        "multiple_count": multiple_count,
        "total_questions": num_q,
        "details": details,
        "rank": rank
    }


def parse_answer_string(text: str, max_q: int = 50) -> Dict[int, str]:
    """Chuyển đổi chuỗi đáp án người dùng nhập sang dictionary {1: 'A', 2: 'B', ...}"""
    clean_text = text.strip()
    result = {}

    # Định dạng "1:A" hoặc "1A"
    indexed_matches = re.findall(r'(\d+)\s*[:\.\-]?\s*([A-Da-d])', clean_text)
    if indexed_matches and len(indexed_matches) >= 3:
        for num_str, opt in indexed_matches:
            q_num = int(num_str)
            if 1 <= q_num <= max_q:
                result[q_num] = opt.upper()
        return result

    # Định dạng chuỗi liên tiếp hoặc cách nhau: "ABCD..." hoặc "A B C D..."
    letters = re.findall(r'[A-Da-d]', clean_text)
    for idx, letter in enumerate(letters[:max_q]):
        result[idx + 1] = letter.upper()

    return result


def generate_sample_answer_key(num_questions: int = 50) -> Dict[int, str]:
    """Tạo bộ đáp án chuẩn mẫu cho N câu hỏi"""
    return {i: ['A', 'B', 'C', 'D'][(i * 3 + 1) % 4] for i in range(1, num_questions + 1)}
