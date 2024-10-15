from django.test import TestCase
from authentication.models import User
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='janedoe@test.com',
            first_name='Jane',
            last_name='Doe',
            username='testuser',
            password='password123',
        )

    def tearDown(self):
        self.user.delete()

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'janedoe@test.com')
        self.assertTrue(self.user.is_active)

    def test_str_representation(self):
        self.assertEqual(str(self.user), 'janedoe@test.com')

    def test_user_password_is_hashed(self):
        self.assertNotEqual(self.user.password, 'password123')
        self.assertTrue(self.user.check_password('password123'))

    def test_invalid_email(self):
        """Test that a user cannot be created with an invalid email format"""
        invalid_email = 'invalid-email'
        with self.assertRaises(ValidationError):
            user = User(
                email=invalid_email,
                first_name='Invalid',
                last_name='Email',
                username='invaliduser',
                password='password123',
            )
            # Manually trigger full clean to validate the email
            user.full_clean()  # This should raise a ValidationError
            user.save()

    def test_unique_username(self):
        """Test that creating a user with the same username raises an IntegrityError"""
        with transaction.atomic():  # Ensure the IntegrityError is isolated
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    email='anotheremail@test.com',
                    first_name='John',
                    last_name='Smith',
                    username='testuser',  # Same username as self.user
                    password='password123',
                )
