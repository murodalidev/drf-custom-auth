from django.db.models import Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.urls import reverse
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import jwt
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from ...models import User
from .serializer import RegisterSerializer, LoginSerializer, \
     SetNewPasswordSerializer, UserSerializer, UserOwnImageUpdateSerializer
from .permissions import IsOwnerForUser


class UserRegisterView(generics.GenericAPIView):
    # http://127.0.0.1:8000/user/v1/register/
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user_data['tokens'] = str(token)
        return Response({'success': True, 'data': user_data}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    # http://127.0.0.1:8000/user/v1/login/
    serializer_class = LoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class GetUserView(generics.RetrieveAPIView):
    # http://127.0.0.1:8000/user/v1/get-user/
    permission_classes = (IsAuthenticated, )
    serializer_class = UserUpdateSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        query = User.objects.get(id=user.id)
        serializer = self.get_serializer(query)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class SetNewPasswordView(generics.GenericAPIView):
    # http://127.0.0.1:8000/user/v1/password-change-complete/
    serializer_class = SetNewPasswordSerializer
    permission_classes = (AllowAny, )

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({'success': True, 'message': 'Successfully changed password'}, status=status.HTTP_200_OK)
        return Response({'success': False, 'message': 'Credentials is invalid'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserListView(generics.ListAPIView):
    # http://127.0.0.1:8000/user/v1/list/
    serializer_class = UserUpdateSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        q = self.request.GET.get('q')
        
        q_condition = Q()
        if q:
            q_condition = (Q(subject__icontains=q) | Q(phone=q))

        queryset = User.objects.filter(q_condition, team_condition, date_condition)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            count = queryset.count()
            return Response({'success': True, 'data': serializer.data, 'count': count}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'data': 'queryset did not matching'}, status=status.HTTP_404_NOT_FOUND)


class UserUpdateView(generics.RetrieveUpdateAPIView):
    # http://127.0.0.1:8000/user/v1/update/<id>/
    serializer_class = UserUpdateSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminUser, )

    def get(self, request, *args, **kwargs):
        query = self.get_object()
        if query:
            serializer = self.get_serializer(query)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'query did not exist'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'success': False, 'message': 'credentials is invalid'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class UserOwnImageUpdateView(generics.RetrieveUpdateAPIView):
    # http://127.0.0.1:8000/user/v1/update-own-image/<id>/
    serializer_class = UserOwnImageUpdateSerializer
    queryset = User.objects.all()
    permission_classes = (IsOwnerForUser, )

    def get(self, request, *args, **kwargs):
        query = self.get_object()
        if query:
            serializer = self.get_serializer(query)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'query did not match'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'success': False, 'message': 'Credentials is invalid'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
