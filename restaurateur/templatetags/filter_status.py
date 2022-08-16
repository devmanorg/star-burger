from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def display_status(value):
    status = {
        'CR': 'Создан',
        'PC': 'Сборка',
        'SH': 'Доставка',
        'CT': 'Выполнен',
    }
    return status.get(value, 'Ошибка!')
