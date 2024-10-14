from django.urls import path

from posts.views import PostCommentAPIView, PostCommentUpdateRetrieveDestroyView, PostCommentView, PostsListView, UserPostCreateListView, UserPostRetrieveUpdateDestroyView, UserPosts


urlpatterns = [
    # APIVIEW
    path('v1/posts/', UserPostCreateListView.as_view(), name='user-post-list-create'),
    path('v1/posts/<int:id>/', UserPostCreateListView.as_view(), name='user-post-update-delete'),
    path('v1/posts/<int:post_id>/comments/', PostCommentAPIView.as_view(), name='post-comment-list-create'),
    path('v1/posts/<int:post_id>/comments/<int:comment_id>/', PostCommentAPIView.as_view(), name='post-comment-update-delete'),
    
    # GENERIC VIEW
    path('v2/posts/', PostsListView.as_view(), name='post-list'),
    path('v2/post/', UserPosts.as_view(), name='user-post-list-create'),
    path('v2/post/<int:post_id>', UserPostRetrieveUpdateDestroyView.as_view(), name='post-retrieve-update-destroy'),
    path('v2/post/<int:post_id>/comment/', PostCommentView.as_view(), name='post-comment-create-list'),
    path('v2/post/<int:post_id>/comments/<int:comment_id>/', PostCommentUpdateRetrieveDestroyView.as_view(), name='post-comment-retrieve-update-delete'),
]