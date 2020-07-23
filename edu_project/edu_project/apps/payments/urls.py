from django.urls import path

from payments import views

urlpatterns = [
    path("ali/", views.AliPayAPIView.as_view()),
    path("success/", views.ZFBAPIView.as_view()),
]