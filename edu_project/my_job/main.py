#celery主程序

# 是第一步
import os

import django
from celery import Celery

#创建实例对象 celery  有多个实例的时候需要指定实例的名字
app = Celery("edu")

# Crlery和django 链接起来 识别并加载django 的配置文件
os.environ.setdefault("DJANGO_SETTINGS_MODULE","edu_project.settings.develop")
django.setup()


#通过创建的实例对象家在配置
#app.config_from_object(["任务一","任务2"])
app.config_from_object("my_job.config")

#添加任务到实例当中
app.autodiscover_tasks(["my_job.my_sms"])
# app.autodiscover_tasks(["my_job.my_file"])

#直接启动celery  在项目的根目录下执行启动命令

# celery -A my_job.main worker --loglevel=info
