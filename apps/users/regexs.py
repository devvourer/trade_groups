from django.core.validators import RegexValidator

inn_regex = RegexValidator(
    regex=r'^(1|2){1}\d{13}$',
    message='Неверный инн'
)
