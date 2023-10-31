from django.urls import path
from .  import views

urlpatterns = [
    path('register/api',views.User_register.as_view(), name='register/api'),
    path('login/api',views.User_login.as_view(), name='login/api'),
    path('userdata/api',views.User_data.as_view(), name='userdata/api'),
    path('verify_otp/api',views.OTP_Verification.as_view(), name='verify_otp/api'),
    path('resend_otp/api',views.Resend_OTP.as_view(), name='resend_otp/api'),
    path('create_task/api',views.CreateTask.as_view(), name='create_task/api'),
    path('edit_task/api',views.Edit_Task.as_view(), name='edit_task/api'),
    path('delete_task/api',views.Delete_Task.as_view(), name='delete_task/api'),
    path('list_task/api', views.ViewTask.as_view(), name='list_task/api'),
]
