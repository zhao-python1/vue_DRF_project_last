from django.shortcuts import render
from rest_framework.generics import CreateAPIView

from sel.models import Order
from sel.serializer import OrderModelSerializer


class SelAPIView(CreateAPIView):
    '''订单生曾的试图'''
    queryset = Order.objects.filter(is_show=True,is_delete=False,)
    serializer_class = OrderModelSerializer
