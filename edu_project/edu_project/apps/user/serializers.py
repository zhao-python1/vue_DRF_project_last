import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers
from django.core.cache import cache

from user.models import Logininfo
from user.utils import get_user_by_account
class UserModelSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1024, read_only=True, help_text="用户token")
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = Logininfo
        fields = ("id", "username", "password", "phone", "token","sms_code")
        extra_kwargs = {
            "id": {
                'read_only': True,
            },
            "username": {
                "read_only": True,
            },
            "password": {
                "write_only": True,
            },
            "phone": {
                "write_only": True
            }
        }
    # 全局钩子
    def validate(self, attrs):
        '''
        验证手机好
        :param attrs:
        :return:
        '''
        phone = attrs.get('phone')
        password = attrs.get("password")
        sms_code = attrs.get("sms_code")
        print(sms_code)
        #     #
        # 验证手机号格式
        if not re.match(r'^1[35789]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式错误")

        # 验证手机号是否重反复
        try:
            user = get_user_by_account(phone)
        except:
            user = None
        if user:
            raise serializers.ValidationError("当前手机号已被注册")

        #验证手机号验证码是否正确
        redis_connection = get_redis_connection('sms_code')
        phone_code = redis_connection.get("mobile_%s" % phone)
        if phone_code.decode() != sms_code:
            raise serializers.ValidationError("验证码不一致")

        #删除验证码
        cache.delete_pattern("mobile_%s" % phone)
        return attrs
    def create(self, validated_data):
        '''
        重写create方法
        :param validated_data:
        :return:
        '''
        pwd = validated_data.get('password')
        hash_password = make_password(pwd)
        #     #处理用户i名  设置默认值 生成随机字符串 手机号
        username = validated_data.get('phone')
        #     #     #添加数据
        user = Logininfo.objects.create(
            phone=username,
            username=username,
            password=hash_password
        )
        #为注册成功的用户生成token
        from rest_framework_jwt.settings import api_settings
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        user.token = jwt_encode_handler(payload)
        return user

class Loginmgs(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1024, read_only=True, help_text="用户token")
    sms_code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text="短信验证码")

    class Meta:
        model = Logininfo
        fields = ("id", "phone", "token", "sms_code")
        extra_kwargs = {
            "id": {
                'read_only': True,
            },
            "phone": {
                "write_only": True
            }
        }

    # 全局钩子
    def validate(self, attrs):
        '''
        验证手机好
        :param attrs:
        :return:
        '''
        phone = attrs.get('phone')
        password = attrs.get("password")
        sms_code = attrs.get("sms_code")
        print(sms_code)
        #     #
        # 验证手机号格式
        if not re.match(r'^1[35789]\d{9}$', phone):
            raise serializers.ValidationError("手机号格式错误")

        # 验证手机号是否重反复
        try:
            user = get_user_by_account(phone)
        except:
            user = None
        if user:
            raise serializers.ValidationError("当前手机号已被注册")

        # 验证手机号验证码是否正确
        redis_connection = get_redis_connection('sms_code')
        phone_code = redis_connection.get("mobile_%s" % phone)
        if phone_code.decode() != sms_code:
            raise serializers.ValidationError("验证码不一致")

        # 删除验证码
        cache.delete_pattern("mobile_%s" % phone)
        return attrs
