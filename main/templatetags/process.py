from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

names_dict = {
    'LFC_binary': 'LFC',
    'LFC_multi': 'LFC',
}


@register.filter
@stringfilter
def convert_names(method):
    if method in names_dict:
        return names_dict[method]
    else:
        return method
