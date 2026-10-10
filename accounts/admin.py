from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as Base
from accounts.models import EmailConfirmation, User


@admin.register(User)
class UserAdmin(Base):
    model = User
    list_display = ("email", "role", "email_confirmed", "is_staff")
    ordering = ("email",)
    search_fields = ("email",)
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("email", "password", "role", "email_confirmed", "consent_pd")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = ((None, {"fields": ("email", "password1", "password2", "role")}),)


admin.site.register(EmailConfirmation)
