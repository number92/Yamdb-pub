import re
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError

ERROR_MESSAGE = 'Имя пользователя содержит недопустимые символы: {}'


def validate_year(value):
    now_year = datetime.now().year
    if value > now_year:
        raise ValidationError(f'{value} не может быть больше {now_year}')
    return value


def validate_username(value):
    if value == settings.FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Имя пользователя не может совпадать '
            f'с "{settings.FORBIDDEN_USERNAME}".'
        )
    invalid_chars = set(re.findall(settings.EXCEPTION_CHARACTERS, value))
    if invalid_chars:
        raise ValidationError(
            ERROR_MESSAGE.format(''.join(invalid_chars))
        )
    return value
