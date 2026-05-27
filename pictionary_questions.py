# pictionary_questions.py
import random
import os
import unicodedata

# Dữ liệu câu hỏi: ảnh và đáp án (có dấu)
QUESTIONS_DATA = [
    {"image": "gach_hoa.jpg", "answer": "GẠCH HOA"},
    {"image": "cong_trai.jpg", "answer": "CÔNG TRÁI"},
    {"image": "tay_trang.jpg", "answer": "TAY TRẮNG"},
    {"image": "bao_ham.jpg", "answer": "BAO HÀM"},
    {"image": "ca_ngua.jpg", "answer": "CÁ NGỰA"},
    {"image": "chan_tuong.jpg", "answer": "CHAN TƯỚNG"},
    {"image": "xe_tang.jpg", "answer": "XE TĂNG"},
    {"image": "bac_tinh.jpg", "answer": "BẠC TÌNH"},
    {"image": "bao_la.jpg", "answer": "BAO LA"},
    {"image": "bao_quat.jpg", "answer": "Bao QUÁT"},
    {"image": "tai_hoa.jpg", "answer": "TAI HỌA"},
    {"image": "ma_ca_rong.jpg", "answer": "MA CÀ RỒNG"},
    {"image": "co_bap.jpg", "answer": "CƠ BẮP"},
    {"image": "hai_long.jpg", "answer": "HÀI LÒNG"},
    {"image": "bao_thuc.jpg", "answer": "BÁO THỨC"},
    {"image": "mui_nhon.jpg", "answer": "MŨI NHỌN"},
    {"image": "ba_moi.jpg", "answer": "BÀ MỐI"},
    {"image": "trai_cay.jpg", "answer": "TRÁI CÂY"},
]

def remove_diacritics(text):
    """Chuyển chữ có dấu thành không dấu (viết hoa)"""
    text = text.upper()
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def get_random_question():
    """Trả về câu hỏi ngẫu nhiên với đường dẫn ảnh đầy đủ"""
    q = random.choice(QUESTIONS_DATA)
    # Đường dẫn ảnh trong thư mục backgrounds (có thể đặt trong assets/pictionary nếu muốn)
    image_path = os.path.join("nhin_hinh", q["image"])
    return {
        "image_path": image_path,
        "answer_diacritic": q["answer"],          # có dấu
        "answer_nodiacritic": remove_diacritics(q["answer"])  # không dấu, viết hoa
    }