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

    # Forum
    path('forum', views.forum, name='forum'),
    path('forum/', views.forum, name='forum'), # So that forum/ still work too
    path('forum/tag/<str:tagName>', views.forum_Tag, name='forum/tag'),
    path('forum/create', views.forum_Create, name='forum/create'),
    path('forum/<str:id>/', views.forum_Content, name='forum'), 
    path('forum/<str:id>/<str:title>', views.forum_Url, name='forum'), 
    path('forum/<str:id>/<str:title>/', views.forum_Url, name='forum'),
    path('forum/<str:id>/<str:title>/edit', views.forum_Edit, name='forum/edit'),
    path('forum/<str:id>/<str:title>/delete', views.forum_Delete, name='forum/delete'),
    path('forum/<str:id>/<str:title>/report', views.forum_Report, name='forum/report'),
    path('forum/<str:id>/<str:title>/like', views.forum_Like, name='forum/like'),
    path('forum/<str:id>/<str:title>/comment', views.forum_Comment, name='post/comment'),
    path('forum/<str:id>/<str:title>/comment/<str:comment_id>/like', views.forum_Comment_Like, name='forum/comment/like'),
    path('forum/<str:id>/<str:title>/comment/<str:comment_id>/edit', views.forum_Comment_Edit, name='post/comment/edit'),
    path('forum/<str:id>/<str:title>/comment/<str:comment_id>/delete', views.forum_Comment_Delete, name='post/comment/delete'),
    path('forum/<str:id>/<str:title>/comment/<str:comment_id>/report', views.forum_Comment_Report, name='post/comment/report'),

    # Artikel
    path('artikel', views.artikel, name='artikel'),
    path('artikel/', views.artikel, name='artikel'),
    path('artikel/create', views.artikel_create, name='artikel/create'),
    path('artikel/tag/<str:tagName>', views.artikel_tag, name='artikel/tag'),
    path('artikel/<str:id>', views.artikel_content, name='artikel/id'), 
    path('artikel/<str:id>/', views.artikel_content, name='artikel/id'), 
    path('artikel/<str:id>/<str:title>', views.artikel_url, name='artikel'), 
    path('artikel/<str:id>/<str:title>/', views.artikel_url, name='artikel'),
    path('artikel/<str:id>/<str:title>/edit', views.artikel_edit, name='artikel/edit'),
    path('artikel/<str:id>/<str:title>/delete', views.artikel_delete, name='artikel/delete'),

    # Konsultasi
    path('konsultasi', views.konsultasi, name='konsultasi'),
    path('konsultasi/', views.konsultasi, name='konsultasi'),
    path('konsultasi/create', views.konsultasi_Create, name='konsultasi/create'),
    path('konsultasi/create/', views.konsultasi_Create, name='konsultasi/create'), # I DONT KNOW WHY BUT IT DOES NOT WORK IF THERE IS NO /
    path('konsultasi/tag/<str:tagName>', views.konsultasi_Tag, name='konsultasi/tag'),
    path('konsultasi/<str:id>/', views.konsultasi_Content, name='konsultasi/id'), # The real url for the konsul
    path('konsultasi/<str:id>/<str:title>', views.konsultasi_Url, name='konsultasi/id'), # Vanity url
    path('konsultasi/<str:id>/<str:title>/', views.konsultasi_Url, name='konsultasi/id'),
    path('konsultasi/<str:id>/<str:title>/delete', views.konsultasi_Delete, name='konsultasi/delete'),
    path('konsultasi/<str:id>/<str:title>/comment', views.konsultasi_Comment, name='konsultasi/comment'),
    path('konsultasi/<str:id>/<str:title>/comment/<str:comment_id>/delete', views.konsultasi_Comment_Delete, name='konsultasi/comment/delete'),
    path('konsultasi/<str:id>/<str:title>/comment/<str:comment_id>/edit', views.konsultasi_Comment_Edit, name='konsultasi/comment/report'),

    # Profile
    path('profile/<str:username>', views.profile, name='profile'),
    path('profile/<str:username>/settings', views.profile_Settings, name='profile/settings'),
    path('profile/<str:username>/posts', views.profile_Posts, name='profile/posts'),
    path('profile/<str:username>/konsultasi', views.profile_Konsultasi, name='profile/konsultasi'),
    # path('profile/<str:username>/comments', views.profile_Comments, name='profile/comments'),
    # path('profile/<str:username>/likes', views.profile_Liked_Commented_Posts, name='profile/likes'),
    # path('profile/<str:username>/notification', views.profile_Notification, name='profile/notification'),
    path('profile/<str:username>/notification/read/<str:notification_id>', views.profile_Notification_Read, name='profile/notification/read'),
    path('profile/<str:username>/notification/readall', views.profile_Notification_Readall, name='profile/notification/readall'),
    path('profile/<str:username>/history', views.profile_history, name='profile/history'),

    # Reports
    path('report', views.report, name='report'),
    path('report/<str:id>/resolve', views.report_Resolve, name='report/resolve'),

    # Tests
    path('tests', views.tests, name='tests'),
    path('tests/', views.tests, name='tests'),

    # Loneliness Test
    path('tests/health/loneliness', views.test_Loneliness, name='tests/health/loneliness'),
    path('tests/health/loneliness/question', views.test_Loneliness_Question, name='tests/health/loneliness/question'),
    path('tests/health/loneliness/result', views.test_Loneliness_Result, name='tests/health/loneliness/submit'),

    # Depression Test
    path('tests/health/depression', views.test_Depression, name='tests/health/depression'),
    path('tests/health/depression/question', views.test_Depression_Question, name='tests/health/depression/question'),
    path('tests/health/depression/result', views.test_Depression_Result, name='tests/health/depression/submit'),

    # Mindfulness Test
    path('tests/health/mindfulness', views.test_Mindfulness, name='tests/health/mindfulness'),
    path('tests/health/mindfulness/question', views.test_Mindfulness_Question, name='tests/health/mindfulness/question'),
    path('tests/health/mindfulness/result', views.test_Mindfulness_Result, name='tests/health/mindfulness/submit'),

    # Hasil test, data ditentukan dari backend
    path('tests/result', views.test_Result, name='tests/result'),

    # Quick Links Privacy Policy
    path('privacy-policy', views.privacy_policy, name='privacy-policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),

    # Quick Links FAQ
    path('faq', views.faq, name='faq'),
    path('faq/', views.faq, name='faq'),
]