from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_weekly_schedule(value):
    if len(value) != 192:
        raise ValidationError(
            _(f'`{value}` must be 192 characters long'),
            params={'value': value},
            code='invalid_length',
        )
    if not all(char in ('X', 'O') for char in value):
        raise ValidationError(
            _(f'`{value}` must only contain X and O'),
            params={'value': value},
            code='invalid_value',
        )

def validate_exam_schedule(value):
    if len(value) != 53:
        raise ValidationError(
            _(f'`{value}` must be 38 characters long'),
            params={'value': value},
            code='invalid_length'
        )
    date, time, timecode = value[:10], value[10:21], value[21:]
    year, month, date = date.split('-')
    try:
        year, month, date = int(year), int(month), int(date)
        if not (1 <= date <= 31 and 1 <= month <= 12 and str(year)[:2] == '20' and 0 <= int(str(year)[2:]) <= 99):
            raise ValidationError(
                _(f'`{value[:10]}` (first 10 chars) must be valid YYYY-MM-DD format'),
                params={'value': value},
                code='invalid_format'
            )
    except ValueError:
        raise ValidationError(
            _(f'`{value[:10]}` (first 10 chars) must be valid YYYY-MM-DD format'),
            params={'value': value},
            code='invalid_format'
        )
    hour_start, min_start, hour_end, min_end = time[:2], time[3:5], time[6:8], time[9:]
    try:
        hour_start, min_start, hour_end, min_end = int(hour_start), int(min_start), int(hour_end), int(min_end)
        if not (0 <= hour_start <= 23 and 0 <= min_start <= 59 and 0 <= hour_end <= 23 and 0 <= min_end <= 59):
            raise ValidationError(
                _(f'`{value[10:21]}` (next 11 chars) must be valid HH:MM-HH:MM format'),
                params={'value': value},
                code='invalid_format'
            )
    except ValueError:
        raise ValidationError(
            _(f'`{value[10:21]}` (next 11 chars) must be valid HH:MM-HH:MM format'),
            params={'value': value},
            code='invalid_format'
        )
    if not all(char in ('X', 'O') for char in timecode):
        raise ValidationError(
            _(f'`{value}` (last 32 chars) must only contain X and O'),
            params={'value': value},
            code='invalid_value',
        )

def validate_information(value):
    info_group = value.split(';')
    for info in info_group:
        single_info = info.split('^')
        if len(single_info) != 6:
            raise ValidationError(
                _(f'`{value}` must be in format of `type^group^day^time^venue^remark`'),
                params={'value': value},
                code='invalid_format'
            )

validate_index = RegexValidator(
    regex=r'^\d{5}$',
    message=_('The value must be 5 numeric digits.'),
    code='invalid_format'
)
