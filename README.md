# 🎤 THE BRAIN LAGS IN THE HAND – FNF GESTURE EDITION

**Friday Night Funkin'** kết hợp với điều khiển bằng cử chỉ tay qua AI – một trải nghiệm âm nhạc – hành động hoàn toàn mới.

---

## 📖 Giới thiệu
NĂM 2026...,xuất hiện 1 women làm điên đảo khắp thế giới. women phải lòng anh main (người chơi), nhưng vẫn có, những kẻ vẫn muốn được độc chiếm lấy wonman đó. su thế hiện tai của thế giới là giải quyết mọi,
vấn đề bằng âm nhạc. chính vì thế mà có rất nhiều kẻ thù xuất hiện thách đấu với main, Chi co minh ban chien dau, bạn phải chiến một mình và women (GIRLFRIEND) chỉ cổ vũ, không can thiệp vào trận đấu bạn phải chiến thắng tất cả các kẻ thù, để bảo vệ em ghẹ của mình.

## 🎮 Tính năng chính

- **Điều khiển bằng cử chỉ tay thực tế** – sử dụng MediaPipe + AI Random Forest.
- **5 cử chỉ chính**: UP (👍), DOWN (☝️), LEFT (✌️), RIGHT (🖐️), NONE (✊).
- **Chế độ chơi đa dạng**:
  - 📖 **Story Mode** – cốt truyện xuyên suốt, hội thoại kịch tính.
  - 🎵 **Free Play** – chơi tự do nhiều bài nhạc với độ khó tăng dần.
  - ⚔️ **Versus (LAN)** – đối đầu 2 người chơi trên cùng mạng LAN (host tạo phòng, client tham gia qua danh sách phòng tự động tìm thấy).
- **Hệ thống buff/debuff** – nhận buff khi chơi tốt hoặc bắt được Buff Note.
- **Mini game đa dạng**:
  - 🧠 **Ai là triệu phú** – trắc nghiệm kiến thức.
  - 🐦 **Flappy Bird** – điều khiển chim bằng cử chỉ tay.
  - 🖼️ **Đuổi hình bắt chữ (Pictionary)** – nhập đáp án qua bàn phím ảo.
  - ✍️ **Vua tiếng Việt** – ghép chữ thành từ có nghĩa.
- **Nhân vật có sprite riêng** – hỗ trợ ảnh nhân vật tuỳ chỉnh.
- **Âm thanh sống động** (có thể bật/tắt, điều chỉnh volume).

---

## 🕹️ Cách điều khiển

| Hành động | Cử chỉ tay | Phím thay thế |
|-----------|------------|----------------|
| Chọn nút / xác nhận | Giơ ngón cái (UP) | Mũi tên Lên / Enter |
| Di chuyển con trỏ (trong mini game) | Nắm tay + di chuyển cổ tay (NONE) | Chuột |
| Bật/tắt Auto Play (trong gameplay) | – | Phím **A** |
| Thoát game / về menu | – | **ESC** |
| Chơi lại (khi game over) | – | **R** |

---

## 🖥️ Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11 (hoặc Linux có hỗ trợ webcam)
- **Python**: 3.8 – 3.12
- **Webcam**: bắt buộc (để track tay)
- **RAM**: tối thiểu 4GB
- **Kết nối mạng** (cho chế độ LAN): card Ethernet/WiFi cùng mạng nội bộ.

---

## 🛠️ Cài đặt và chạy game

1. **Clone hoặc tải source code** về máy.
2. **Cài đặt Python 3.12** và pip.
3. **Cài đặt các thư viện cần thiết**:
   ```bash
   pip install pygame mediapipe opencv-python scikit-learn pandas numpy
