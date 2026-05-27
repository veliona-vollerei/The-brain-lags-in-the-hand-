# king_vietnamese_questions.py
import random
import unicodedata

# Dữ liệu câu hỏi: (các chữ cái gợi ý, đáp án có dấu, gợi ý loại từ)
QUESTIONS = [
    {"clues": "c/ọ/ồ/l/n", "answer": "LỌ CỒN", "hint": "Danh từ (đồ dùng)"},
    {"clues": "c/á/c/h/u/ố/i", "answer": "CÁ CHUỐI", "hint": "Động vật"},
    {"clues": "h/à/n/g/x/ó/l/m/ồ/n", "answer": "HỒN XÓM LÀNG", "hint": "Tập thể"},
    {"clues": "t/o/à/đ/n/ụ", "answer": "ĐOÀN TỤ", "hint": "Hành động"},
    {"clues": "l/ồ/c/n/ậ/u", "answer": "CỒN LẬU", "hint": "Địa danh"},
    {"clues": "h/ấ/t/c/ứ/t/đ", "answer": "THẤT ĐỨC", "hint": "Phẩm chất"},
    {"clues": "v/ư/ợ/t/b/ậ/c", "answer": "VƯỢT BẬC", "hint": "Tính từ"},
    {"clues": "c/ứ/c/m/ó/t", "answer": "MỨT CÓC", "hint": "Món ăn"},
    {"clues": "c/h/ị/h/c/t/ủ", "answer": "CHỦ TỊCH", "hint": "Chức vụ"},
    {"clues": "n/ệ/n/ả/h/đ/i", "answer": "ĐIỆN ẢNH", "hint": "Lĩnh vực nghệ thuật"},
    {"clues": "s/ú/c/c/ố", "answer": "CÚ SỐC", "hint": "Cảm xúc"},
]

def remove_diacritics(text):
    """Chuyển chữ có dấu thành không dấu, viết hoa"""
    text = text.upper()
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def get_random_question():
    q = random.choice(QUESTIONS)
    return {
        "clues": q["clues"],
        "answer_diacritic": q["answer"],
        "answer_nodiacritic": remove_diacritics(q["answer"]),
        "hint": q["hint"]
    }