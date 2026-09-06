from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Business, User

class BusinessSerializer(serializers.ModelSerializer):
    class Meta: model = Business; fields = ("id", "name", "created_at")

class UserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    class Meta: model = User; fields = ("id", "email", "name", "business", "created_at")

class RegisterSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists(): raise serializers.ValidationError("A user with this email already exists.")
        return value
    @transaction.atomic
    def create(self, validated_data):
        business = Business.objects.create(name=validated_data.pop("business_name"))
        return User.objects.create_user(business=business, **validated_data)
    def to_representation(self, user):
        refresh = RefreshToken.for_user(user)
        return {"user": UserSerializer(user).data, "access": str(refresh.access_token), "refresh": str(refresh)}
