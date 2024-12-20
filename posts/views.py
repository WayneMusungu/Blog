from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from posts.filters import PostFilter
from posts.models import Category, Comment, Post
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from posts.pagination import SmallResultSetPagination
from posts.serializers import CommentSerializer, HomePostSerializer, PostSerializer
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from silk.profiling.profiler import silk_profile
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    SuggesterFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from posts.documents import PostDocument
from posts.serializers import PostDocumentSerializer

# Create your views here.

# API VIEWS
class UserPostCreateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all posts created by all authenticated user/users.
        """
        posts = Post.objects.all()
        serializer = HomePostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new post for the authenticated user.
        """
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """
        Update a specific post created by the authenticated user.
        """
        post = get_object_or_404(Post, id=id, author=request.user)
        serializer = PostSerializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """
        Delete a specific post created by the authenticated user.
        """
        post = get_object_or_404(Post, id=id, author=request.user)
        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class PostCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        """
        Retrieve a post by its ID with all comments.
        """
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        """
        Create a comment on the retrieved post.
        """
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)  # Link the post and the author
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, post_id, comment_id):
        """
        Update a user's comment on a specific post.
        """
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post)

        # Ensure the comment belongs to the authenticated user
        if comment.author != request.user:
            return Response({"error": "You are not allowed to update this comment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the updated comment
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):
        """
        Delete a user's comment on a specific post.
        """
        post = get_object_or_404(Post, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id, post=post)

        # Ensure the comment belongs to the authenticated user
        if comment.author != request.user:
            return Response({"error": "You are not allowed to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

        # Delete the comment
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
    
class UserPostsMine(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = self.request.user
        
        # posts = user.user_posts.select_related('author').prefetch_related('categories')
        posts = Post.objects.filter(author=user).select_related('author').prefetch_related('categories')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


 
# GENERIC VIEWS
class PostsListView(generics.ListAPIView):
    serializer_class = HomePostSerializer
    pagination_class = SmallResultSetPagination

    def get_queryset(self):
        queryset = Post.objects.all()
        author_username = self.request.query_params.get('author')
        if author_username:
            queryset = queryset.filter(author__username__iexact=author_username)
            if not queryset:
                raise NotFound(f"No posts found for author {author_username}")
        return queryset 


class UserPosts(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    @silk_profile(name="User's Post") 
    def get_queryset(self):
        user = self.request.user
        # Using select_related for author and prefetch_related for categories
        return user.user_posts.select_related('author').prefetch_related('categories')
    
    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
    

class UserPostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)
    
    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        
        if post.author != self.request.user:
            raise PermissionDenied("You are not allowed to modify this post.")
                
        return post
     

class PostCommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return Comment.objects.filter(post=post)
    
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)
        
        
class PostCommentUpdateRetrieveDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        
        comment = get_object_or_404(Comment, post=post, id=self.kwargs['comment_id'])
                
        if comment.author != self.request.user:
            raise PermissionDenied("You are not allowed to modify this comment.")
        
        return comment
    

class SearchPostsByCategoryView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = HomePostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter
    permission_classes = []
    

class PostDocumentView(DocumentViewSet):
    document = PostDocument
    serializer_class = PostDocumentSerializer

    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
        SuggesterFilterBackend
    ]

    search_fields = (
        'title',
    )

    filter_fields = {
        'categories': 'categories.id'
    }

    suggester_fields = {
        'title': {
            'field': 'title.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
        },
    }