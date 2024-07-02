import json

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.files.storage import default_storage
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSignUpSerializer, UserSerializer
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from products.signals import move_cart_to_user


class SignUpView(APIView):
    def post(self, request):
        print(request.data)
        data_string = list(request.data.keys())[0]
        data_dict = json.loads(data_string)
        print(data_dict)
        serializer = UserSignUpSerializer(data=data_dict)
        if serializer.is_valid():
            user = serializer.save()
            username = data_dict.get("username")
            password = data_dict.get("password")
            user = authenticate(username=username, password=password)
            old_session_key = request.session.session_key
            if user is not None:
                login(request, user)
                move_cart_to_user(request, user, old_session_key)
                return Response({"message": "User created and logged in successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "User authenticated but not logged in"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    def post(self, request):
        if request.data.get("username"):
            username = request.data.get("username")
            password = request.data.get("password")
        else:
            data_string = list(request.data.keys())[0]
            data_dict = json.loads(data_string)
            username = data_dict.get("username")
            password = data_dict.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "User signed in successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class SignOutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "User signed out successfully"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        data = request.data

        profile_data = {
            'full_name': data.get('fullName'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'avatar_src': data.get('avatar', {}).get('src'),
            'avatar_alt': data.get('avatar', {}).get('alt')
        }

        serializer = UserSerializer(instance=user, data={'profile': profile_data}, partial=True)

        if serializer.is_valid():
            profile = user.profile
            profile.full_name = profile_data['full_name']
            profile.email = profile_data['email']
            profile.phone = profile_data['phone']
            profile.save()

            return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data['currentPassword']
        new_password = request.data['newPassword']
        if not user.check_password(current_password):
            return Response({"currentPassword": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


class AvatarUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        avatar = request.FILES.get('avatar')
        if avatar:
            if user.profile.avatar_src:
                try:
                    if default_storage.exists(user.profile.avatar_src.name):
                        default_storage.delete(user.profile.avatar_src.name)
                except Exception as e:
                    return Response({"error": f"Failed to delete old avatar: {str(e)}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            user.profile.avatar_src = avatar
            user.profile.save()
            return Response({"message": "Avatar updated successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "No avatar file provided"}, status=status.HTTP_400_BAD_REQUEST)
