"""
Module: storage_manager.py
Phụ trách: Quản lý lưu trữ thông tin Bài kiểm tra và Bài làm (dạng JSON)
"""

import os
import json
from typing import List, Optional, Dict
from core.models import Exam, Submission, ExamMode


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EXAMS_FILE = os.path.join(DATA_DIR, "exams.json")


def set_data_dir(custom_path: str):
    """Cho phép tùy biến thư mục lưu dữ liệu theo cấu hình người dùng"""
    global DATA_DIR, EXAMS_FILE
    DATA_DIR = os.path.abspath(custom_path)
    EXAMS_FILE = os.path.join(DATA_DIR, "exams.json")
    ensure_data_dir()


def get_data_dir() -> str:
    """Lấy đường dẫn thư mục dữ liệu hiện tại"""
    return DATA_DIR


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
    except json.JSONDecodeError as jde:
        print(f"[CẢNH BÁO] File exams.json bị lỗi cấu trúc: {jde}")
        # Sao lưu file hỏng để tránh mất dữ liệu hoàn toàn
        backup_path = EXAMS_FILE + ".bak"
        try:
            import shutil
            shutil.copyfile(EXAMS_FILE, backup_path)
            print(f"Đã sao lưu file lỗi sang: {backup_path}")
        except Exception:
            pass
        return []
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
