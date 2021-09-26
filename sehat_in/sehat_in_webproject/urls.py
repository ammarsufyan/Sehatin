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
    path('profile/<str:username>/posts', views.profile_Posts, name='profile/posts'),
    path('profile/<str:username>/comments', views.profile_Comments, name='profile/comments'),
    path('profile/<str:username>/likes', views.profile_Liked_Commented_Posts, name='profile/likes'),
    path('profile/<str:username>/notification', views.profile_Notification, name='profile/notification'),
    path('profile/<str:username>/notification/read/<str:notification_id>', views.profile_Notification_Read, name='profile/notification/read'),
    path('profile/<str:username>/notification/readall', views.profile_Notification_Readall, name='profile/notification/readall'),

    # Reports
    path('report', views.report, name='report'),
    path('report/<str:id>/resolve', views.report_Resolve, name='report/resolve'),

    # Tests
    path('tests', views.tests, name='tests'),
    path('tests/health/kesehatan-mental', views.test_SehatMental, name='tests/health/kesehatan-mental'),
    path('tests/health/kesehatan-mental/question', views.test_SehatMental_Question, name='tests/health/kesehatan-mental/question'),

    # Hasil test, data ditentukan dari backend
    path('tests/result', views.test_SehatMental_Result, name='tests/health/kesehatan-mental/result'),
]