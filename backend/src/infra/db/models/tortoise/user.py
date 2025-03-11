from tortoise import Model, fields

from .common import IntIDMixin, TimestampsMixin


class User(Model, IntIDMixin, TimestampsMixin):
    username = fields.CharField(max_length=50, unique=True, null=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    first_name = fields.CharField(max_length=150, blank=True, null=True)
    last_name = fields.CharField(max_length=150, blank=True, null=True)
    is_staff = fields.BooleanField(default=False)
    date_joined = fields.DatetimeField(auto_now_add=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "auth_user"

    class PydanticMeta:
        exclude = ["hashed_password"]
