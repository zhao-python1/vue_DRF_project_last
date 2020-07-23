from rest_framework.generics import ListAPIView
from edu_project.settings.constants import BANNER_LENGTH,NAV_LENGTH
from first_one.models import Banner, Nav
from first_one.serializers import BannerModelSerializer,NavModelSerializers
#

class BannerListAPIView(ListAPIView):
    queryset = Banner.objects.filter(is_show=True, is_delete=False).order_by("-orders")[:BANNER_LENGTH]
    serializer_class = BannerModelSerializer


class BannerListAPIViews(ListAPIView):
        queryset = Nav.objects.filter(is_show=True, is_delete=False,position = 1 ).order_by("-orders")[:NAV_LENGTH]
        serializer_class = NavModelSerializers
class BannerListAPIViewss(ListAPIView):
        queryset = Nav.objects.filter(is_show=True, is_delete=False,position = 2 ).order_by("-orders")[:NAV_LENGTH]
        serializer_class = NavModelSerializers
