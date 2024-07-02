from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class UserSignUpSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
        )
        Profile.objects.create(
            user=user,
            full_name=validated_data['name'],
            email=validated_data['email'],
        )
        return user


class AvatarSerializer(serializers.Serializer):
    src = serializers.ImageField(source='avatar_src')
    alt = serializers.CharField(source='avatar_alt')


class UserSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source='profile.full_name')
    email = serializers.EmailField(source='profile.email')
    phone = serializers.CharField(source='profile.phone')
    avatar = AvatarSerializer(source='profile')

    class Meta:
        model = User
        fields = ['fullName', 'email', 'phone', 'avatar']
