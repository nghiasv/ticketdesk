from django.contrib import admin
from django.db.models import Count

from .models import Category, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "title",
        "status",
        "priority",
        "category_name",
        "customer_name",
        "assignee",
        "is_sla_breached",
        "created_at",
    ]
    # Cột dạng hàm (category_name, customer_name) làm admin không tự JOIN được nữa,
    # thiếu dòng này mỗi trang 100 ticket sinh thêm khoảng 200 query (N+1)
    list_select_related = ["category", "created_by", "assignee"]
    list_filter = ["status", "priority", "is_sla_breached", "category"]
    search_fields = ["code", "title", "description"]
    autocomplete_fields = ["assignee"]
    readonly_fields = ["code", "resolved_at", "is_sla_breached"]

    @admin.display(description="Danh mục", ordering="category__name")
    def category_name(self, obj):
        return obj.category.name

    @admin.display(description="Khách hàng", ordering="created_by__username")
    def customer_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "ticket_count"]
    search_fields = ["name"]

    def get_queryset(self, request):
        # Đếm sẵn bằng một câu GROUP BY, thay vì mỗi dòng gọi obj.tickets.count()
        return super().get_queryset(request).annotate(_ticket_count=Count("tickets"))

    @admin.display(description="Số ticket", ordering="_ticket_count")
    def ticket_count(self, obj):
        return obj._ticket_count
