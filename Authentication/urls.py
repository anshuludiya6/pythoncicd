# Authentication/urls.py

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('status/', status, name='status'),
    path('register/', signup, name='register'),
    path('login/', login, name='login'),
    path('verify_email/', verify_email, name='verify_email'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    # path('forgot_password/', forgot_password, name='forgot_password'),
    # path('reset_password/', reset_password, name='reset_password'),
    # path('check_reset_token/', check_reset_token, name='check_reset_token'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('check-reset-token/<str:token>/', check_reset_token_for_user, name='check_reset_token'),
    path('reset_password/', reset_password, name='reset_password'),
    path('get_user_information/', get_user_information, name='get_user_information'),
    # path('create_user/', create_user, name='create_user'),
    path('update_user_information/', update_user_information, name='update_user_information'),
    path('delete_user/', delete_user, name='delete_user'),
    path('get_all_user_info/', get_all_user_info, name='get_all_user_info'),
    path('verify_email/<str:token>/', verify_email, name='verify_email'),
    path('success/', TemplateView.as_view(template_name="success.html"), name='success_page'),
    path('failure/', TemplateView.as_view(template_name="failure.html"), name='failure_page'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
