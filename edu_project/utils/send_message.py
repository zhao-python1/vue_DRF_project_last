import requests

from edu_project.settings import constants
class Message(object):

    def __init__(self, api_key):
        # 账号的唯一标识
        self.api_key = api_key

        # 单条短信发送接口
        self.single_send_url = constants.SINGLE_SEND_URL

    def send_message(self, phone, code):
        '''
        短信发送的实现
        :param phone:
        :param code: 随机验证码
        :return:
        '''
        params = {
            "apikey": self.api_key,
            "mobile": phone,
            # 'text': "【王睿昊】您的验证码是{code}".format(code=code)

            # 'text': "【毛信宇test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
            'text': "【毛信宇test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
            # 'text': "【赵少博test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        rel = requests.post(self.single_send_url, data=params)
        print(rel)


if __name__ == '__main__':
    # message = Message('40d6180426417bfc57d0744a362dc108')
    message = Message(constants.API_KEY)
    message.send_message('18439415705', '123456')
