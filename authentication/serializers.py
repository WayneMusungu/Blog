from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from authentication.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.tasks import send_thank_you_email


def validate_special_character(value):
    # This is a custom validator that adds aditional layer of complexity to ensure passwords
    # includes characters beyond alpha numeric ones
    pattern = r'[\W_]+'
    if not re.search(pattern, value):
        raise ValidationError('Password must contain at least one special character eg."~!@#$%^&*"')


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=35, required=True)
    last_name = serializers.CharField(max_length=35, required=True)
    password = serializers.CharField(write_only=True, validators=[validate_special_character])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'confirm_password')
   

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password do not match"})
        return data

    def create(self, validated_data):
        # Remove confirm_password before creating the user
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def authenticate_user(self):
        email = self.validated_data['email']
        password = self.validated_data['password']
        
        user = authenticate(email=email, password=password)
        
        if user is None:
            return None, None
        
        refresh = RefreshToken.for_user(user)
        tokens = {
            'status': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        
        # Trigger the thank-you email task
        send_thank_you_email.delay(user.email)
        
        return user, tokens