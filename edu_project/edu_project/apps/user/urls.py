from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from user import views

urlpatterns = [
    path("login/", obtain_jwt_token),
    path("captcha/", views.CapAPIView.as_view()),
    path("register/", views.Register.as_view()),
    #生成验证码
    # path("send/", views.SendMessageAPIView.as_view()),
    path("mobile/<str:mobile>", views.Mobilereappera.as_view()),
    path("message/<str:mobile>", views.SendMessageAPIView.as_view()),
]
