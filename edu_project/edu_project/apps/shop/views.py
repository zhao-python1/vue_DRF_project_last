import logging

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django_redis import get_redis_connection
from rest_framework import status
from course.models import Course, CourseExpire
from rest_framework.permissions import IsAuthenticated

from edu_project.settings import constants
from edu_project.settings.constants import IMAGE_SRC

logs = logging.getLogger("django")


class ShopView(ViewSet):
    permission_classes = [IsAuthenticated]
    '''购物相关的处理
    用户id 课程id 有效期 勾选状态
    '''

    def add_shop(self, request):
        # 课程id
        course_id = request.data.get('course_id')
        # 用户id
        user_id = request.user.id
        # 是否勾选
        select = True

        # 有效期
        expire = 0

        # 检验前端提交的参数

        try:
            Course.objects.get(is_show=True, id=course_id)
        except Course.DoesNotExist:
            return Response({"message": "参数有误，课程不存在"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取redis连接对象
            redis_connection = get_redis_connection("cart")
            # 将数据保存到redis
            pipeline = redis_connection.pipeline()
            # 管道开启
            pipeline.multi()
            pipeline.hset("cart_%s" % user_id, course_id, expire)
            # 被勾选的商品
            pipeline.sadd("selected_%s" % user_id, course_id)
            # 执行
            pipeline.execute()
            course_len = redis_connection.hlen("cart_%s" % user_id)

        except:
            logs.error("购物车数据储存失败")
            return Response({"message": "参数有误，购物车添加失败"}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        return Response({"message": "购物车商品添加成功", "cart_length": course_len})

    def list_cart(self, request):
        user_id = request.user.id
        redis_connection = get_redis_connection('cart')
        cart_list_bytes = redis_connection.hgetall('cart_%s' % user_id)
        select_list_bytes = redis_connection.smembers("selected_%s" % user_id)
        # print("cart_list",cart_list)
        # print("select_list",select_list)
        # 循环从mysql找出商品
        data = []
        for course_id_byte, expire_id_byte in cart_list_bytes.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)
            try:
                # 获取到的所有的课程信息
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:

                continue
            expire_text = "永久有效"
            if expire_id > 0:
                course_expire = CourseExpire.objects.get(id=expire_id)
                expire_text = course_expire.expire_text
            # 将购物车所需的信息返回
            data.append({
                "selected": True if course_id_byte in select_list_bytes else False,
                "course_img": constants.IMAGE_SRC + course.course_img.url,
                "name": course.name,
                "id": course_id,
                "expire_id": expire_id,
                # "price": course.real_price(),
                # 新增当前课程对应的有效期
                # 课程的有效期的
                'expire_list': course.expire_list,
                # "real_price":course.price,
                # TODO 获取真实价格
                # "real_price": course.real_expire_price(expire_id),
                "real_price": course.real_expire_price(expire_id),
            })

        return Response(data)

    def change_select(self, request):
        '''切换购物车状态'''
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')
        try:
            # 获取到的所有的课程信息
            Course.objects.get(is_show=True, is_delete=False, id=course_id)
        except Course.DoesNotExist:
            return Response({"message": "参数有误，当前商品不存在"}, status=status.HTTP_400_BAD_REQUEST)
        redis_connection = get_redis_connection('cart')
        if selected:
            # 讲商品添加到 set 代表选中
            redis_connection.sadd("selected_%s" % user_id, course_id)
            # redis_connection.add("selected_%s" % user_id, course_id)
        else:
            redis_connection.srem("selected_%s" % user_id, course_id)

        return Response({"message": "状态相同，切换成功"}, status=status.HTTP_200_OK)

    def delete_cart(self, request):
        '''删除购物车信信息'''
        user_id = request.user.id
        course_id = request.data.get('course_id')
        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({'message': '参数传递错误，没有相关课程'}, status=status.HTTP_400_BAD_REQUEST)
        redis_connection = get_redis_connection('cart')
        if course_id:
            redis_connection.hdel('cart_%s' % user_id, course_id)
        return Response({'message': '删除成功'}, status=status.HTTP_200_OK)

    def change_expiry(self, request):
        '''改变redis中课程的有效期'''
        user_id = request.user.id
        course_id = request.data.get("course_id")
        expire_id = request.data.get("expire_id")

        try:
            # 获取到的所有的课程信息
            course = Course.objects.get(is_show=True, is_delete=False, id=course_id)

            # 如果前段传递过来的有效期选项 不是0 修改有效期
            if expire_id > 0:
                expire_item = CourseExpire.objects.filter(is_show=True, is_delete=False, id=expire_id)
                if not expire_item:
                    raise Course.DoesNotExist()
        except Course.DoesNotExist:
            return Response({"message": "课程信息不存在"}, status=status.HTTP_400_BAD_REQUEST)

        connection = get_redis_connection("cart")
        connection.hset("cart_%s" % user_id, course_id, expire_id)

        # 重新计算有效期的价格
        real_price = course.real_expire_price(expire_id)

        return Response({"message": "切换有效期成功","real_price":real_price})


    def get_select(self,request):
        '''获取购物车中已勾选的商品  然后返回到前段也面处'''

        user_id = request.user.id
        redis_connection= get_redis_connection("cart")

        # //获取当前的商品【商品

        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("selected_%s" % user_id)

        total_price = 0 #要先计算一下商品的总价
        data = []

        for course_id_byte, expire_id_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_id = int(expire_id_byte)
            print(course_id,expire_id)

            # 判断商品的id时候已经在勾选状态了
            if course_id_byte in select_list:
                try:
                    # 获取到的所有的课程信息
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    continue
                # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                original_price = course.price
                expire_text = "永久有效"


                try:
                    if expire_id > 0:
                        course_expire = CourseExpire.objects.get(id=expire_id)
                        # 要也对应有效期的价格
                        original_price = course_expire.price
                        expire_text = course_expire.expire_text
                except CourseExpire.DoesNotExist:
                    pass

                # 根据已勾选的商品对应有效期的价格去计算最终的价钱
                real_expire_price = course.real_expire_price(expire_id)

                # 将购物车所需的信息返回
                data.append({
                    "course_img": constants.IMAGE_SRC + course.course_img.url,
                    "name": course.name,
                    "id": course.id,
                    # 新增当前课程对应的有效期
                    # 课程的有效期的
                    'expire_text': expire_text,
                    # 原价是
                    "price": original_price,
                    # TODO 获取真实价格  计算真实价格
                    "real_price": "%.2f" % float(real_expire_price),
                    # 活动名称
                    "activity_name":course.activity_name
                })
                #         商品的总价
                total_price += float(real_expire_price)

        return Response({"course_list":data,"total_price":total_price,"message":"成功获取"})




