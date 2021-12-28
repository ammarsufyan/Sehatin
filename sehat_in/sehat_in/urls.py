"""sehat_in URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from .validator import MyPasswordForm

urlpatterns = [
    path('s3cr3t4dm1n/', admin.site.urls),
    path('', include('sehat_in_webproject.urls')),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/reset-done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password/reset-confirm.html', form_class=MyPasswordForm), name='password_reset_confirm'),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password/reset-complete.html'), name='password_reset_complete'),
    path('favicon.ico', RedirectView.as_view(url='/static/img/favicon/favicon.ico'))
]

handler404 = 'sehat_in_webproject.views.error_404_view'
handler403 = 'sehat_in_webproject.views.error_403_view'