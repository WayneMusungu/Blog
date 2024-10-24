from django.contrib import admin

from posts.models import Comment, Post, Category

# Register your models here.
admin.site.register(Comment)
admin.site.register(Post)
admin.site.register(Category)
