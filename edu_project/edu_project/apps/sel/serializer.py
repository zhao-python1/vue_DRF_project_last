from datetime import datetime

from django.db import transaction     #事务的导包
from django_redis import get_redis_connection
from rest_framework import serializers, status
from rest_framework.response import Response
# from rest_framework.serializers import ModelSerializer

from course.models import Course, CourseExpire
from sel.models import Order, OrderDetail


class OrderModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_number", "pay_type")

        extra_kwargs = {
            "id": {"read_only": True},
            "order_number": {"read_only": True},
            "pay_type": {"write_only": True}
        }

    def validate(self, attrs):
        # 对支付类型进行验证判断处理
        pay_type = attrs.get("pay_type")
        try:
            Order.pay_choices[pay_type]
        except Order.DoesNotExist:
            raise serializers.ValidationError("你的支付类型不在我们的服务范围内，很抱歉")
        return attrs

    # 需要重新写create方法生成订单
    def create(self, validated_data):
        """生成订单与订单详情"""
        redis_connection = get_redis_connection('cart')   #连接到Redis数据库
        # k可以通过context获取到request对象
        user_id = self.context["request"].user.id
        # user_id = 1
        incr = redis_connection.incr("order")

        # 生成唯一的订单号  时间戳  用户id  随机字符串
        order_number = datetime.now().strftime("%Y%m%d%H%M%S") + "%06d" % user_id + "%06d" % incr
        # 生成订单
        order = Order.objects.create(
            order_title="我是订单标题",
            total_price=0,
            real_price=0,
            order_number=order_number,
            order_status=0,
            pay_type=validated_data.get("pay_type"),
            credit=0,
            coupon=0,
            order_desc="这是一个订单",
            user_id=user_id
        )
        #开启事务
        with transaction.atomic():
            # 记录下事务回滚的点 下面的内容出错的话返回到这个位置
            rollback = transaction.savepoint()
            # 生成订单详情
            # 获取当前用户购物车中所有的商品
            cart_list = redis_connection.hgetall("cart_%s" % user_id)
            select_list = redis_connection.smembers("selected_%s" % user_id)

            for course_id_byte, expire_id_byte in cart_list.items():
                course_id = int(course_id_byte)
                expire_id = int(expire_id_byte)

                # 在这判断商品是否2在这里
                if course_id_byte in select_list:
                    try:
                        # 获取到的所有的课程信息
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        # 如果订单吃错则回滚数据
                        transaction.savepoint_rollback(rollback)
                        return serializers.ValidationError("对不起，您访问的商品开小差了")

                    # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                    original_price = course.price
                    course_text = '永久有效'
                    try:
                        if expire_id > 0:
                            course_expire = CourseExpire.objects.get(id=expire_id)
                            # 拿到有效期的原价
                            original_price = course_expire.price
                            lef_text = course_expire.expire_text
                    except CourseExpire.DoesNotExist:
                        transaction.savepoint_rollback(rollback)
                    #  在这里计算优惠过后的价钱 并且是已勾选的
                    real_expire_price = course.real_expire_price(expire_id)
                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(
                            order=order,
                            course=course,
                            expire=expire_id,
                            price=original_price,
                            real_price=real_expire_price,
                            discount_name=course.activity_name
                    )
                    except:
                        # 如果订单吃错则回滚数据
                        transaction.savepoint_rollback(rollback)
                        raise serializers.ValidationError("订单生成失败")

                    # 计算订单总价
                    order.total_price += float(original_price)
                    order.real_price += float(real_expire_price)
                    # 生成之后删除购物车里的商品
                    redis_connection.hdel("cart_%s" % user_id, course_id)
                    redis_connection.srem("selected_%s" % user_id, course_id)
                order.save()
            return order












