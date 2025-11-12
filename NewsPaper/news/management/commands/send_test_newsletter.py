from django.core.management.base import BaseCommand
from news.management.commands.runapscheduler import send_weekly_newsletter


class Command(BaseCommand):
    help = "Send test weekly newsletter"

    def handle(self, *args, **options):
        self.stdout.write("Отправка тестовой рассылки...")
        send_weekly_newsletter()
        self.stdout.write(
            self.style.SUCCESS("Тестовая рассылка завершена!")
        )