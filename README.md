# Partition Tolerance (SPlit-Brain) Test: "Key-Value Store"

**Sinh viên thực hiện:** Huỳnh Đình Thạch  
**Học phần:** Cơ sở dữ liệu phân tán 

## Tổng quan dự án (Project Overview)
Dự án này mô phỏng một hệ thống cơ sở dữ liệu phân tán gồm **5 Nodes độc lập**, hoạt động theo nguyên lý chia sẻ không tập trung. Hệ thống sử dụng thuật toán **Quorum-based voting (Túc số đa số)** để quản lý giao dịch cập nhật dữ liệu và duy trì tính nhất quán mạnh (Strong Consistency) khi xảy ra các sự cố mạng.


## Yêu cầu môi trường (Prerequisites)
- Python 3.8+
- Trình duyệt web (Chrome, Edge, Firefox,...) để chạy Frontend.
- Cài đặt các thư viện Python cần thiết:
  `pip install flask flask-cors requests`

## Hướng dẫn Cài đặt & Khởi chạy:

**Bước 1: Khởi tạo Cơ sở dữ liệu vật lý**
Hệ thống sử dụng file CSV nguồn để đúc ra 5 cơ sở dữ liệu SQLite độc lập (mô hình Key-Value: `product_id` và `stock`).
Tại thư mục gốc, mở Terminal và chạy lệnh:
  `python init_db.py`

**Bước 2: Khởi động Controller**
Controller đóng vai trò giám sát túc số mạng lưới và giả lập các kịch bản đứt mạng.
Mở một Terminal mới và chạy:
  `python controller.py`

**Bước 3: Khởi động 5 Nodes phân tán**
Mở 5 cửa sổ Terminal hoàn toàn độc lập (để mô phỏng 5 tiến trình/máy chủ khác nhau), lần lượt chạy các lệnh sau:
  `python nodes/node1.py`
  `python nodes/node2.py`
  `python nodes/node3.py`
  `python nodes/node4.py`
  `python nodes/node5.py`

**Bước 4: Mở Giao diện điều khiển**
Click đúp vào file `index.html` để mở giao diện quản trị trên trình duyệt.


## Cấu trúc thư mục (Project Structure)
- `init_db.py`: Script khởi tạo và dọn dẹp dữ liệu tự động.
- `controller.py`: Trái tim điều phối mạng lưới và đếm túc số.
- `nodes/`: Chứa mã nguồn Python của 5 Node và các file cơ sở dữ liệu vật lý `.sqlite3`.
- `logs/`: Nơi lưu trữ tự động các file nhật ký giao dịch `.log` (bị loại trừ khỏi GitHub qua `.gitignore`).
- `index.html`, `style.css`, `script.js`: Frontend điều khiển hệ thống và hiển thị Performance Metrics.
- `dataset.csv`: Dữ liệu gốc dùng để seed vào các cơ sở dữ liệu.