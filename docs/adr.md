# ADR-001: Dùng PostgreSQL thay vì MySQL
Ngày: 2026-10-27 · Trạng thái: Đã chấp nhận
Bối cảnh:  Cần full-text search tiếng Việt, JSONField, team đã quen PostgreSQL.
Quyết định: Dùng PostgreSQL 16 chạy bằng Docker.
Hệ quả:    + Dùng được SearchVector, JSONField. − Thành viên mới cần học psql.

# ADR-002: Lưu is_sla_breached thay vì tính khi truy vấn
Ngày: 2026-10-28 . Trạng thái: đã chấp nhận
Bối cảnh: quản lý cần lọc nhanh các ticket quá hạn nhưng thời hạn của 1 ticket lại phụ thuộc vào mức độ ưu tiên
Quyết định: Tạo cột is_sla_breached trong bảng ticket đặt kiểu dữ liệu boolean nhằm cho Celery có thể cập nhật ticket quá hạn theo chu kì 15p thay vì truy vấn lúc cần
Hệ quả: truy vấn nhanh và có index nhưng dữ liệu có thể trễ 15p, phải cập nhật khi đổi priority hoặc khi ticket chuyển status sang đã xử lý và hệ thống phải chạy thêm 1 job.