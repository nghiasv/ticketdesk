from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Prefetch, Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.accounts.models import User

from .models import Ticket


class TicketQuerysetMixin:
    def get_queryset(self):
        # Quyền xem ticket theo mục 3.4 tài liệu yêu cầu
        user = self.request.user
        qs = Ticket.objects.select_related("category", "assignee", "created_by")
        if user.role == User.Role.MANAGER:
            return qs
        if user.role == User.Role.AGENT:
            return qs.filter(Q(assignee=user) | Q(assignee__isnull=True))
        if user.role == User.Role.CUSTOMER:
            return qs.filter(created_by=user)
        return qs.none()


class TicketListView(LoginRequiredMixin, TicketQuerysetMixin, ListView):
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Đếm trên cùng queryset đã lọc theo quyền, nên mỗi người chỉ thấy số của mình
        context["stats"] = self.get_queryset().aggregate(
            total=Count("id"),
            new=Count("id", filter=Q(status=Ticket.Status.NEW)),
            in_progress=Count("id", filter=Q(status=Ticket.Status.IN_PROGRESS)),
            done=Count(
                "id",
                filter=Q(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED]),
            ),
        )
        return context


class TicketDetailView(LoginRequiredMixin, TicketQuerysetMixin, DetailView):
    pass


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = ["title", "description", "category", "priority"]
    success_url = reverse_lazy("tickets:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, TicketQuerysetMixin, UpdateView):
    model = Ticket
    fields = ["title", "description", "category", "priority"]
    success_url = reverse_lazy("tickets:list")


class TicketDeleteView(LoginRequiredMixin, TicketQuerysetMixin, DeleteView):
    model = Ticket
    success_url = reverse_lazy("tickets:list")


class TicketStatsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "tickets/ticket_stats.html"

    def test_func(self):
        # Chỉ quản lý được xem thống kê toàn hệ thống, người khác nhận 403
        return self.request.user.role == User.Role.MANAGER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Đếm ticket theo trạng thái (annotate + GROUP BY) -> [{'status': 'new', 'total': 12}, ...]
        by_status = (
            Ticket.objects.values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )
        context["status_rows"] = [
            (row["status"], Ticket.Status(row["status"]).label, row["total"])
            for row in by_status
        ]

        # Tổng số ticket, số chưa có người xử lý và số quá hạn SLA
        context.update(
            Ticket.objects.aggregate(
                total=Count("id"),
                unassigned=Count("id", filter=Q(assignee__isnull=True)),
                breached=Count("id", filter=Q(is_sla_breached=True)),
            )
        )

        # 3 ticket chưa đóng mới nhất của mỗi nhân viên. Prefetch có cắt [:3] được Django
        # dịch thành ROW_NUMBER() OVER (PARTITION BY assignee_id), nên chỉ tốn 1 query
        # cho mọi nhân viên và chỉ tải đúng 3 dòng mỗi người, thay vì 1 query mỗi nhân viên.
        recent_open = Prefetch(
            "assigned_tickets",
            queryset=Ticket.objects.exclude(status=Ticket.Status.CLOSED).order_by(
                "-created_at"
            )[:3],
            to_attr="recent_open",
        )

        # Số ticket đang mở (chưa đóng) của từng nhân viên
        context["agents"] = (
            User.objects.filter(role=User.Role.AGENT)
            .annotate(
                total=Count("assigned_tickets"),
                open_count=Count(
                    "assigned_tickets",
                    filter=~Q(assigned_tickets__status=Ticket.Status.CLOSED),
                ),
            )
            .prefetch_related(recent_open)
            .order_by("-open_count")
        )
        return context
