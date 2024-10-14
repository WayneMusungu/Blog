from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from authentication.models import User
from authentication.serializers import LoginSerializer, UserSerializer

# Create your views here.

class UserRegistration(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
 
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user, tokens = serializer.authenticate_user()
            if user is not None:
                return Response(tokens, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Authentication failed', 'status': False}, status=status.HTTP_404_NOT_FOUND)
        
