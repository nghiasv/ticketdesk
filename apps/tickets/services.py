"""Nghiệp vụ của ticket. View và API (tuần 6) gọi vào đây, không tự sửa ticket."""

from django.db import transaction

from apps.accounts.models import User

from .models import Ticket


class TicketClosedError(Exception):
    """Ticket đã đóng, không được thao tác nữa (api-spec: mã lỗi ticket_closed, HTTP 409)."""


class InvalidAssigneeError(Exception):
    """Người được gán không phải nhân viên hỗ trợ đang hoạt động."""


@transaction.atomic
def assign_ticket(ticket_id: int, agent: User) -> Ticket:
    """Gán ticket cho nhân viên hỗ trợ và chuyển sang Đang xử lý.

    select_for_update() khoá dòng ticket tới hết transaction: nếu hai quản lý gán
    cùng lúc, request sau phải chờ request trước commit rồi mới đọc được dữ liệu mới,
    nên không có chuyện hai lần gán ghi đè lên nhau.
    """
    if agent.role != User.Role.AGENT or not agent.is_active:
        raise InvalidAssigneeError("Chỉ gán được cho nhân viên hỗ trợ đang hoạt động")

    ticket = Ticket.objects.select_for_update().get(pk=ticket_id)
    if ticket.status == Ticket.Status.CLOSED:
        raise TicketClosedError("Ticket đã đóng")

    ticket.assignee = agent
    if ticket.status == Ticket.Status.NEW:
        ticket.status = Ticket.Status.IN_PROGRESS
    # Chỉ UPDATE đúng các cột này, không ghi đè cột khác mà request khác vừa sửa
    ticket.save(update_fields=["assignee", "status", "updated_at"])
    return ticket
