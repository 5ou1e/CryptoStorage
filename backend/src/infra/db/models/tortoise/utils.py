import decimal

from tortoise import fields


class MyDecimalField(fields.DecimalField):
    """Переопределение стандартного DecimalField для корректной обработки чисел с большой целочисленной частью"""

    def to_python_value(self, value):
        if value is not None:
            with decimal.localcontext() as ctx:
                ctx.prec = self.max_digits  # Устанавливаем точность (общая для целой и дробной части)
                # Преобразуем число в Decimal и квантизируем (ограничиваем дробную часть)
                value = decimal.Decimal(value).quantize(self.quant).normalize()
                return value
        return value
