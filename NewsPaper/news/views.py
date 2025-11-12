
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from .models import Post, Author, Category, Subscription
from .filters import NewsFilter
from .forms import NewsForm, ArticleForm
from datetime import datetime
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


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
        context['categories'] = Category.objects.all()

        if self.request.user.is_authenticated:
            context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
            subscribed_categories = Subscription.objects.filter(user=self.request.user).values_list('category_id',
                                                                                                    flat=True)
            context['subscribed_categories'] = list(subscribed_categories)

            yesterday = timezone.now() - timedelta(days=1)

            user_news_count = Post.objects.filter(
                author__user=self.request.user,
                post_type=Post.NEWS,
                created_at__gte=yesterday
            ).count()

            user_articles_count = Post.objects.filter(
                author__user=self.request.user,
                post_type=Post.ARTICLE,
                created_at__gte=yesterday
            ).count()

            context['user_news_count'] = user_news_count
            context['user_articles_count'] = user_articles_count

        return context


# Остальные представления остаются без изменений...
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

    def get_form_kwargs(self):
        """Передаем request в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post_type = Post.NEWS

        if not self.request.user.groups.filter(name='authors').exists():
            raise PermissionDenied("Только авторы могут создавать новости")

        author, created = Author.objects.get_or_create(user=self.request.user)
        self.object.author = author

        self.object.save()
        form.save_m2m()

        return super().form_valid(form)


class NewsUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/news_edit.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.NEWS)


class NewsDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post_type = Post.ARTICLE

        if not self.request.user.groups.filter(name='authors').exists():
            raise PermissionDenied("Только авторы могут создавать статьи")

        author, created = Author.objects.get_or_create(user=self.request.user)
        self.object.author = author

        self.object.save()
        form.save_m2m()

        return super().form_valid(form)


class ArticleUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = ArticleForm
    model = Post
    template_name = 'news/article_edit.html'
    permission_required = ('news.change_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


class ArticleDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'news/article_delete.html'
    success_url = reverse_lazy('news_list')
    permission_required = ('news.delete_post',)

    def get_queryset(self):
        return Post.objects.filter(post_type=Post.ARTICLE)


@login_required
def subscribe_to_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if not Subscription.objects.filter(user=request.user, category=category).exists():
        Subscription.objects.create(user=request.user, category=category)
        messages.success(request, f'Вы успешно подписались на категорию "{category.name}"')
    else:
        messages.info(request, f'Вы уже подписаны на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


@login_required
def unsubscribe_from_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    subscription = Subscription.objects.filter(user=request.user, category=category)
    if subscription.exists():
        subscription.delete()
        messages.success(request, f'Вы отписались от категории "{category.name}"')
    else:
        messages.info(request, f'Вы не были подписаны на категорию "{category.name}"')

    return redirect(request.META.get('HTTP_REFERER', 'news_list'))


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