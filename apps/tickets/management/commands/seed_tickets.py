import random
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.tickets.models import Category, Ticket

CATEGORY_NAMES = ["Phần cứng", "Phần mềm", "Mạng", "Tài khoản", "Khác"]
TITLES = [
    "Không đăng nhập được",
    "Máy in không hoạt động",
    "Mất kết nối mạng",
    "Lỗi khi xuất báo cáo",
    "Quên mật khẩu",
    "Phần mềm bị treo",
    "Yêu cầu cấp quyền truy cập",
    "Email không gửi được",
]
# Mật khẩu chung cho nhân viên do seed tạo, chỉ dùng ở môi trường dev
SEED_AGENT_PASSWORD = "ticketdesk123"


class Command(BaseCommand):
    help = "Tạo dữ liệu ticket mẫu số lượng lớn để đo hiệu năng truy vấn"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10_000)
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Xoá ticket do lệnh này tạo trước đó rồi mới tạo lại",
        )
        parser.add_argument(
            "--agents",
            type=int,
            default=5,
            help="Số nhân viên hỗ trợ tối thiểu (tạo thêm nhanvien01, nhanvien02... nếu thiếu)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Ngày tạo ticket rải ngẫu nhiên trong bấy nhiêu ngày gần nhất",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Hạt giống random, truyền cùng một số để lần nào cũng ra cùng dữ liệu",
        )

    @transaction.atomic
    def handle(self, *args, count, clear, agents, days, seed, **options):
        rng = random.Random(seed)

        customers = list(User.objects.filter(role=User.Role.CUSTOMER))
        if not customers:
            raise CommandError(
                "Cần ít nhất 1 user vai trò khách hàng (chạy loaddata demo trước)"
            )
        agent_users = self.ensure_agents(agents)

        if clear:
            deleted, _ = Ticket.objects.filter(title__startswith="[seed]").delete()
            self.stdout.write(f"Đã xoá {deleted} ticket seed cũ")

        categories = [
            Category.objects.get_or_create(name=name)[0] for name in CATEGORY_NAMES
        ]

        now = timezone.now()
        tickets = []
        created_dates = []
        for i in range(1, count + 1):
            status = rng.choice(Ticket.Status.values)
            priority = rng.choice(Ticket.Priority.values)
            created_at = now - timedelta(seconds=rng.randint(0, days * 24 * 3600))
            created_dates.append(created_at)
            sla = timedelta(hours=Ticket.SLA_HOURS[priority])

            resolved_at = None
            if status in Ticket.DONE_STATUSES:
                # Xử lý xong sau 30 phút tới 5 ngày, không vượt quá hiện tại
                resolved_at = min(
                    created_at + timedelta(minutes=rng.randint(30, 5 * 24 * 60)), now
                )
                breached = resolved_at > created_at + sla
            else:
                breached = now > created_at + sla

            tickets.append(
                Ticket(
                    title=f"[seed] {rng.choice(TITLES)} #{i}",
                    description="Mô tả mẫu sinh bởi lệnh seed_tickets.",
                    status=status,
                    priority=priority,
                    category=rng.choice(categories),
                    created_by=rng.choice(customers),
                    # Ticket Mới chưa có người xử lý; các trạng thái khác đã được giao
                    assignee=rng.choice(agent_users)
                    if status != Ticket.Status.NEW
                    else None,
                    resolved_at=resolved_at,
                    is_sla_breached=breached,
                )
            )

        # bulk_create gom nhiều INSERT vào một câu, nhanh hơn rất nhiều so với save() từng ticket
        created = Ticket.objects.bulk_create(tickets, batch_size=1000)

        # auto_now_add luôn ghi đè created_at bằng thời điểm hiện tại khi INSERT,
        # nên phải gán lại ngày tạo ngẫu nhiên bằng một lượt UPDATE
        for obj, created_at in zip(created, created_dates, strict=True):
            obj.created_at = created_at
        Ticket.objects.bulk_update(created, ["created_at"], batch_size=1000)

        self.stdout.write(
            self.style.SUCCESS(
                f"Đã tạo {count} ticket, rải trong {days} ngày, {len(agent_users)} nhân viên"
            )
        )

    def ensure_agents(self, minimum):
        agent_users = list(User.objects.filter(role=User.Role.AGENT).order_by("id"))
        password = make_password(SEED_AGENT_PASSWORD)
        n = 1
        while len(agent_users) < minimum:
            username = f"nhanvien{n:02d}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "role": User.Role.AGENT,
                    "password": password,
                    "first_name": f"Nhân viên {n:02d}",
                },
            )
            if created:
                agent_users.append(user)
                self.stdout.write(
                    f"Tạo nhân viên {username} (mật khẩu {SEED_AGENT_PASSWORD})"
                )
            n += 1
        return agent_users
