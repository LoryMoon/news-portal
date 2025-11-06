from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post
from datetime import datetime

class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context

class NewsDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'