from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'username', 'email', 'full_name', 'phone', 'image_tag', 'is_superuser', 'is_staff',
                    'is_active', 'is_verified', 'date_login', 'date_created')
    readonly_fields = ('date_login', 'date_created')
    list_filter = ('date_created', 'is_superuser', 'is_staff', 'is_active', 'is_verified')
    ordering = ()
    fieldsets = (
        (None, {'fields': ('username', 'email', 'full_name', 'phone', 'image', 'password')}),
        (_('Permissions'), {'fields': ('is_superuser', 'is_staff', 'is_active', 'is_verified',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('date_login', 'date_created')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2'), }),
    )
    search_fields = ('username', 'email', 'full_name', 'phone')


admin.site.register(User, UserAdmin)
