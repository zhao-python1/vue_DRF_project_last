from django.urls import path

from sel import views

urlpatterns = [
    # path("banner/", views.BannerListAPIView.as_view()),
    # path("/", views.BannerListAPIViews.as_view()),
    path("sell/", views.SelAPIView.as_view()),


]