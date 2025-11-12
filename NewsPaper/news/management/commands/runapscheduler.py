# news/management/commands/runapscheduler.py
import logging
import sys
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from news.models import Subscription, Post, Category
from datetime import timedelta
from django.utils import timezone

# Настройка логирования
logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    """Еженедельная рассылка новых статей подписчикам"""
    print("🔄 Запуск еженедельной рассылки...")

    try:
        # Определяем период - последние 7 дней
        week_ago = timezone.now() - timedelta(days=7)

        # Получаем все новые статьи за неделю
        new_posts = Post.objects.filter(
            created_at__gte=week_ago,
            post_type=Post.ARTICLE
        ).order_by('-created_at')

        if not new_posts.exists():
            print("ℹ️ За последнюю неделю не было новых статей")
            return

        # Группируем статьи по категориям
        posts_by_category = {}
        for post in new_posts:
            for category in post.categories.all():
                if category.id not in posts_by_category:
                    posts_by_category[category.id] = {
                        'category': category,
                        'posts': []
                    }
                # Добавляем пост только если его еще нет в списке
                if post not in posts_by_category[category.id]['posts']:
                    posts_by_category[category.id]['posts'].append(post)

        # Отправляем письма подписчикам
        emails_sent = 0
        for category_id, data in posts_by_category.items():
            category = data['category']
            posts = data['posts']

            # Получаем всех подписчиков категории
            subscriptions = Subscription.objects.filter(category=category)

            for subscription in subscriptions:
                user = subscription.user

                # Формируем HTML-письмо
                html_content = render_to_string(
                    'news/email/weekly_newsletter.html',
                    {
                        'user': user,
                        'category': category,
                        'posts': posts,
                        'week_ago': week_ago,
                        'domain': '127.0.0.1:8000',
                    }
                )

                # Отправляем письмо
                try:
                    msg = EmailMultiAlternatives(
                        subject=f'📰 Еженедельная подборка статей в категории "{category.name}"',
                        body=f'Здравствуйте, {user.username}! За последнюю неделю в категории "{category.name}" появилось {len(posts)} новых статей.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email],
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
                    emails_sent += 1
                    print(f"✅ Отправлено письмо пользователю {user.username}")

                except Exception as e:
                    print(f"❌ Ошибка отправки письма {user.username}: {e}")

        print(f"📧 Еженедельная рассылка завершена. Отправлено писем: {emails_sent}")

    except Exception as e:
        print(f"❌ Критическая ошибка в рассылке: {e}")


def test_scheduler():
    """Тестовая функция для проверки работы планировщика"""
    print("🕒 APScheduler работает...")


def delete_old_job_executions(max_age=604_800):
    """Удаляем неактуальные задачи старше max_age секунд"""
    try:
        DjangoJobExecution.objects.delete_old_job_executions(max_age)
        print("✅ Удалены старые выполнения задач")
    except Exception as e:
        print(f"❌ Ошибка при удалении старых задач: {e}")


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        # Настройка вывода в консоль
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            stream=sys.stdout
        )

        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Добавляем еженедельную рассылку (каждый понедельник в 9:00 утра)
        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(
                day_of_week="mon",
                hour="9",
                minute="00"
            ),
            id="send_weekly_newsletter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✅ Добавлена задача: 'send_weekly_newsletter' (понедельник 9:00)")

        # Добавляем тестовую задачу для проверки (каждые 30 секунд) - используем именованную функцию
        scheduler.add_job(
            test_scheduler,
            trigger=CronTrigger(second="*/30"),
            id="test_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✅ Добавлена тестовая задача: 'test_job' (каждые 30 секунд)")

        # Добавляем очистку старых задач (каждое воскресенье в 23:59)
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="sun",
                hour="23",
                minute="59"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("✅ Добавлена задача: 'delete_old_job_executions' (воскресенье 23:59)")

        # Выводим информацию о задачах
        print("\n" + "=" * 50)
        print("📅 Запланированные задачи APScheduler:")
        print("   • send_weekly_newsletter - понедельник 9:00")
        print("   • test_job - каждые 30 секунд")
        print("   • delete_old_job_executions - воскресенье 23:59")
        print("=" * 50)
        print("🚀 Планировщик запущен. Для остановки нажмите Ctrl+C")
        print("=" * 50 + "\n")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            print("\n🛑 Остановка планировщика...")
            scheduler.shutdown()
            print("✅ Планировщик остановлен")
        except Exception as e:
            logger.error(f"❌ Ошибка планировщика: {e}")