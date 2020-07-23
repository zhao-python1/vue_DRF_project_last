# 定义了jwt的返回值
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from user.models import Logininfo


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        "user_id": user.id
    }

def get_user_by_account(account):
    try:
        user = Logininfo.objects.filter(Q(username=account) | Q(phone=account)).first()
    except Logininfo.DoesNotExist:
        return None
    else:
        return user

class UserA(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        zhanghao获取用户对象
        :param request:
        :param username:
        :param password:
        :param kwargs:
        :return:
        '''
        # 满足于一个
        user = get_user_by_account(username)
        if user and user.check_password(password) and user.is_authenticated:
            return user
        else:
            return None

