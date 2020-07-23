from django.urls import path

from first_one import views

urlpatterns = [
    path("banner/", views.BannerListAPIView.as_view()),
    path("nav/", views.BannerListAPIViews.as_view()),
    path("navs/", views.BannerListAPIViewss.as_view()),
]
