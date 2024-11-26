# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login-redirect/', views.login_redirect, name='login_redirect'),
    path('callback/', views.callback_view, name='callback'),
    path('get-user-info/', views.get_user_info, name='get_user_info'),  # 사용자 정보 API
    path('reservation/', views.reservation_view, name='reservation'),
    #path('test-parse/', views.test_parse_view, name='test_parse'),  # 테스트 URL (선택 사항)
]