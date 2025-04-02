def formatted_number(
    value,
    prefix="",
    suffix="",
    decimals=2,
    zero_value=None,
    none_value="-",
    subscript=False,
    add_sign=False,
) -> str or None:

    from django.utils.translation import gettext_lazy as _
    test = _("Текст")
    print(test)
    if value is None:
        return none_value
    if value == 0 and zero_value is not None:
        return zero_value

    if isinstance(value, int):
        formatted_value = f"{value}"
    else:
        if not subscript:
            formatted_value = f"{value:,.{decimals}f}".replace(",", " ")
        else:
            value_str = f"{value:,.{decimals}f}".replace(",", " ")
            # Ищем количество нулей после запятой до первого ненулевого числа
            integer_part = value_str.split(".")[0]
            decimal_part = value_str.split(".")[1]  # Получаем часть после запятой
            zero_count = len(decimal_part) - len(
                decimal_part.lstrip("0")
            )  # Считаем количество нулей
            subscript_map = {
                "0": "₀",
                "1": "₁",
                "2": "₂",
                "3": "₃",
                "4": "₄",
                "5": "₅",
                "6": "₆",
                "7": "₇",
                "8": "₈",
                "9": "₉",
                "10": "₁₀",
                "11": "₁₁",
            }
            # Формируем строку с подстрочными индексами для нулей
            if zero_count:
                subscript_zeroes = "0" + subscript_map[str(zero_count)]
            else:
                subscript_zeroes = ""
            # Оставшаяся часть числа (не включая нули)
            remaining_value = decimal_part.lstrip("0")[:3]
            # Формируем итоговое значение
            formatted_value = f"{integer_part}.{subscript_zeroes}{remaining_value}"
        if add_sign:
            formatted_value = f"{'+' if value > 0 else ''}{formatted_value}"

    return f"{prefix}{formatted_value}{suffix}"


def round_to_first_non_zero(value: float, max_decimals=5) -> float:
    # Преобразуем число в строку с учётом значений после запятой
    str_value = str(value)

    # Ищем первое ненулевое значение после запятой
    if "." in str_value:
        decimal_part = str_value.split(".")[1]
        for i, digit in enumerate(decimal_part):
            if digit != "0" or i + 1 >= max_decimals:
                # Округляем до первого ненулевого числа
                rounded_value = round(value, i + 1)
                return rounded_value
    return value  # Если нет ненулевых чисел, возвращаем исходное число
