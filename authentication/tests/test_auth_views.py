from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from authentication.models import User


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