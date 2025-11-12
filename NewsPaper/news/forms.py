
from django import forms
from django.core.exceptions import ValidationError
from .models import Post
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta


class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.request and hasattr(self, 'instance'):
            user = self.request.user

            yesterday = timezone.now() - timedelta(days=1)
            today_news_count = Post.objects.filter(
                author__user=user,
                post_type=Post.NEWS,
                created_at__gte=yesterday
            ).count()

            if today_news_count >= 3:
                raise ValidationError(
                    "Вы не можете публиковать более 3 новостей в сутки. "
                    f"Сегодня вы уже опубликовали {today_news_count} новостей."
                )

        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Заголовок должен содержать не менее 5 символов.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
        if len(content) < 20:
            raise ValidationError("Текст должен содержать не менее 20 символов.")
        return content


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.request and hasattr(self, 'instance'):
            user = self.request.user

            yesterday = timezone.now() - timedelta(days=1)
            today_articles_count = Post.objects.filter(
                author__user=user,
                post_type=Post.ARTICLE,
                created_at__gte=yesterday
            ).count()

            if today_articles_count >= 5:
                raise ValidationError(
                    "Вы не можете публиковать более 5 статей в сутки. "
                    f"Сегодня вы уже опубликовали {today_articles_count} статей."
                )

        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 5:
            raise ValidationError("Заголовок должен содержать не менее 5 символов.")
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
        if len(content) < 50:
            raise ValidationError("Текст статьи должен содержать не менее 50 символов.")
        return content


class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user