# TicketDesk — Đặc tả API v1

> **Trạng thái:** Chính thức — đã được mentor duyệt
> **Dựa trên:** [Tài liệu yêu cầu](user-stories.md)
> **Công nghệ:** Django REST Framework, djangorestframework-simplejwt, django-filter, drf-spectacular

## 1. Quy ước chung

| Mục | Quy ước |
|---|---|
| Base URL | `/api/` |
| Định dạng | JSON, UTF-8 |
| Xác thực | Header `Authorization: Bearer <access_token>` |
| Đường dẫn | Có dấu `/` ở cuối (mặc định của DRF router) |
| Tài liệu | Swagger UI tại `/api/docs/`, schema tại `/api/schema/` |

### 1.1 Phân trang

Dùng `PageNumberPagination` của DRF, 20 bản ghi/trang, tham số `?page=2`.

```json
{
  "count": 45,
  "next": "https://.../api/tickets/?page=3",
  "previous": "https://.../api/tickets/?page=1",
  "results": []
}
```

### 1.2 Lỗi

Mọi lỗi nghiệp vụ trả về cùng một format:

```json
{ "detail": "Ticket đã đóng", "code": "ticket_closed" }
```

Lỗi validation (400) trả về theo từng field, mặc định của DRF:

```json
{ "title": ["Trường này không được để trống."] }
```

| Mã | Khi nào |
|---|---|
| 400 | Dữ liệu gửi lên sai |
| 401 | Chưa đăng nhập, token hết hạn hoặc không hợp lệ |
| 403 | Đã đăng nhập nhưng không đủ quyền |
| 404 | Không tìm thấy, **hoặc không có quyền xem** (tránh lộ thông tin — IDOR) |
| 409 | Xung đột trạng thái (ticket đã đóng, đã có người nhận, chuyển trạng thái sai) |
| 413 | Tệp vượt quá 10 MB |

## 2. Mapping enum

| Nghiệp vụ | Giá trị API |
|---|---|
| Khách hàng / Nhân viên hỗ trợ / Quản lý | `customer` / `agent` / `manager` |
| Mới / Đang xử lý / Đã xử lý / Đã đóng | `new` / `in_progress` / `resolved` / `closed` |
| Thấp / Trung bình / Cao | `1` / `2` / `3` |

## 3. Endpoint

### 3.1 Xác thực và tài khoản (US01–US03)

| Method | Đường dẫn | Mô tả | Quyền | Thành công | Lỗi |
|---|---|---|---|---|---|
| POST | `/api/auth/register/` | Đăng ký | Ai cũng được | 201 | 400 |
| POST | `/api/auth/token/` | Đăng nhập, trả `access`, `refresh` | Ai cũng được | 200 | 401 |
| POST | `/api/auth/token/refresh/` | Lấy access token mới | Ai cũng được | 200 | 401 |
| POST | `/api/auth/logout/` | Đưa refresh token vào blacklist | Đã đăng nhập | 205 | 401 |
| GET / PATCH | `/api/users/me/` | Xem / sửa hồ sơ | Đã đăng nhập | 200 | 400 |
| POST | `/api/users/me/change-password/` | Đổi mật khẩu | Đã đăng nhập | 200 | 400 |
| GET | `/api/users/` | Danh sách người dùng (`?role=agent`) | Manager | 200 | 403 |
| PATCH | `/api/users/{id}/` | Đổi `role`, `is_active` | Manager | 200 | 400, 403, 404 |

### 3.2 Ticket (US04–US08, US14)

| Method | Đường dẫn | Mô tả | Quyền | Thành công | Lỗi |
|---|---|---|---|---|---|
| GET | `/api/tickets/` | Danh sách, lọc `?status=`, `?priority=`, `?assignee=`, `?sla_breached=true`, `?search=`, `?ordering=` | Theo vai trò (mục 4) | 200 | 401 |
| POST | `/api/tickets/` | Tạo ticket | Customer | 201 | 400, 403 |
| GET | `/api/tickets/{id}/` | Chi tiết | Theo vai trò | 200 | 404 |
| POST | `/api/tickets/{id}/assign/` | Gán, body `{"assignee": 5}` | Manager | 200 | 400, 403, 409 |
| POST | `/api/tickets/{id}/claim/` | Nhân viên tự nhận | Agent | 200 | 403, 409 |
| POST | `/api/tickets/{id}/transition/` | Chuyển trạng thái, body `{"status": "resolved"}` | Theo bảng chuyển trạng thái | 200 | 403, 409 |

Các field `status`, `assignee`, `created_by`, `code`, `resolved_at`, `is_sla_breached` là **read-only** trong serializer. Chỉ đổi được qua các action ở trên.

### 3.3 Bình luận, lịch sử, tệp đính kèm (US09–US11)

| Method | Đường dẫn | Mô tả | Quyền | Thành công | Lỗi |
|---|---|---|---|---|---|
| GET | `/api/tickets/{id}/comments/` | Danh sách bình luận (Customer không nhận `is_internal=true`) | Theo vai trò | 200 | 404 |
| POST | `/api/tickets/{id}/comments/` | Thêm bình luận, `is_internal` chỉ Agent/Manager được đặt | Theo vai trò | 201 | 400, 403, 404 |
| GET | `/api/tickets/{id}/activities/` | Lịch sử, mới nhất trước | Theo vai trò | 200 | 404 |
| POST | `/api/tickets/{id}/attachments/` | Upload (multipart) | Theo vai trò | 201 | 400, 404, 409, 413 |
| GET | `/api/attachments/{id}/download/` | Tải tệp, có header `Content-Disposition` | Theo vai trò | 200 | 404 |

### 3.4 Báo cáo (US13, US15)

| Method | Đường dẫn | Mô tả | Quyền | Thành công | Lỗi |
|---|---|---|---|---|---|
| GET | `/api/reports/overview/?start_date=&end_date=` | Đếm theo trạng thái + số chưa gán | Manager | 200 | 400, 403 |
| GET | `/api/reports/agents/?start_date=&end_date=` | `tickets_assigned`, `tickets_resolved`, `avg_resolution_hours` | Manager | 200 | 403 |
| POST | `/api/reports/exports/` | Tạo job xuất Excel, trả `{"id": "..."}` | Manager | 202 | 400, 403 |
| GET | `/api/reports/exports/{id}/` | Trạng thái `pending` / `success` / `failure`, kèm `download_url` | Manager (người tạo) | 200 | 404 |

## 4. Phân quyền dữ liệu

Lọc trong `get_queryset()`, không lọc ở frontend:

| Vai trò | Ticket nhìn thấy |
|---|---|
| `customer` | `created_by = request.user` |
| `agent` | `assignee = request.user` hoặc `assignee IS NULL` |
| `manager` | Tất cả |

## 5. Ghi chú kỹ thuật (ứng viên cho ADR)

| Chủ đề | Quyết định đề xuất | Story |
|---|---|---|
| Băm mật khẩu | Argon2 (`argon2-cffi`), đặt đầu `PASSWORD_HASHERS` | US01, US03 |
| Khoá tài khoản | Bật `rest_framework_simplejwt.token_blacklist`, blacklist mọi refresh token của user | US02 |
| Gán / nhận đồng thời | `select_for_update()` trong `transaction.atomic` (`services.assign_ticket`) | US06, US07 |
| Chuyển trạng thái | Kiểm tra trong `services.transition_ticket` theo bảng mục 3.2 của tài liệu yêu cầu | US08 |
| Lịch sử | Model `TicketActivity` chỉ insert, ghi trong cùng service, không có API sửa/xoá | US10 |
| Tệp đính kèm | Tên lưu là UUID; kiểm tra MIME bằng nội dung tệp; Nginx `client_max_body_size 10M` | US11 |
| Email | Celery task, gọi qua `transaction.on_commit()`; `autoretry_for`, `max_retries=3`, `retry_backoff=True` | US12 |
| Quá hạn SLA | Celery beat chạy mỗi 15 phút, cập nhật `is_sla_breached` | US14 |
| Xuất Excel | Celery task + `openpyxl`; tệp xoá sau 24 giờ | US15 |
