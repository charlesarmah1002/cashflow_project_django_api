from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        return Response(serializer.to_representation(serializer.save()), status=201)

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    def get_object(self): return self.request.user

class LoginView(TokenObtainPairView): pass
class RefreshView(TokenRefreshView): pass
