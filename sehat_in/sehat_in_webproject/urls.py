from django.urls import path
from . import views # Import views from same dir, thats why we use '.'

# This will contains all the urls for the project
urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.test, name='test'),
    path('test/a', views.a, name='test/a')
]