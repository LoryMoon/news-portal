from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post
from .forms import PostForm

class NewsList(ListView):
    model = Post
    template_name = 'news_list.html'
    context_object_name = 'news'

    def get_queryset(self):
        return Post.objects.filter(post_type='NW').order_by('-created_at')


class ArticleList(ListView):
    model = Post
    template_name = 'article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR').order_by('-created_at')

class PostDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

class NewsCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class NewsUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class NewsDelete(DeleteView):
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')


class ArticleCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'article_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class ArticleUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'article_edit.html'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class ArticleDelete(DeleteView):
    model = Post
    template_name = 'article_delete.html'
    success_url = reverse_lazy('article_list')

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')