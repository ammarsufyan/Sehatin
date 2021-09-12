from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(UserProfile)
admin.site.register(Notification)
admin.site.register(Report)
# admin.site.register(Follow)
# admin.site.register(Message)
# admin.site.register(Chat)