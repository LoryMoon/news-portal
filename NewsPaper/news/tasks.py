from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, Post, Category


@shared_task
def send_new_post_notification(post_id):
    try:
        post = Post.objects.get(id=post_id)
        categories = post.categories.all()

        content_type = "статью" if post.post_type == Post.ARTICLE else "новость"

        for category in categories:
            subscriptions = Subscription.objects.filter(category=category)

            for subscription in subscriptions:
                user = subscription.user

                html_content = render_to_string(
                    'news/email/new_post_notification.html',
                    {
                        'post': post,
                        'username': user.username,
                        'domain': '127.0.0.1:8000',
                        'content_type': content_type,
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=f'Новая {content_type}: {post.title}',
                    body=post.content[:50] + '...',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

        return f"Уведомления отправлены для поста {post.title}"

    except Exception as e:
        return f"Ошибка отправки уведомлений: {e}"


@shared_task
def send_weekly_newsletter():
    try:
        week_ago = timezone.now() - timedelta(days=7)
        new_posts = Post.objects.filter(
            created_at__gte=week_ago,
            post_type=Post.ARTICLE
        ).order_by('-created_at')

        if not new_posts.exists():
            return "Нет новых статей за неделю"

        posts_by_category = {}
        for post in new_posts:
            for category in post.categories.all():
                if category.id not in posts_by_category:
                    posts_by_category[category.id] = {
                        'category': category,
                        'posts': []
                    }
                if post not in posts_by_category[category.id]['posts']:
                    posts_by_category[category.id]['posts'].append(post)

        emails_sent = 0
        for category_id, data in posts_by_category.items():
            category = data['category']
            posts = data['posts']

            subscriptions = Subscription.objects.filter(category=category)

            for subscription in subscriptions:
                user = subscription.user

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

                msg = EmailMultiAlternatives(
                    subject=f'📰 Еженедельная подборка статей в категории "{category.name}"',
                    body=f'Здравствуйте, {user.username}! За последнюю неделю в категории "{category.name}" появилось {len(posts)} новых статей.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                emails_sent += 1

        return f"Еженедельная рассылка завершена. Отправлено писем: {emails_sent}"

    except Exception as e:
        return f"Ошибка еженедельной рассылки: {e}"


@shared_task
def cleanup_old_tasks():
    return "Очистка выполнена"