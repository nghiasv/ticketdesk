from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
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
    fields = ["title", "description", "category", "priority"]
    success_url = reverse_lazy("tickets:list")
