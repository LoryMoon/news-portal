
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import Post, Subscription


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_category_add(sender, instance, action, **kwargs):
    if action == "post_add":
        categories = instance.categories.all()

        content_type = "статью" if instance.post_type == Post.ARTICLE else "новость"

        for category in categories:
            subscriptions = Subscription.objects.filter(category=category)

            for subscription in subscriptions:
                user = subscription.user

                html_content = render_to_string(
                    'news/email/new_post_notification.html',
                    {
                        'post': instance,
                        'username': user.username,
                        'domain': '127.0.0.1:8000',
                        'content_type': content_type,
                    }
                )

                msg = EmailMultiAlternatives(
                    subject=f'Новая {content_type}: {instance.title}',
                    body=instance.content[:50] + '...',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()