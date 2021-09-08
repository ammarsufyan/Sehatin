from django.urls import path
from . import views # Import views from same dir, thats why we use '.'

# This will contains all the urls for the project
urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.test, name='test'),
    path('test/a', views.a, name='test/a'),
    path('auth/register', views.register, name='auth/register'),
    path('auth/login', views.login, name='auth/login'),
    path('logout', views.logout, name='logout')
]