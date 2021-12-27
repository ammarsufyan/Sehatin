import datetime
from django import template
register = template.Library()


@register.simple_tag
def check_edited_comments(created, updated):
   edited = ""
   if updated > created + datetime.timedelta(minutes=5):
        edited = "Edited"
   return edited