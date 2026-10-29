"""
Module: grading_engine.py
Phụ trách: Cài đặt logic chấm điểm cho cả 2 Chế độ:
  - Chế độ 1: Full trắc nghiệm 4 lựa chọn (chia đều điểm)
  - Chế độ 2: Đề chuẩn Tốt nghiệp THPT mới BGD&ĐT (3 Phần: P1 0.25đ/câu, P2 lũy tiến, P3 0.5đ/câu)
"""

from typing import Dict, Any, Tuple


def grade_full_mcq(
    student_answers: Dict[Any, Any], 
    answer_key: Dict[Any, Any], 
    max_score: float = 10.0
) -> Dict[str, Any]:
    """
    Chấm điểm Chế độ 1: Full trắc nghiệm 4 lựa chọn (A, B, C, D)
    """
    total_questions = len(answer_key) if answer_key else 40
    if total_questions == 0:
        total_questions = 40

    correct_count = 0
    wrong_count = 0
    blank_count = 0
    details = {}

    for q_num, correct_ans in answer_key.items():
        q_key = int(q_num) if str(q_num).isdigit() else q_num
        st_ans = student_answers.get(q_key) or student_answers.get(str(q_key))
        
        # Chuẩn hóa
        correct_ans_str = str(correct_ans).strip().upper() if correct_ans else ""
        st_ans_str = str(st_ans).strip().upper() if st_ans else ""

        if not st_ans_str:
            blank_count += 1
            is_correct = False
        elif st_ans_str == correct_ans_str:
            correct_count += 1
            is_correct = True
        else:
            wrong_count += 1
            is_correct = False

        details[q_key] = {
            "student": st_ans_str,
            "key": correct_ans_str,
            "is_correct": is_correct
        }

    score = round((correct_count / total_questions) * max_score, 2)

    return {
        "score": score,
        "correct_count": correct_count,
        "wrong_count": wrong_count,
        "blank_count": blank_count,
        "total_questions": total_questions,
        "details": details
    }


def normalize_numeric_string(val_str: Any) -> str:
    """
    Chuẩn hóa chuỗi số học để so khớp Phần III (ví dụ: '1,5' -> '1.5', '015' -> '15')
    """
    if val_str is None:
        return ""
    s = str(val_str).strip().replace(',', '.')
    try:
        f = float(s)
        # Nếu là số nguyên (ví dụ 15.0) -> '15'
        if f.is_integer():
            return str(int(f))
        return str(f)
    except ValueError:
        return s


def grade_thpt_2025(
    student_data: Dict[str, Any], 
    answer_key: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Chấm điểm Chế độ 2: Đề chuẩn Tốt nghiệp THPT mới của Bộ GD&ĐT (3 Phần)
    - student_data: {"part1": {...}, "part2": {...}, "part3": {...}}
    - answer_key:   {"part1": {...}, "part2": {...}, "part3": {...}}
    """
    # -------------------------------------------------------------
    # 1. Chấm PHẦN I (12 câu - mỗi câu 0.25đ, tối đa 3.0đ)
    # -------------------------------------------------------------
    key_p1 = answer_key.get("part1", {})
    st_p1 = student_data.get("part1", {})
    p1_correct = 0
    p1_details = {}

    for q_num, correct_ans in key_p1.items():
        q_key = int(q_num) if str(q_num).isdigit() else q_num
        st_ans = st_p1.get(q_key) or st_p1.get(str(q_key))
        c_str = str(correct_ans).strip().upper() if correct_ans else ""
        s_str = str(st_ans).strip().upper() if st_ans else ""

        is_c = (s_str == c_str and bool(s_str))
        if is_c:
            p1_correct += 1

        p1_details[q_key] = {"student": s_str, "key": c_str, "is_correct": is_c}

    score_p1 = round(p1_correct * 0.25, 2)

    # -------------------------------------------------------------
    # 2. Chấm PHẦN II (4 câu - Quy chế tính điểm lũy tiến, tối đa 4.0đ)
    #    1 ý đúng: 0.1đ | 2 ý đúng: 0.25đ | 3 ý đúng: 0.5đ | 4 ý đúng: 1.0đ
    # -------------------------------------------------------------
    key_p2 = answer_key.get("part2", {})
    st_p2 = student_data.get("part2", {})
    score_p2 = 0.0
    p2_details = {}

    progression_table = {
        0: 0.0,
        1: 0.1,
        2: 0.25,
        3: 0.5,
        4: 1.0
    }

    for q_num, key_subs in key_p2.items():
        q_key = int(q_num) if str(q_num).isdigit() else q_num
        st_subs = st_p2.get(q_key) or st_p2.get(str(q_key)) or {}

        correct_sub_count = 0
        sub_details = {}

        for sub in ['a', 'b', 'c', 'd']:
            k_val = str(key_subs.get(sub, "")).strip().upper()
            s_val = str(st_subs.get(sub, "")).strip().upper()

            # Chuẩn hóa Đ/S
            k_std = "Đ" if k_val in {"Đ", "D", "T"} else ("S" if k_val in {"S", "F"} else "")
            s_std = "Đ" if s_val in {"Đ", "D", "T"} else ("S" if s_val in {"S", "F"} else "")

            is_sub_c = (k_std == s_std and bool(s_std))
            if is_sub_c:
                correct_sub_count += 1

            sub_details[sub] = {"student": s_std, "key": k_std, "is_correct": is_sub_c}

        q_score = progression_table.get(correct_sub_count, 0.0)
        score_p2 += q_score
        p2_details[q_key] = {
            "correct_subs": correct_sub_count,
            "score": q_score,
            "sub_items": sub_details
        }

    score_p2 = round(score_p2, 2)

    # -------------------------------------------------------------
    # 3. Chấm PHẦN III (6 câu - mỗi câu 0.5đ, tối đa 3.0đ)
    # -------------------------------------------------------------
    key_p3 = answer_key.get("part3", {})
    st_p3 = student_data.get("part3", {})
    p3_correct = 0
    p3_details = {}

    for q_num, correct_val in key_p3.items():
        q_key = int(q_num) if str(q_num).isdigit() else q_num
        st_val = st_p3.get(q_key) or st_p3.get(str(q_key))

        k_norm = normalize_numeric_string(correct_val)
        s_norm = normalize_numeric_string(st_val)

        is_c = (k_norm == s_norm and bool(s_norm))
        if is_c:
            p3_correct += 1

        p3_details[q_key] = {"student": s_norm, "key": k_norm, "is_correct": is_c}

    score_p3 = round(p3_correct * 0.5, 2)

    total_score = round(score_p1 + score_p2 + score_p3, 2)

    return {
        "score_part1": score_p1,
        "score_part2": score_p2,
        "score_part3": score_p3,
        "total_score": total_score,
        "p1_correct": p1_correct,
        "p3_correct": p3_correct,
        "details_p1": p1_details,
        "details_p2": p2_details,
        "details_p3": p3_details
    }
