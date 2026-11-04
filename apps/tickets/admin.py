from django.contrib import admin

from .models import Category, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "priority", "assignee", "created_at"]
    list_filter = ["status", "priority", "category"]
    search_fields = ["title", "description"]
    autocomplete_fields = ["assignee"]


admin.site.register(Category)
