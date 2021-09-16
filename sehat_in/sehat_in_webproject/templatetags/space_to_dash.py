from django import template

register = template.Library()

@register.filter
def space_to_dash(value):
    return value.replace(" ","-")