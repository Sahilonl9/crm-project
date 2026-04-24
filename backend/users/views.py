# we create view for API

from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exceptions = True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),}, status= status.HTTP_201_CREATED)
    
class LoginView(APIView):
    permission_classes = (AllowAny)
    def post(self, request):
        from django.contrib.auth import authenticate
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password','')

        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access':str(refresh.access_token),
            'refresh':str(refresh),

        })

class RefreshView(APIView):
    permission_classes = (AllowAny)
    def post(self,request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail':'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            return Response({'access':str(token.access_token)})
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated)
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:  
            return Response({'detail':'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail':'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated) 
    serializer_class =UserSerializer

    def get_object(self):
        return self.request.user
            


