from django.conf import settings
from django.db import models


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"#{self.pk} {self.title}"
