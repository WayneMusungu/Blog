from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from authentication.models import User
from posts.models import Post, Category, Comment

class UserPostsAPIView(APITestCase):
    def setUp(self):
        # Create a user and a post
        self.user = User.objects.create_user(
            email='janedoe@test.com',
            first_name='Jane',
            last_name='Doe',
            username='janedoe',
            password='password123',
        )
        self.user_2 = User.objects.create_user(
            email='warren@test.com',
            first_name='Warren',
            last_name='Doe',
            username='warren',
            password='password123',
        )
        self.post = Post.objects.create(
            title='Introduction to Django',
            body='This is a post about Django',
            author=self.user,
        )
        self.category_one = Category.objects.create(
            name='Django',
        )
        self.category_two = Category.objects.create(
            name='Python',
        )
        self.post.categories.add(self.category_one, self.category_two)
        self.comment = Comment.objects.create(
            post = self.post,
            author = self.user,
            content = 'This is a comment about Django'
        )    
        self.comment_2 = Comment.objects.create(
            post = self.post,
            author = self.user_2,
            content = 'Django is fun'
        )
        
    def tearDown(self):
        # Delete the user, post, category, and comment
        self.comment.delete()
        self.comment_2.delete()
        self.post.delete()
        self.category_one.delete()
        self.category_two.delete()
        self.user.delete()
        
    def test_view_all_posts(self):
        url = reverse('post-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 2)
        
        # Verify the content of the post in the response
        post_data = response.data['results'][0]
        self.assertEqual(post_data['title'], self.post.title)
        self.assertEqual(post_data['body'], 'This is a post about Django')
        self.assertEqual(post_data['author'], 'janedoe')        
        
    def test_query_search_filter_author_no_post(self):
        url = reverse('post-list')
        data = {
            'author': 'warren'
        }
        response = self.client.get(url, data, format='json')        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "No posts found for author warren")   
 
    def test_query_search_filter_author(self):
        result = Post.objects.filter(author__username__iexact='janedoe').values('title', 'author__email')
        
        print("Query Result:", result)
        
        self.assertQuerySetEqual(
            result,
            [{'title': 'Introduction to Django', 'author__email': 'janedoe@test.com'}]
        )
