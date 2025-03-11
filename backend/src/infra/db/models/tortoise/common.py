import uuid

from tortoise import fields


class IntIDMixin:
    id = fields.IntField(primary_key=True)


class UUIDIDMixin:
    id = fields.UUIDField(primary_key=True, default=uuid.uuid1)


class TimestampsMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
