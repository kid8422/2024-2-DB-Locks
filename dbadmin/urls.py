from django.urls import path
from . import views

urlpatterns = [
    path('', views.dbadmin_home, name='dbadmin_home'),
    path('login/', views.dbadmin_login, name='dbadmin_login'),
    path('logout/', views.dbadmin_logout, name='dbadmin_logout'),
    path('get-lockers-data/', views.get_lockers_data, name='get_lockers_data'),
    path('get-rent-data/', views.get_rent_data, name='get_rent_data'),
    path('get-log-data/', views.get_log_data, name='get_log_data'),
    path('get-student-data/', views.get_student_data, name='get_student_data'),
    path('update-data/', views.update_data, name='update_data'),  # table_name 매개변수 제거
]
