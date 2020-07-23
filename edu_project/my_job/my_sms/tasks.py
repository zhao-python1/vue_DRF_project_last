#my_job任务目录  一个目录可以放置多个任务
import logging

from edu_project.settings import constants
from my_job.main import app
from edu_project.utils.send_message import Message
log = logging.getLogger("django")
#tasks  任务的文件，名称不变
@app.task(name="send_sms") #name 指定当前   任务的名称 不填 默认使用函数名
def send_sms(mobile, code):
    message = Message(constants.API_KEY)
    status = message.send_message(mobile, code)
    if status:
        log.error("用户发送短信失败，手机号为：%s" % mobile)
    return "发送成功了"

# @app.task(name="send_mail") #name 指定当前   任务的名称 不填 默认使用函数名
# def send_mail():
#     print("这是发送短信的方法")
#     return "word"