import decimal

import uuid6
from tortoise import fields


class IntIDMixin:
    id = fields.IntField(primary_key=True)


class UUIDIDMixin:
    id = fields.UUIDField(primary_key=True, default=uuid6.uuid7)


class TimestampsMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class CorrectedDecimalField(fields.DecimalField):
    """Переопределение стандартного DecimalField для корректной обработки чисел с большой целочисленной частью"""

    def to_python_value(self, value):
        if value is not None:
            with decimal.localcontext() as ctx:
                ctx.prec = (
                    self.max_digits
                )  # Устанавливаем точность (общая для целой и дробной части)
                # Преобразуем число в Decimal и квантизируем (ограничиваем дробную часть)
                value = decimal.Decimal(value).quantize(self.quant).normalize()
                return value
        return value
