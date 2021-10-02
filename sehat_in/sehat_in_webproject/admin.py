from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Forum)
admin.site.register(Artikel)
admin.site.register(Konsultasi)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(UserProfile)
admin.site.register(Notification)
admin.site.register(Report)
admin.site.register(History)