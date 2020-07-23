import os
from datetime import datetime

from django.db import transaction
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from alipay import AliPay
from django.shortcuts import render
import logging
# Create your views here.
from course.models import CourseExpire
from edu_project.settings.develop import BASE_DIR
from sel.models import Order
from user.models import UserCourse

#日志文件
log = logging.getLogger()
class AliPayAPIView(APIView):
    def get(self,request):
        '''获取支付的地址链接'''
        order_number = request.query_params.get("order_number")
        # 公私钥的位置 # 自己生成的私钥
        app_private_key_string = open(os.path.join(BASE_DIR, "apps/payments/keys/app_private_key.pem")).read()
        # 支付宝的公钥
        alipay_public_key_string = open(os.path.join(BASE_DIR, "apps/payments/keys/alipay_public_key.pem")).read()
        print(alipay_public_key_string)

        # 查询订单是否存在
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return Response({"message": "当前订单不存在"}, status=status.HTTP_400_BAD_REQUEST)

        # 对支付宝初始化参数配置
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG["appid"],  # 沙箱支付的id
            app_notify_url=settings.ALIAPY_CONFIG["app_notify_url"],  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type=settings.ALIAPY_CONFIG["sign_type"],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG["debug"],  # 默认False
        )

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 生成支付的连接地址
        order_string = alipay.api_alipay_trade_page_pay(
            # 支付宝所接受的订单号
            out_trade_no=order.order_number,
            total_amount=float(order.real_price),
            subject=order.order_title,
            return_url=settings.ALIAPY_CONFIG["return_url"],
            notify_url=settings.ALIAPY_CONFIG["notify_url"]  # 可选, 不填则使用默认notify url
        )

        # 生成好的支付地址，和网关拼接才能用
        # 生成好的地址跳转页面
        url = settings.ALIAPY_CONFIG["gateway_url"] + order_string

        return Response(url)


#修改地订单状态  生成购买记录 展示结算成功页面

class ZFBAPIView(APIView):
    '''处理支付成功后的业务 验证支付的是页面情况'''
    def get(self, request):
        # 公私钥的位置 # 自己生成的私钥
        app_private_key_string = open(os.path.join(BASE_DIR, "apps/payments/keys/app_private_key.pem")).read()
        # 支付宝的公钥
        alipay_public_key_string = open(os.path.join(BASE_DIR, "apps/payments/keys/alipay_public_key.pem")).read()

        # 对支付宝初始化参数配置
        alipay = AliPay(
            appid=settings.ALIAPY_CONFIG["appid"],  # 沙箱支付的id
            app_notify_url=settings.ALIAPY_CONFIG["app_notify_url"],  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type=settings.ALIAPY_CONFIG["sign_type"],  # RSA 或者 RSA2
            debug=settings.ALIAPY_CONFIG["debug"],  # 默认False
        )

        #验证alipay 的异步通知，data的来自支付宝的回调·post 给data 字典格式

        data = request.query_params.dict()
        #再此获取签名的信息
        sig = data.pop("sign")
        #比对签名是否合法
        success = alipay.verify(data,sig)
        success  =True
        if success:
            return self.success_pay(data)
            #支付成功后的业务逻辑
        return Response({"message":"sorry,当前订单失败"})

    def success_pay(self,data):
        """处理订单支付成功后的业务
                修改订单状态  生成用户购买记录  展示结算信息  购买后增加对应课程的购买人数
        """
#         先查询订单是否成功
        order_number = data.get("out_trade_no")
        try:
            order = Order.objects.get(order_number=order_number,order_status=0)
        except Order.DoesNotExist:
            return Response({"message":"sorry！支付结果查询失败"},status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            savepoint = transaction.savepoint()
            #修改订单状态
            try:
                order.pay_time = datetime.now()
                order.order_status = 1
                order.save()
                #根据订单获取对应的的用户
                user = order.user
                #获取订单的所有课程
                order_detail_list = order.order_courses.all()
                #订单结算页面的信息
                course_list = []

                for order_detail in order_detail_list:
                    '''便利本次订单所有商品'''
                    course = order_detail.course
                    course.students +=1
                    course.save()
                    #根据订单获取对应的用户
                    user = order.user
                    #获取 购买的所有的课程
                    order_detail_list = order.order_courses.all()
                    #订单结算页面的喜喜

                    course_list=[]
                    for order_detail in order_detail_list:
                        '''遍历本次订单中所有的商品'''
                        course = order_detail.course
                        course.students += 1
                        course.save()

                    #判断购买的课程是否长期有效 不是则记录在时间里

                    pay_time = order.pay_time.timestamp()
                    #如果购买的不是长期客户课程
                    if order_detail.expire > 0:
                        expire = CourseExpire.objects.get(pk=order_detail.expire)
                        expire_time = expire.get_next_in_order *24 * 60
                        end_time = datetime.fromtimestamp(pay_time + expire_time)
                    else:
                        #永久购买
                        end_time = None

                    #  为用户生成购买课程的信息
                    UserCourse.objects.create(
                        user_id=user.id,
                        course_id=course.id,
                        trade_no=data.get("trade_no"),
                        buy_type=1,
                        pay_time=order.pay_time,
                        out_time=end_time,
                    )
                    course_list.append({
                        "id": course.id,
                        "name": course.name
                    })
            except:
                log.error("订单处理过程中吃错，请检查")
                transaction.savepoint_rollback(savepoint)
                return Response({"message":"sorry！更新订单相关的信息失败了" },status=status.HTTP_400_BAD_REQUEST)
        # 返回订单结算页面所需的数据


        return Response({"message": "支付成功",
                         "success": "success",
                         "pay_time": order.pay_time,
                         "real_price": order.real_price,
                         "course_list": course_list
                         })