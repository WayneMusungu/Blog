from django.urls import path

from posts.views import PostCommentAPIView, PostDetailView, UserPostCreateListView, UserPosts


urlpatterns = [
    # APIVIEW
    path('posts/', UserPostCreateListView.as_view(), name='user-post-list-create'),
    path('posts/<int:id>/', UserPostCreateListView.as_view(), name='user-post-update-delete'),
    path('posts/<int:post_id>/comments/', PostCommentAPIView.as_view(), name='post-comment-list-create'),
    path('posts/<int:post_id>/comments/<int:comment_id>/', PostCommentAPIView.as_view(), name='post-comment-update-delete'),

]