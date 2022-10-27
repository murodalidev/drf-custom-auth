from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    password2 = serializers.CharField(min_length=6, max_length=68, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError({'success': False, 'message': 'Password did not match, please try again'})
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(max_length=68, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {
            'role': {'read_only': True}
        }

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed({
                'message': 'Username or password is not correct'
            })
        if not user.is_active:
            raise AuthenticationFailed({
                'message': 'Account disabled'
            })
        if not user.is_verified:
            raise AuthenticationFailed({
                'message': 'Email is not verified'
            })

        data = {
            'success': True,
            'username': user.username,
            'tokens': user.tokens,
        }
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'full_name', 'username', 'phone', 'image', 'team_name')
        extra_kwargs = {
            'image': {'read_only': True}
        }


class UserOwnImageUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('image', )


class SetNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=64, write_only=True)
    password2 = serializers.CharField(min_length=6, max_length=64, write_only=True)

    class Meta:
        model = User
        fields = ('password', 'password2')

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        request = user =  self.context['request']
        user = request.user
        if password != password2:
            raise serializers.ValidationError({'success': False, 'message': 'Password did not match, '
                                                                            'please try again new'})
        user.set_password(password)
        user.save()
        return user

