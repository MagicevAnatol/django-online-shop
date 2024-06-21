import json

from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSignUpSerializer


class SignUpView(APIView):
    def post(self, request):
        data_string = list(request.data.keys())[0]
        data_dict = json.loads(data_string)
        serializer = UserSignUpSerializer(data=data_dict)
        if serializer.is_valid():
            user = serializer.save()
            username = data_dict.get("username")
            password = data_dict.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
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
