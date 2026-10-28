# TicketDesk — Tài liệu yêu cầu v1

> **Trạng thái:** Bản nháp — chờ trưởng bộ phận hỗ trợ duyệt
> **Tài liệu liên quan:** [Đặc tả API](api-spec.md) (phần kỹ thuật)

## Mục lục

1. [Stakeholder](#1-stakeholder)
2. [Phạm vi](#2-phạm-vi)
3. [Thuật ngữ và quy tắc nghiệp vụ](#3-thuật-ngữ-và-quy-tắc-nghiệp-vụ)
4. [User story](#4-user-story)
5. [Yêu cầu phi chức năng](#5-yêu-cầu-phi-chức-năng)
6. [Ưu tiên MoSCoW và phạm vi MVP](#6-ưu-tiên-moscow-và-phạm-vi-mvp)
7. [Câu hỏi còn mở](#7-câu-hỏi-còn-mở)

---

## 1. Stakeholder

| Nhóm | Vai trò | Quan tâm chính |
|---|---|---|
| Người dùng | **Khách hàng** | Gửi yêu cầu hỗ trợ, theo dõi tiến độ |
| Người dùng | **Nhân viên hỗ trợ** | Nhận và xử lý ticket, trao đổi với khách |
| Người dùng | **Quản lý** | Phân công, theo dõi khối lượng công việc và hiệu suất |
| Ra quyết định | **Trưởng bộ phận hỗ trợ** | Duyệt yêu cầu, chốt phạm vi MVP |
| Vận hành | **Bộ phận IT** | Triển khai, sao lưu, xử lý sự cố sau bàn giao |

## 2. Phạm vi

**Trong phạm vi MVP**

- Tài khoản, đăng nhập và phân quyền theo 3 vai trò
- Tạo, phân công, xử lý và đóng ticket
- Bình luận, ghi chú nội bộ, đính kèm tệp
- Thông báo qua email
- Báo cáo tổng quan cho quản lý

**Ngoài phạm vi MVP**

- Chat trực tiếp với khách hàng
- Ứng dụng di động
- Tích hợp tổng đài điện thoại

## 3. Thuật ngữ và quy tắc nghiệp vụ

### 3.1 Trạng thái ticket

| Trạng thái | Ý nghĩa |
|---|---|
| **Mới** | Khách vừa gửi, chưa có người xử lý |
| **Đang xử lý** | Đã có nhân viên phụ trách |
| **Đã xử lý** | Nhân viên báo đã giải quyết xong, chờ xác nhận |
| **Đã đóng** | Kết thúc; không được thay đổi nữa |

### 3.2 Chuyển trạng thái hợp lệ

| Từ | Sang | Ai thực hiện |
|---|---|---|
| Mới | Đang xử lý | Tự động khi quản lý gán hoặc nhân viên nhận ticket |
| Đang xử lý | Đã xử lý | Nhân viên đang phụ trách |
| Đã xử lý | Đã đóng | Khách hàng xác nhận, hoặc quản lý |
| Đã xử lý | Đang xử lý | Khách hàng mở lại vì vấn đề chưa được giải quyết |

Mọi chuyển trạng thái khác đều bị từ chối (ví dụ: Mới → Đã đóng).

### 3.3 Mức ưu tiên và thời hạn xử lý (SLA)

| Mức ưu tiên | Thời hạn xử lý (đề xuất, chờ xác nhận) |
|---|---|
| Cao | 4 giờ |
| Trung bình | 24 giờ |
| Thấp | 72 giờ |

Thời hạn tính từ lúc tạo ticket đến khi ticket chuyển sang **Đã xử lý**.

### 3.4 Quyền xem ticket

- **Khách hàng:** chỉ ticket do mình tạo.
- **Nhân viên hỗ trợ:** ticket mình phụ trách và ticket chưa có người xử lý.
- **Quản lý:** tất cả ticket.

---

## 4. User story

Mẫu: *Là [vai trò], tôi muốn [hành động] để [giá trị].*

| Epic | Story |
|---|---|
| E1. Tài khoản và phân quyền | US01, US02, US03 |
| E2. Xử lý ticket | US04, US05, US06, US07, US08 |
| E3. Trao đổi trên ticket | US09, US10, US11 |
| E4. Thông báo | US12 |
| E5. Báo cáo và giám sát | US13, US14, US15 |

---

### E1. Tài khoản và phân quyền

#### US01 — Đăng ký và đăng nhập

> Là **khách hàng**, tôi muốn đăng ký tài khoản và đăng nhập bằng email để gửi và theo dõi yêu cầu hỗ trợ của mình.

**Ưu tiên:** Must

**Kịch bản 1: Đăng ký thành công**
- **Given** khách chưa có tài khoản
- **When** khách đăng ký bằng email hợp lệ và mật khẩu đủ mạnh, nhập lại mật khẩu khớp
- **Then** tài khoản được tạo với vai trò **Khách hàng**
- **And** khách nhận được thông báo đăng ký thành công

**Kịch bản 2: Email đã được dùng**
- **Given** email `an@example.com` đã có tài khoản
- **When** một người đăng ký bằng `an@example.com`
- **Then** hệ thống báo "Email này đã được đăng ký"
- **And** không có tài khoản mới nào được tạo

**Kịch bản 3: Mật khẩu không đạt yêu cầu**
- **Given** khách đang đăng ký
- **When** khách nhập mật khẩu dưới 8 ký tự, hoặc nhập lại mật khẩu không khớp
- **Then** hệ thống chỉ rõ lỗi ở ô mật khẩu và không tạo tài khoản

**Kịch bản 4: Đăng nhập thành công**
- **Given** khách có tài khoản đang hoạt động
- **When** khách nhập đúng email và mật khẩu
- **Then** khách vào được hệ thống và thấy danh sách ticket của mình

**Kịch bản 5: Đăng nhập sai**
- **Given** khách đang ở màn hình đăng nhập
- **When** khách nhập email chưa đăng ký hoặc sai mật khẩu
- **Then** hệ thống báo "Email hoặc mật khẩu không đúng" (không nói rõ sai phần nào)

---

#### US02 — Quản lý tài khoản và vai trò

> Là **quản lý**, tôi muốn cấp vai trò và khoá tài khoản để mỗi thành viên có đúng quyền hạn.

**Ưu tiên:** Must

**Kịch bản 1: Cấp vai trò nhân viên hỗ trợ**
- **Given** "binh" đang có vai trò Khách hàng
- **When** quản lý đổi vai trò của "binh" thành **Nhân viên hỗ trợ**
- **Then** lần đăng nhập tiếp theo "binh" thấy được các ticket chưa có người xử lý

**Kịch bản 2: Người không phải quản lý không được đổi vai trò**
- **Given** người dùng có vai trò Khách hàng hoặc Nhân viên hỗ trợ
- **When** người đó cố đổi vai trò của một tài khoản
- **Then** hệ thống từ chối với thông báo "Bạn không có quyền thực hiện thao tác này"

**Kịch bản 3: Khoá tài khoản**
- **Given** nhân viên "chi" đã nghỉ việc
- **When** quản lý khoá tài khoản của "chi"
- **Then** "chi" bị đăng xuất khỏi mọi thiết bị và không đăng nhập lại được
- **And** các ticket "chi" đang phụ trách trở về trạng thái chưa có người xử lý

---

#### US03 — Cập nhật hồ sơ và đổi mật khẩu

> Là **người dùng**, tôi muốn cập nhật thông tin cá nhân và đổi mật khẩu để giữ tài khoản chính xác và an toàn.

**Ưu tiên:** Should

**Kịch bản 1: Cập nhật hồ sơ**
- **Given** người dùng đã đăng nhập
- **When** người dùng sửa họ tên hoặc số điện thoại
- **Then** thông tin mới được lưu và hiển thị ngay

**Kịch bản 2: Đổi mật khẩu thành công**
- **Given** người dùng đã đăng nhập
- **When** người dùng nhập đúng mật khẩu hiện tại và mật khẩu mới hợp lệ
- **Then** mật khẩu được đổi; lần đăng nhập sau phải dùng mật khẩu mới

**Kịch bản 3: Sai mật khẩu hiện tại**
- **Given** người dùng đã đăng nhập
- **When** người dùng nhập sai mật khẩu hiện tại
- **Then** hệ thống báo "Mật khẩu hiện tại không đúng" và giữ nguyên mật khẩu cũ

---

### E2. Xử lý ticket

#### US04 — Tạo ticket

> Là **khách hàng**, tôi muốn gửi yêu cầu hỗ trợ để vấn đề của tôi được giải quyết.

**Ưu tiên:** Must

**Kịch bản 1: Tạo ticket thành công**
- **Given** khách đã đăng nhập
- **When** khách nhập tiêu đề, mô tả, chọn danh mục và mức ưu tiên rồi gửi
- **Then** ticket được tạo ở trạng thái **Mới**, có mã theo dõi (ví dụ `TD-42`)
- **And** khách thấy ticket ở đầu danh sách của mình

**Kịch bản 2: Thiếu thông tin bắt buộc**
- **Given** khách đang tạo ticket
- **When** khách để trống tiêu đề hoặc mô tả
- **Then** hệ thống chỉ rõ ô còn thiếu và không tạo ticket

**Kịch bản 3: Nhân viên và quản lý không tạo ticket thay khách**
- **Given** người dùng có vai trò Nhân viên hỗ trợ hoặc Quản lý
- **Then** người dùng không thấy chức năng tạo ticket

---

#### US05 — Xem và lọc danh sách ticket

> Là **nhân viên hỗ trợ**, tôi muốn lọc ticket theo trạng thái để xử lý ticket mới trước.

**Ưu tiên:** Must

**Kịch bản 1: Mỗi vai trò chỉ thấy đúng ticket của mình**
- **Given** khách "an" có 3 ticket, khách "binh" có 2 ticket
- **When** "an" mở danh sách ticket
- **Then** "an" chỉ thấy 3 ticket của mình
- **And** nhân viên chỉ thấy ticket mình phụ trách và ticket chưa có người xử lý; quản lý thấy tất cả (xem mục 3.4)

**Kịch bản 2: Lọc theo trạng thái**
- **Given** có 5 ticket **Mới** và 8 ticket **Đang xử lý**
- **When** nhân viên lọc theo trạng thái **Mới**
- **Then** chỉ 5 ticket **Mới** được hiển thị

**Kịch bản 3: Phân trang**
- **Given** người dùng có quyền xem 45 ticket
- **When** người dùng mở danh sách
- **Then** mỗi trang hiển thị 20 ticket, mới nhất trước, kèm tổng số ticket và số trang

**Kịch bản 4: Không xem được ticket của người khác**
- **Given** ticket `TD-50` thuộc khách "binh"
- **When** khách "an" mở đường dẫn tới `TD-50`
- **Then** hệ thống báo "Không tìm thấy ticket" (không tiết lộ ticket có tồn tại)

---

#### US06 — Gán ticket cho nhân viên

> Là **quản lý**, tôi muốn gán ticket cho nhân viên để công việc có người chịu trách nhiệm.

**Ưu tiên:** Must

**Kịch bản 1: Gán thành công**
- **Given** ticket `TD-42` đang ở trạng thái **Mới**
- **When** quản lý gán ticket cho "nhanvien01"
- **Then** người xử lý của ticket là "nhanvien01"
- **And** trạng thái chuyển thành **Đang xử lý**

**Kịch bản 2: Chuyển ticket sang nhân viên khác**
- **Given** ticket `TD-42` đang do "nhanvien01" xử lý
- **When** quản lý gán lại cho "nhanvien02"
- **Then** người xử lý là "nhanvien02" và việc chuyển được ghi vào lịch sử ticket

**Kịch bản 3: Không gán được ticket đã đóng**
- **Given** ticket `TD-43` đang ở trạng thái **Đã đóng**
- **When** quản lý gán ticket cho "nhanvien01"
- **Then** hệ thống báo "Ticket đã đóng"
- **And** ticket không thay đổi

**Kịch bản 4: Chỉ gán được cho nhân viên hỗ trợ**
- **Given** "an" có vai trò Khách hàng
- **When** quản lý chọn người xử lý
- **Then** "an" không có trong danh sách để chọn

---

#### US07 — Nhân viên tự nhận ticket

> Là **nhân viên hỗ trợ**, tôi muốn tự nhận ticket chưa có người xử lý để bắt tay vào việc mà không phải chờ quản lý phân công.

**Ưu tiên:** Should

**Kịch bản 1: Nhận ticket thành công**
- **Given** ticket `TD-44` đang **Mới** và chưa có người xử lý
- **When** "nhanvien01" bấm "Nhận ticket"
- **Then** "nhanvien01" trở thành người xử lý, trạng thái chuyển thành **Đang xử lý**

**Kịch bản 2: Hai nhân viên cùng nhận một ticket**
- **Given** "nhanvien01" vừa nhận `TD-44`
- **When** "nhanvien02" bấm "Nhận ticket" `TD-44` ngay sau đó
- **Then** hệ thống báo "Ticket đã có người nhận" và người xử lý vẫn là "nhanvien01"

---

#### US08 — Cập nhật trạng thái ticket

> Là **nhân viên hỗ trợ**, tôi muốn cập nhật trạng thái ticket để khách hàng và quản lý biết tiến độ xử lý.

**Ưu tiên:** Must

**Kịch bản 1: Báo đã xử lý xong**
- **Given** ticket `TD-42` đang **Đang xử lý** và do "nhanvien01" phụ trách
- **When** "nhanvien01" chuyển ticket sang **Đã xử lý**
- **Then** trạng thái là **Đã xử lý** và thời điểm xử lý xong được ghi lại

**Kịch bản 2: Khách xác nhận và đóng ticket**
- **Given** ticket `TD-42` đang **Đã xử lý**
- **When** khách xác nhận vấn đề đã được giải quyết
- **Then** ticket chuyển sang **Đã đóng**

**Kịch bản 3: Khách mở lại ticket**
- **Given** ticket `TD-42` đang **Đã xử lý**
- **When** khách báo vấn đề vẫn chưa được giải quyết
- **Then** ticket quay lại **Đang xử lý** với cùng người phụ trách

**Kịch bản 4: Chuyển trạng thái không hợp lệ**
- **Given** ticket `TD-45` đang **Mới**
- **When** ai đó cố chuyển thẳng sang **Đã đóng**
- **Then** hệ thống báo "Không thể chuyển từ Mới sang Đã đóng" và ticket không thay đổi

**Kịch bản 5: Ticket đã đóng không sửa được**
- **Given** ticket `TD-43` đang **Đã đóng**
- **When** bất kỳ ai cố thay đổi trạng thái, người xử lý hoặc nội dung
- **Then** hệ thống báo "Ticket đã đóng"

---

### E3. Trao đổi trên ticket

#### US09 — Bình luận và ghi chú nội bộ

> Là **nhân viên hỗ trợ**, tôi muốn trao đổi với khách và ghi chú nội bộ trên ticket để giải quyết vấn đề mà không lộ thông tin nội bộ cho khách.

**Ưu tiên:** Must

**Kịch bản 1: Bình luận công khai**
- **Given** khách "an" là chủ ticket `TD-42`
- **When** "an" hoặc nhân viên phụ trách gửi bình luận
- **Then** bình luận hiện trên ticket cho cả hai bên, kèm tên người viết và thời gian

**Kịch bản 2: Ghi chú nội bộ**
- **Given** nhân viên đang xem ticket `TD-42`
- **When** nhân viên gửi bình luận và đánh dấu "Nội bộ"
- **Then** nhân viên và quản lý thấy ghi chú này
- **And** khách "an" không thấy ghi chú này

**Kịch bản 3: Khách không tạo được ghi chú nội bộ**
- **Given** khách đang xem ticket của mình
- **Then** khách không thấy lựa chọn "Nội bộ"

**Kịch bản 4: Bình luận trống**
- **When** người dùng gửi bình luận không có nội dung
- **Then** hệ thống không lưu và nhắc nhập nội dung

---

#### US10 — Lịch sử hoạt động của ticket

> Là **quản lý**, tôi muốn xem lịch sử thay đổi của ticket để biết ai đã làm gì và khi nào.

**Ưu tiên:** Should

**Kịch bản 1: Thay đổi được ghi lại tự động**
- **Given** ticket `TD-42` đang **Mới**
- **When** quản lý gán ticket cho "nhanvien01"
- **Then** lịch sử ghi: thời gian, "quản lý" đã gán người xử lý, từ "chưa có" sang "nhanvien01", trạng thái từ **Mới** sang **Đang xử lý**

**Kịch bản 2: Xem lịch sử**
- **Given** ticket có nhiều thay đổi
- **When** người dùng có quyền xem ticket mở tab "Lịch sử"
- **Then** các thay đổi hiển thị theo thời gian, mới nhất trước

**Kịch bản 3: Lịch sử không sửa được**
- **Then** không ai, kể cả quản lý, sửa hoặc xoá được lịch sử

---

#### US11 — Đính kèm tệp

> Là **khách hàng**, tôi muốn đính kèm ảnh chụp màn hình hoặc tài liệu vào ticket để nhân viên hiểu rõ vấn đề.

**Ưu tiên:** Should

**Kịch bản 1: Đính kèm thành công**
- **Given** ticket `TD-42` chưa đóng
- **When** khách đính kèm tệp ảnh (PNG, JPG), PDF hoặc Word, dung lượng tối đa 10 MB
- **Then** tệp hiện trong ticket với tên gốc và dung lượng

**Kịch bản 2: Loại tệp không được hỗ trợ**
- **When** khách đính kèm tệp chương trình (ví dụ `setup.exe`)
- **Then** hệ thống báo "Loại tệp không được hỗ trợ" và không lưu tệp

**Kịch bản 3: Tệp quá lớn**
- **When** khách đính kèm tệp lớn hơn 10 MB
- **Then** hệ thống báo "Tệp vượt quá 10 MB"

**Kịch bản 4: Chỉ người liên quan tải được tệp**
- **Given** tệp đính kèm thuộc ticket của khách "an"
- **When** khách "binh" mở đường dẫn tải tệp
- **Then** hệ thống báo "Không tìm thấy" và không trả tệp

---

### E4. Thông báo

#### US12 — Thông báo qua email

> Là **khách hàng** và **nhân viên hỗ trợ**, tôi muốn nhận email khi ticket có thay đổi quan trọng để không phải liên tục vào hệ thống kiểm tra.

**Ưu tiên:** Should

**Kịch bản 1: Khách nhận email khi tạo ticket**
- **Given** khách vừa tạo ticket `TD-42`
- **Then** khách nhận email chứa mã ticket và đường dẫn xem ticket
- **And** khách không phải chờ email gửi xong mới thấy ticket được tạo

**Kịch bản 2: Nhân viên nhận email khi được gán ticket**
- **When** quản lý gán `TD-42` cho "nhanvien01"
- **Then** "nhanvien01" nhận email có tiêu đề, mức ưu tiên và đường dẫn tới ticket

**Kịch bản 3: Khách nhận email khi ticket được xử lý xong**
- **When** ticket `TD-42` chuyển sang **Đã xử lý**
- **Then** khách nhận email mời xác nhận đóng hoặc mở lại ticket

**Kịch bản 4: Máy chủ email tạm thời lỗi**
- **Given** máy chủ email không phản hồi
- **Then** hệ thống tự gửi lại tối đa 3 lần, giãn cách tăng dần
- **And** nếu vẫn lỗi thì ghi nhận để bộ phận IT kiểm tra; thao tác của người dùng không bị ảnh hưởng

---

### E5. Báo cáo và giám sát

#### US13 — Tổng quan khối lượng công việc

> Là **quản lý**, tôi muốn xem tổng quan ticket và hiệu suất từng nhân viên để phân bổ công việc hợp lý.

**Ưu tiên:** Should

**Kịch bản 1: Số ticket theo trạng thái**
- **Given** quản lý chọn khoảng thời gian 01/10 – 19/10
- **When** quản lý mở trang tổng quan
- **Then** quản lý thấy số ticket tạo trong khoảng đó theo từng trạng thái, và số ticket chưa có người xử lý

**Kịch bản 2: Hiệu suất nhân viên**
- **When** quản lý xem bảng hiệu suất trong cùng khoảng thời gian
- **Then** mỗi nhân viên có: số ticket được giao, số ticket đã xử lý, thời gian xử lý trung bình (giờ)

**Kịch bản 3: Chỉ quản lý xem được**
- **Given** người dùng có vai trò Khách hàng hoặc Nhân viên hỗ trợ
- **Then** người dùng không thấy và không mở được trang tổng quan

---

#### US14 — Cảnh báo ticket quá hạn

> Là **quản lý**, tôi muốn biết ticket nào đã quá hạn xử lý để can thiệp kịp thời.

**Ưu tiên:** Could

**Kịch bản 1: Ticket bị đánh dấu quá hạn**
- **Given** ticket ưu tiên **Cao** được tạo lúc 08:00, đang **Mới** hoặc **Đang xử lý**
- **When** đến 12:00 ticket vẫn chưa chuyển sang **Đã xử lý**
- **Then** ticket được đánh dấu "Quá hạn" (chậm nhất 15 phút sau khi quá hạn)

**Kịch bản 2: Lọc ticket quá hạn**
- **When** quản lý lọc danh sách theo "Quá hạn"
- **Then** chỉ ticket quá hạn được hiển thị, quá hạn lâu nhất trước

**Kịch bản 3: Ticket xử lý đúng hạn**
- **Given** ticket ưu tiên **Cao** chuyển sang **Đã xử lý** sau 3 giờ
- **Then** ticket không bị đánh dấu quá hạn

---

#### US15 — Xuất báo cáo Excel

> Là **quản lý**, tôi muốn xuất danh sách ticket ra Excel để báo cáo cho cấp trên.

**Ưu tiên:** Could

**Kịch bản 1: Yêu cầu xuất báo cáo**
- **Given** quản lý đã lọc danh sách ticket (theo trạng thái, khoảng thời gian, nhân viên)
- **When** quản lý bấm "Xuất Excel"
- **Then** hệ thống báo "Đang tạo báo cáo"; quản lý tiếp tục làm việc khác mà không phải chờ

**Kịch bản 2: Tải báo cáo**
- **Given** báo cáo đã tạo xong
- **Then** quản lý thấy nút "Tải về" và nhận được tệp Excel chứa đúng các ticket đã lọc

**Kịch bản 3: Báo cáo hết hạn**
- **Given** báo cáo được tạo cách đây hơn 24 giờ
- **When** quản lý mở lại đường dẫn tải
- **Then** hệ thống báo báo cáo đã hết hạn và gợi ý xuất lại

---

## 5. Yêu cầu phi chức năng

| Nhóm | Yêu cầu (đo được) |
|---|---|
| Bảo mật | Mật khẩu được băm, không lưu dạng đọc được |
| Bảo mật | Mọi chức năng, trừ đăng ký và đăng nhập, đều yêu cầu đăng nhập |
| Bảo mật | Phiên đăng nhập hết hạn sau 30 phút không hoạt động |
| Bảo mật | Bắt buộc HTTPS trên môi trường production |
| Phân quyền | Người dùng không xem được ticket, bình luận, tệp ngoài quyền của mình (mục 3.4), kể cả khi tự gõ đường dẫn |
| Hiệu năng | 95% lượt mở danh sách ticket (20 ticket/trang) phản hồi dưới 500 ms khi có 10.000 ticket |
| Hiệu năng | Gửi email và xuất báo cáo không làm chậm thao tác của người dùng |
| Tệp đính kèm | Tối đa 10 MB/tệp; chỉ nhận PNG, JPG, PDF, DOCX; kiểm tra theo nội dung tệp, không chỉ theo đuôi |
| Vận hành | Sao lưu dữ liệu hằng ngày; khôi phục được trong vòng 1 giờ |
| Vận hành | Có trang tài liệu API để bộ phận IT và đội phát triển tra cứu |
| Truy vết | Mọi thay đổi trạng thái và người xử lý đều được ghi lịch sử, không sửa được |

## 6. Ưu tiên MoSCoW và phạm vi MVP

| Mức | Story |
|---|---|
| **Must** (MVP) | US01, US02, US04, US05, US06, US08, US09 |
| **Should** | US03, US07, US10, US11, US12, US13 |
| **Could** | US14, US15 |
| **Won't** (lần này) | Chat trực tiếp, ứng dụng di động, tích hợp tổng đài, đánh giá mức độ hài lòng của khách |

## 7. Câu hỏi còn mở

Cần hỏi trưởng bộ phận hỗ trợ trước khi chốt v1:

1. Thời hạn xử lý ở mục 3.3 có đúng thực tế không? Có cần mức ưu tiên **Khẩn cấp** riêng không?
2. Nếu khách không xác nhận, ticket **Đã xử lý** có tự động đóng sau một số ngày không?
3. Thời hạn xử lý có tính cả ngoài giờ làm việc, cuối tuần không?
4. Khi khách mở lại ticket, thời hạn xử lý tính lại từ đầu hay tiếp tục?
5. Nhân viên hỗ trợ có cần tạo ticket thay khách (khi khách gọi điện) không?
6. Danh mục ticket do ai quản lý, có những danh mục nào?
