from django import forms
from django.core.exceptions import ValidationError
from .models import Post
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group



class NewsForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
        }

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