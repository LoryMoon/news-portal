from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Author, Category
from .filters import NewsFilter
from .forms import NewsForm, ArticleForm
from datetime import datetime


class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(post_type=Post.NEWS)
        self.filterset = NewsFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class NewsSearch(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news/news_search.html'
    context_object_name = 'news_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.filter(post_type=Post.NEWS)
        self.filterset = NewsFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['time_now'] = datetime.utcnow()
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'news/news_detail.html'
    context_object_name = 'news'


class NewsCreate(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    login_url = '/admin/login/'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.NEWS

        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        return super().form_valid(form)


class NewsUpdate(LoginRequiredMixin, UpdateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    login_url = '/admin/login/'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class NewsDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/admin/login/'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class ArticleCreate(LoginRequiredMixin, CreateView):
    form_class = ArticleForm
    model = Post
    template_name = 'news/article_edit.html'
    login_url = '/admin/login/'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.ARTICLE

        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        return super().form_valid(form)


class ArticleUpdate(LoginRequiredMixin, UpdateView):
    form_class = ArticleForm
    model = Post
    template_name = 'news/article_edit.html'
    login_url = '/admin/login/'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class ArticleDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    login_url = '/admin/login/'

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)