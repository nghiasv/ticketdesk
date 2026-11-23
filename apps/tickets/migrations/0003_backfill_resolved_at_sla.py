"""Data migration: điền resolved_at và is_sla_breached cho các ticket đã có.

Ticket tạo trước migration 0002 không có resolved_at. Với ticket đã xử lý hoặc đã đóng,
lấy tạm updated_at (lần sửa cuối) làm thời điểm xử lý xong. Sau đó tính cờ quá hạn
theo thời hạn của từng mức ưu tiên (mục 3.3 tài liệu yêu cầu).

Mọi phép tính dùng F() và update() nên chạy hoàn toàn trong database,
không kéo 10.000 ticket về Python.
"""

from datetime import timedelta

from django.db import migrations
from django.db.models import F
from django.utils import timezone

# Chép cứng thay vì import từ models: migration phải giữ nguyên kết quả
# dù sau này model có đổi giá trị SLA.
SLA_HOURS = {3: 4, 2: 24, 1: 72}
DONE = ["resolved", "closed"]
OPEN = ["new", "in_progress"]


def backfill(apps, schema_editor):
    Ticket = apps.get_model("tickets", "Ticket")

    Ticket.objects.filter(status__in=DONE, resolved_at__isnull=True).update(
        resolved_at=F("updated_at")
    )

    now = timezone.now()
    for priority, hours in SLA_HOURS.items():
        sla = timedelta(hours=hours)
        # Đang mở và đã quá hạn tính tới hiện tại
        Ticket.objects.filter(
            priority=priority, status__in=OPEN, created_at__lt=now - sla
        ).update(is_sla_breached=True)
        # Đã xử lý nhưng xử lý xong sau hạn (so sánh hai cột bằng F)
        Ticket.objects.filter(
            priority=priority, status__in=DONE, resolved_at__gt=F("created_at") + sla
        ).update(is_sla_breached=True)


def unbackfill(apps, schema_editor):
    Ticket = apps.get_model("tickets", "Ticket")
    Ticket.objects.update(resolved_at=None, is_sla_breached=False)


class Migration(migrations.Migration):
    dependencies = [
        ("tickets", "0002_ticket_code_sla_resolved"),
    ]

    operations = [
        migrations.RunPython(backfill, unbackfill),
    ]
