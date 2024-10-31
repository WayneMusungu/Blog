from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from authentication.models import User
from unittest.mock import patch


class UserRegistrationTest(APITestCase):

    def test_user_registration_success(self):
        """Test user registration with valid data"""
        url = reverse('register')
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'janedoe@example.com')
        
    def test_user_registration_passwords_not_matching(self):
        "Test user registration with non-matching passwords"
        url = reverse('register') 
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'Password@123',
            'confirm_password': 'Password@124'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)
        self.assertEqual(response.data['confirm_password'][0], "Password do not match")
        self.assertEqual(User.objects.count(), 0)
        
    def test_user_registration_invalid_email(self):
        """Test user registration with an invalid email"""
        url = reverse('register') 
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(response.data['email'][0], "Enter a valid email address.")
        self.assertEqual(User.objects.count(), 0)
        
    def test_user_registration_no_special_character_password(self):
        """Test user registration without special character in password"""
        url = reverse('register') 
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'Password must contain at least one special character eg."~!@#$%^&*"')
        self.assertEqual(User.objects.count(), 0)
        
 
class LoginViewTest(APITestCase):

    def setUp(self):
        # Create a user to authenticate
        self.user = User.objects.create_user(
            email='janedoe@example.com',
            first_name='Jane',
            last_name='Doe',
            username='janedoe',
            password='Password@123'
        )
        
    def tearDown(self):
        self.user.delete()
    
    @patch('authentication.serializers.send_thank_you_email.delay')
    def test_login_success_email_task_triggered(self, mock_send_email_task):
        """Test that a successful login triggers the thank-you email task"""
        url = reverse('login')
        data = {
            'email': 'janedoe@example.com',
            'password': 'Password@123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], True)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Check that the email task was called once with the correct argument
        mock_send_email_task.assert_called_once()
     
    @patch('authentication.serializers.send_thank_you_email.delay')   
    def test_login_does_not_trigger_email_task_on_failed_login(self, mock_send_email_task):
        """Test that the thank-you email task is not triggered if login fails"""
        url = reverse('login')
        data = {
            'email': 'jane@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], False)
        self.assertEqual(response.data['detail'], 'Authentication failed')
        
        # Ensure the email task was not triggered
        mock_send_email_task.assert_not_called()
        
    def test_login_user_does_not_exist(self):
        """Test login with non-existing user"""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'Password@123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], False)
        self.assertEqual(response.data['detail'], 'Authentication failed')
