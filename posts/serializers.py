from rest_framework import serializers
from posts.models import Category, Comment, Post

class HomePostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Post
        fields = ['title', 'body', 'author', 'created_on', 'updated_on']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_on']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def create(self, validated_data):
        # Create a new category instance
        category = Category.objects.create(**validated_data)
        return category


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comments = CommentSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, required=True)
    
    class Meta:
        model = Post
        fields = ['id','title', 'body', 'author', 'categories', 'comments']
        
    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        post = Post.objects.create(**validated_data)

        for category_data in categories_data:
            # Normalize category name to lowercase
            category_data['name'] = category_data['name'].lower()  
            category, created = Category.objects.get_or_create(**category_data)
            post.categories.add(category)

        return post
        

