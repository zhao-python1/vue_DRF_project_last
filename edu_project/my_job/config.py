#celery相关配置

#任务队列的链接地址
broker_url = "redis://127.0.01:6379/5"
#结果队列的链接地址
result_backend = "redis://127.0.01:6379/6"