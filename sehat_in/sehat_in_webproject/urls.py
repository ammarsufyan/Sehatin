from django.urls import path
from . import views # Import views from same dir, thats why we use '.'

# This will contains all the urls for the project
urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # Account authentication
    path('auth/register', views.register, name='auth/register'),
    path('auth/login', views.login, name='auth/login'),
    path('logout', views.logout, name='logout'), # Not going anywhere, just logging out

    # Post
    path('post', views.post, name='post'),
    path('post/', views.post, name='post'), # So that post/ still work too
    path('post/tag/<str:tagName>', views.post_Tag, name='post/tag'),
    path('post/create', views.post_Create, name='post/create'), # So that post/ still work too
    path('post/<str:id>/', views.post_Content, name='post'), # The real url for the post
    path('post/<str:id>/<str:title>', views.post_Url, name='post'), # Vanity url
    path('post/<str:id>/<str:title>/', views.post_Url, name='post'),
    path('post/<str:id>/<str:title>/edit', views.post_Edit, name='post/edit'),
    path('post/<str:id>/<str:title>/delete', views.post_Delete, name='post/delete'),
    path('post/<str:id>/<str:title>/report', views.post_Report, name='post/report'),
    path('post/<str:id>/<str:title>/like', views.post_Like, name='post/like'),

    # Post comment
    path('post/<str:id>/<str:title>/comment', views.post_Comment, name='post/comment'),
    path('post/<str:id>/<str:title>/comment/<str:comment_id>/like', views.post_Comment_Like, name='post/comment/like'),
    path('post/<str:id>/<str:title>/comment/<str:comment_id>/edit', views.post_Comment_Edit, name='post/comment/edit'),
    path('post/<str:id>/<str:title>/comment/<str:comment_id>/delete', views.post_Comment_Delete, name='post/comment/delete'),
    path('post/<str:id>/<str:title>/comment/<str:comment_id>/report', views.post_Comment_Report, name='post/comment/report'),

    # Profile
    path('profile/<str:username>', views.profile, name='profile'),
    path('profile/<str:username>/settings', views.profile_Settings, name='profile/settings'),
    path('profile/<str:username>/notification', views.profile_Notification, name='profile/notification'),

    # Reports
    path('report', views.report, name='report'),
]