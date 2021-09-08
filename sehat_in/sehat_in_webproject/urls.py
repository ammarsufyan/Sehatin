from django.urls import path
from . import views # Import views from same dir, thats why we use '.'

# This will contains all the urls for the project
urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.test, name='test'),
    path('test/a', views.a, name='test/a'),
    path('auth/register', views.register, name='auth/register'),
    path('auth/login', views.login, name='auth/login'),
    path('logout', views.logout, name='logout'), # Not going anywhere, just logging out
    path('post', views.post, name='post'),
    path('post/', views.post, name='post'), # So that post/ still work too
    path('post/<str:id>/', views.post_Content, name='post'),
    path('post/<str:id>/<str:title>', views.post_Url, name='post'),
    path('post/<str:id>/edit', views.post_Edit, name='post/edit'),
    path('post/<str:id>/report', views.post_Report, name='post/report')
]