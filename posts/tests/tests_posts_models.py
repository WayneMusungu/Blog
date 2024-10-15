from django.test import TestCase
from authentication.models import User
from posts.models import Post, Comment

# Tests for the Post model
class TestPostModel(TestCase):
    def setUp(self):
        # Create a user and a post
        self.user = User.objects.create_user(
            email='janedoe@test.com',
            first_name='Jane',
            last_name='Doe',
            username='testuser',
            password='password123',
        )
        self.post = Post.objects.create(
            title='Introduction to Django',
            body='This is a post about Django',
            author=self.user,
        )
        # Create another user
        self.another_user = User.objects.create_user(
            email='johndoe@test.com',
            first_name='John',
            last_name='Doe',
            username='johndoe',
            password='password456',
        )

    def tearDown(self):
        self.post.delete()
        self.user.delete()
        self.another_user.delete()

    def test_create_post(self):
        """Test that the post is created correctly"""
        self.assertEqual(self.post.title, 'Introduction to Django')
        self.assertEqual(self.post.body, 'This is a post about Django')
        self.assertEqual(self.post.author, self.user)

    def test_post_str(self):
        """Test the string representation of a post"""
        self.assertEqual(str(self.post), 'Introduction to Django by janedoe@test.com.')


# Tests for the Comment model
class TestCommentModel(TestCase):
    def setUp(self):
        # Create users and a post
        self.user = User.objects.create_user(
            email='janedoe@test.com',
            first_name='Jane',
            last_name='Doe',
            username='testuser',
            password='password123',
        )
        self.another_user = User.objects.create_user(
            email='johndoe@test.com',
            first_name='John',
            last_name='Doe',
            username='johndoe',
            password='password456',
        )
        self.post = Post.objects.create(
            title='Introduction to Django',
            body='This is a post about Django',
            author=self.user,
        )
        # Create a comment from another user
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.another_user,
            content='Great post! I found it very helpful.',
        )

    def tearDown(self):
        Comment.objects.filter(post=self.post).delete()
        self.comment.delete()
        self.post.delete()
        self.user.delete()
        self.another_user.delete()

    def test_create_comment(self):
        """Test that a comment is created correctly"""
        self.assertEqual(self.comment.content, 'Great post! I found it very helpful.')
        self.assertEqual(self.comment.author, self.another_user)
        self.assertEqual(self.comment.post, self.post)

    def test_comment_str(self):
        """Test the string representation of a comment"""
        self.assertEqual(
            str(self.comment),
            f"Comment by {self.another_user.username} on {self.comment.created_on}"
        )

    def test_multiple_comments(self):
        """Test that multiple comments can be added to a post"""
        # Add another comment
        another_comment = Comment.objects.create(
            post=self.post,
            author=self.user,  # Original user comments now
            content='Thanks for the feedback!',
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 2)
