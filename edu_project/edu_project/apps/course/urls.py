from django.urls import path

from course import views

urlpatterns = [
    path("category/", views.CourseCatgoryListAPIView.as_view()),
    path("list/", views.CourseListAPIView.as_view()),
    path("list_filter/", views.CourseFilterListAPIView.as_view()),
    # path("less/", views.CourseLessonListAPIView.as_view()),
    path("less/<str:id>", views.CourseLessonListAPIView.as_view()),
    path("chapter/", views.CourseCapterAPIView.as_view()),
]
