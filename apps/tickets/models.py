from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.functions import Cast, Concat


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Mới"
        IN_PROGRESS = "in_progress", "Đang xử lý"
        RESOLVED = "resolved", "Đã xử lý"
        CLOSED = "closed", "Đã đóng"

    class Priority(models.IntegerChoices):
        LOW = 1, "Thấp"
        MEDIUM = 2, "Trung bình"
        HIGH = 3, "Cao"

    # Thời hạn xử lý theo mục 3.3 tài liệu yêu cầu, tính từ lúc tạo tới lúc "Đã xử lý"
    SLA_HOURS = {Priority.HIGH: 4, Priority.MEDIUM: 24, Priority.LOW: 72}
    # Trạng thái được coi là đã xử lý xong, khi đó resolved_at phải có giá trị
    DONE_STATUSES = (Status.RESOLVED, Status.CLOSED)

    # Mã theo dõi dạng TD-42, do PostgreSQL tự sinh từ id (cột generated, không ghi tay được)
    code = models.GeneratedField(
        expression=Concat(models.Value("TD-"), Cast("id", models.CharField())),
        output_field=models.CharField(max_length=20),
        db_persist=True,
        unique=True,
    )
    title = models.CharField("Tiêu đề", max_length=200)
    description = models.TextField("Mô tả")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.MEDIUM)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="tickets"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tickets",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    # ADR-002: lưu sẵn cờ quá hạn để lọc nhanh, job định kỳ sẽ cập nhật (tuần 8)
    is_sla_breached = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            # Trang danh sách của quản lý: ORDER BY created_at DESC LIMIT 20
            models.Index(fields=["-created_at"], name="ticket_created_idx"),
            # Lọc theo trạng thái rồi sắp xếp mới nhất trước
            models.Index(
                fields=["status", "-created_at"], name="ticket_status_created_idx"
            ),
            # Index một phần (partial): chỉ chứa ticket quá hạn, phục vụ lọc ?sla_breached=true
            models.Index(
                fields=["-created_at"],
                condition=models.Q(is_sla_breached=True),
                name="ticket_sla_breached_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(title=""), name="ticket_title_not_empty"
            ),
            models.CheckConstraint(
                condition=models.Q(priority__in=[1, 2, 3]),
                name="ticket_priority_valid",
            ),
            # Chỉ ticket đã xử lý / đã đóng mới được có resolved_at
            models.CheckConstraint(
                condition=models.Q(resolved_at__isnull=True)
                | models.Q(status__in=["resolved", "closed"]),
                name="ticket_resolved_at_only_when_done",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} {self.title}" if self.pk else self.title

    @property
    def sla_deadline(self):
        return self.created_at + timedelta(hours=self.SLA_HOURS[self.priority])
