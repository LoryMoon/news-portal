from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'post_type',
            'categories',
            'author'
        ]

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError("Заголовок должен содержать не менее 5 символов")
        return title

    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) < 20:
            raise forms.ValidationError("Текст должен содержать не менее 20 символов")
        return content
