from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


class AccountManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if username is None:
            raise TypeError(_('User should have a username'))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        if password is None:
            raise TypeError(_('Password should not be None'))

        user = self.create_user(
            username=username,
            password=password,
            **extra_fields,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.is_verified = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        # abstract = True

    username = models.CharField(max_length=50, unique=True, verbose_name=_('Email'), db_index=True)
    email = models.EmailField(max_length=50, unique=True, verbose_name=_('Email'), db_index=True)
    full_name = models.CharField(max_length=50, verbose_name=_('Full name'), null=True)
    phone = models.CharField(max_length=16, verbose_name=_('Phone Number'), null=True)
    image = models.ImageField(upload_to='users/', verbose_name=_('User image'), null=True, blank=True)
    is_superuser = models.BooleanField(default=False, verbose_name=_('Super user'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Staff user'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active user'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified user'))
    date_login = models.DateTimeField(auto_now=True, verbose_name=_('Last login'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created date'))

    objects = AccountManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        if self.full_name:
            return f'{self.full_name} ({self.username})'
        return f'{self.username}'

    def image_tag(self):
        if self.image:
            return mark_safe(f'<a href="{self.image.url}"><img src="{self.image.url}" style="height:40px;"/></a>')
        else:
            return 'no_image'
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return 'no_image'
    
    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return data

    def has_perm(self, perm, obj=None):
        return True  # does user have a specific permission, simple answer - yes

    def has_module_perms(self, app_label):
        return True  # does user have permission to view the app 'app_label'?
