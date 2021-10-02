from django import template

register = template.Library()

@register.filter
def remove_unused(value):
    return value.replace(" ","-").replace("?", "")