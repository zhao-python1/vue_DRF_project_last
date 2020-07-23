import random
import re

from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as statuss
from rest_framework.generics import CreateAPIView
from django_redis import get_redis_connection
from edu_project.libs.geetest import GeetestLib
from edu_project.settings import constants
from user.models import Logininfo
from user.utils import get_user_by_account
from user.serializers import UserModelSerializer
from utils.send_message import Message

pc_geetest_id = "6f91b3d2afe94ed29da03c14988fb4ef"
pc_geetest_key = "7a01b1933685931ef5eaf5dabefd3df2"


#
#
class CapAPIView(APIView):
    #     """极验验证码"""
    user_id = 0
    status = False

    #
    def get(self, request, *args, **kwargs):
        #         """获取验证码"""
        username = request.query_params.get('username')
        user_obj = get_user_by_account(username)
        if user_obj is None:
            return Response({"message": "用户不存在"}, status=statuss.HTTP_400_BAD_REQUEST)
        #
        self.user_id = user_obj.id
        #
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    #
    def post(self, request, *args, **kwargs):
        #         """验证验证码"""
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        #         # 判断用户是否存在
        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


# 注册的类视图
class Register(CreateAPIView):
    queryset = Logininfo.objects.all()
    serializer_class = UserModelSerializer

    # def get(self ,request, *args,**kwargs):


# 验证手机号是否重复
class Mobilereappera(APIView):
    def get(self, request,mobile):
        # 判断手机号是否合法
        if not re.match(r'^1[35789]\d{9}', mobile):
            return Response({"message": "手机号格式不对"}, status=http_status.HTTP_400_BAD_REQUEST)
        user = get_user_by_account(mobile)

        if user is not None:
            return Response({"message": "手机号重复"}, status=http_status.HTTP_400_BAD_REQUEST)

        return Response({"message": "ok"})


#手机号的验证码
class SendMessageAPIView(APIView):
    def get(self,request,mobile):
        '''
        获取验证码 为手机号生成并发送
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        #获取redis链接
        redis_connection = get_redis_connection("sms_code")
        # 1. 判断手机验证码是否在60s内发送过短信
        mobile_code = redis_connection.get("sms_%s" % mobile)
        if mobile_code is not None:
            return Response({"message": "您已经在60秒内发送过短信了~"},status = http_status.HTTP_400_BAD_REQUEST)
        #  生成随机的短息验证码
        code = "%06d" % random.randint(0,999999)

        # 3 将验证码保存到redis中
        redis_connection.setex("sms_%s" % mobile, constants.SMS_EXPIRE_TIME, code)# 60s不允许再发送
        redis_connection.setex("mobile_%s" % mobile, constants.MOBILE_EXPIRE_TIME, code)  # 验证码的有效时间
    # #     4#调用方法 完成短信的的发送
        try:
           #通过celery异步执行短信的服务
            # from my_task.sms.tasks import send_sms
            # send_sms.delay(mobile, code) #如果需要参数传递过去 不需要则不传递
            message = Message(constants.API_KEY)
            message.send_message(mobile,code)
            # message = Message(constants.API_KEY)
            # message.send_message(mobile,code)
        except:
            return Response({"message":"短信息发送失败"}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)


            # 5. 返回一个响应响应回去
        return Response({"message": "发送短信成功"}, status=http_status.HTTP_200_OK)

class Loginmin(APIView):
    def post(self,request,*args,**kwargs):
        return


