#my_job任务目录  一个目录可以放置多个任务
from my_job.main import app


#tasks  任务的文件，名称不变
@app.task(name="send_for") #name 指定当前   任务的名称 不填 默认使用函数名
def send_for():
    print("这是发送短信的方法")
    return "hello"