"""
Module: storage_manager.py
Phụ trách: Quản lý lưu trữ thông tin Bài kiểm tra và Bài làm (dạng JSON)
"""

import os
import json
from typing import List, Optional, Dict
from core.models import Exam, Submission, ExamMode


DATA_DIR = "d:/Thị giác máy tính/Đồ Án/data"
EXAMS_FILE = os.path.join(DATA_DIR, "exams.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(EXAMS_FILE):
        with open(EXAMS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def get_all_exams() -> List[Exam]:
    ensure_data_dir()
    try:
        with open(EXAMS_FILE, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
            return [Exam.from_dict(item) for item in raw_list]
    except Exception as e:
        print(f"Lỗi đọc danh sách bài kiểm tra: {e}")
        return []


def get_exam_by_id(exam_id: str) -> Optional[Exam]:
    exams = get_all_exams()
    for e in exams:
        if e.exam_id == exam_id:
            return e
    return None


def save_exam(exam: Exam) -> bool:
    ensure_data_dir()
    try:
        exams = get_all_exams()
        # Tìm xem đã tồn tại chưa để update, nếu chưa thì thêm mới
        found = False
        for idx, e in enumerate(exams):
            if e.exam_id == exam.exam_id:
                exams[idx] = exam
                found = True
                break
        if not found:
            exams.append(exam)

        with open(EXAMS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in exams], f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi lưu bài kiểm tra: {e}")
        return False


def delete_exam(exam_id: str) -> bool:
    ensure_data_dir()
    try:
        exams = get_all_exams()
        exams = [e for e in exams if e.exam_id != exam_id]
        with open(EXAMS_FILE, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in exams], f, ensure_ascii=False, indent=2)

        # Xóa file submission tương ứng nếu có
        sub_file = os.path.join(DATA_DIR, f"submissions_{exam_id}.json")
        if os.path.exists(sub_file):
            os.remove(sub_file)
        return True
    except Exception as e:
        print(f"Lỗi xóa bài kiểm tra: {e}")
        return False


def get_submissions(exam_id: str) -> List[Submission]:
    ensure_data_dir()
    sub_file = os.path.join(DATA_DIR, f"submissions_{exam_id}.json")
    if not os.path.exists(sub_file):
        return []
    try:
        with open(sub_file, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
            return [Submission.from_dict(item) for item in raw_list]
    except Exception as e:
        print(f"Lỗi đọc bài nộp: {e}")
        return []


def save_submissions(exam_id: str, submissions: List[Submission]) -> bool:
    ensure_data_dir()
    sub_file = os.path.join(DATA_DIR, f"submissions_{exam_id}.json")
    try:
        with open(sub_file, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in submissions], f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi lưu bài nộp: {e}")
        return False
