from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from .models import Post, Author, Category
from .filters import NewsFilter
from .forms import NewsForm, ArticleForm
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

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

        if self.request.user.is_authenticated:
            context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()

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


class NewsCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.NEWS

        if not self.request.user.groups.filter(name='authors').exists():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Только авторы могут создавать новости")

        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        return super().form_valid(form)

class NewsUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class NewsDelete(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'news/news_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = ('news.delete_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = ArticleForm
    model = Post
    template_name = 'news/article_edit.html'
    permission_required = ('news.add_post',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = Post.ARTICLE

        # Проверяем, является ли пользователь автором
        if not self.request.user.groups.filter(name='authors').exists():
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Только авторы могут создавать статьи")

        # Создаем или получаем Author
        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    form_class = ArticleForm
    model = Post
    template_name = 'news/article_edit.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)
1

class ArticleDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = ('news.delete_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)

def custom_permission_denied(request, exception):
    return render(request, '403.html', status=403)

@login_required
def become_author(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')

    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
        Author.objects.get_or_create(user=user)

        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(Post)
        permissions = Permission.objects.filter(content_type=content_type)

        for permission in permissions:
            user.user_permissions.add(permission)

    return redirect('/news/')
