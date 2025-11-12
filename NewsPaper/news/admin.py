from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment, Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'subscribed_at']
    list_filter = ['category', 'subscribed_at']

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostCategory)