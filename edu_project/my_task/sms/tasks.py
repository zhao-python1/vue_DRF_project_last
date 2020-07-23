import logging

from edu_project.settings import constants
from edu_project.utils.send_message import Message
from my_task.main import app

logger = logging.getLogger('django')


@app.task(name="send_sms")  #name 指定当前   任务的名称 不填 默认使用函数名
def send_sms(mobile, code):
    print("这是发送短信的方法")
    message = Message(constants.API_KEY)
    status = message.send_message(mobile, code)
    if status:
        logger.error("用户发送短信失败，手机号为：%s" % mobile)
    return "hello"