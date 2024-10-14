from django.urls import path

from posts.views import PostCommentAPIView, PostsListView, UserPostCreateListView, UserPostRetrieveUpdateDestroyView, UserPosts


urlpatterns = [
    # APIVIEW
    path('v1/posts/', UserPostCreateListView.as_view(), name='user-post-list-create'),
    path('v1/posts/<int:id>/', UserPostCreateListView.as_view(), name='user-post-update-delete'),
    path('v1/posts/<int:post_id>/comments/', PostCommentAPIView.as_view(), name='post-comment-list-create'),
    path('v1posts/<int:post_id>/comments/<int:comment_id>/', PostCommentAPIView.as_view(), name='post-comment-update-delete'),
    
    # GENERIC VIEW
    path('v2/posts/', PostsListView.as_view(), name='post-list'),
    path('v2/post/', UserPosts.as_view(), name='user-post-list-create'),
    path('v2/post/<pk>', UserPostRetrieveUpdateDestroyView.as_view(), name='post-detail'),

]