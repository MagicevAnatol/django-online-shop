from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class UserSignUpSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        Profile.objects.create(
            user=user,
            full_name=validated_data['name']
        )
        return user


class AvatarSerializer(serializers.Serializer):
    src = serializers.ImageField(source='avatar_src')
    alt = serializers.CharField(source='avatar_alt')


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = AvatarSerializer(source='*')

    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'phone', 'avatar']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'profile']
