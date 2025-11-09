from django.urls import path
from .views import (
    NewsCreate, NewsUpdate, NewsDelete,
    ArticleCreate, ArticleUpdate, ArticleDelete,
    NewsList, ArticleList, PostDetail
)

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('articles/', ArticleList.as_view(), name='article_list'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),

    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),

    path('articles/create/', ArticleCreate.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdate.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
]