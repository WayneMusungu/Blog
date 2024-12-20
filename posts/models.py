from django.db import models
from authentication.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=30)
    
    class  Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Post(models.Model):
   title = models.CharField(max_length=200) 
   body = models.TextField()
   author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
   categories = models.ManyToManyField(Category, related_name='posts')
   created_on = models.DateTimeField(auto_now_add=True)
   updated_on = models.DateTimeField(auto_now=True)
   
   class Meta:
       ordering = ['-created_on']
   
   def __str__(self):
       return f"{self.title} by {self.author}."
   

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.created_on}"
    
    class Meta:
       ordering = ['-created_on']
   
