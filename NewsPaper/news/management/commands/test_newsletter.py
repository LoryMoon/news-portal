
from django.core.management.base import BaseCommand
from news.management.commands.runapscheduler import send_weekly_newsletter


class Command(BaseCommand):
    help = "Test weekly newsletter"

    def handle(self, *args, **options):
        self.stdout.write("Тестирование еженедельной рассылки...")
        send_weekly_newsletter()
        self.stdout.write(
            self.style.SUCCESS("Тест рассылки завершен!")
        )