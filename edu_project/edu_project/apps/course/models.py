from datetime import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models

# from course.utils.BaseModel import BaseModel
from course.BaseModel import BaseModel


class CourseCategory(BaseModel):
    """
    课程分类
    """
    name = models.CharField(max_length=64, unique=True, verbose_name="分类名称")

    class Meta:
        db_table = "bz_course_category"
        verbose_name = "课程分类"
        verbose_name_plural = "课程分类"

    def __str__(self):
        return "%s" % self.name


class Course(BaseModel):
    """
    专题课程
    """
    course_type = (
        (0, '收费课程'),
        (1, '高级课程'),
        (2, '专业技能')
    )
    level_choices = (
        (0, '入门'),
        (1, '进阶'),
        (2, '大师'),
    )
    status_choices = (
        (0, '上线'),
        (1, '下线'),
        (2, '预上线'),
    )
    videos = models.FileField(upload_to='video', null=True, blank=True, verbose_name="视频")
    name = models.CharField(max_length=128, verbose_name="课程名称")
    course_img = models.ImageField(upload_to="course", max_length=255, verbose_name="封面图片", blank=True, null=True)
    course_type = models.SmallIntegerField(choices=course_type, default=0, verbose_name="付费类型")
    # 使用这个字段的原因
    brief = RichTextUploadingField(max_length=2048, verbose_name="详情介绍", null=True, blank=True)
    # brief = models.TextField(max_length=2048, verbose_name="详情介绍", null=True, blank=True)
    level = models.SmallIntegerField(choices=level_choices, default=1, verbose_name="难度等级")
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)
    period = models.IntegerField(verbose_name="建议学习周期(day)", default=7)
    file_path = models.FileField(max_length=128, verbose_name="课件路径", blank=True, null=True)
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="课程状态")
    course_category = models.ForeignKey("CourseCategory", on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name="课程分类")
    students = models.IntegerField(verbose_name="学习人数", default=0)
    lessons = models.IntegerField(verbose_name="总课时数量", default=0)
    pub_lessons = models.IntegerField(verbose_name="课时更新数量", default=0)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程原价", default=0)
    teacher = models.ForeignKey("Teacher", on_delete=models.DO_NOTHING, null=True, blank=True, verbose_name="授课老师")

    class Meta:
        db_table = "bz_course"
        verbose_name = "专题课程"
        verbose_name_plural = "专题课程"

    def __str__(self):
        return "%s" % self.name

    @property
    def lesson_list(self):
        "获取当前课程的前几节课程用于展示"

        lesson_list = CourseLesson.objects.filter(is_show=True, is_delete=False, course_id=self.id).all()

        data_list = []
        for lesson in lesson_list:
            data_list.append({
                "id": lesson.id,
                "name": lesson.name,
                "free_trail": lesson.free_trail,
            })

        return data_list

    # 定义一个自定义字段
    @property
    def level_style(self):
        return self.level_choices[self.level][1]

    @property
    def brief_html(self):
        brief = self.brief.replace('src="/media', 'src="%s/media' % "http://api.baizhis.com:9001")
        return brief

    def active_list(self):
        # 当前课程所对应的活动列表
        # 活动开始时间必须大于当前时间活动结束时间必须小于当前时间
        return self.activeprices.filter(is_show=True, is_delete=False, active__start_time__lte=datetime.now(),
                                        active__end_time__gte=datetime.now(), ).order_by("-orders", "-id")

    @property
    def activity_name(self):
        """ 如果当前课程参与了活动 返回当前课程所对应的优惠活动名称"""
        name = ""
        # 当前课程所对应的活动列表
        # 活动开始时间必须大于当前时间活动结束时间必须小于当前时间
        active_list = self.active_list()
        if len(active_list) > 0:
            """当前课程参与了活动才返回优惠类型名称"""
            active = active_list[0]
            name = active.discount.discount_type.name
        return name

    def now_price(self):
        '''完成对价格的修改'''
        # 获取当前价格
        price = self.price
        # 找到当前当前课程所参与的活动
        active_list = self.active_list()
        self.price = float(self.price)
        if len(active_list) > 0:
            # 如果存在课程 根据课程所参与的活动计算价格
            active = active_list[0]
            # 优先判断活动是否满足价格门槛
            # 优惠价格
            condition = active.discount.condition
            sale = active.discount.sale
            # 判断属于那种优惠价格
            if self.price >= condition:
                # 判断当前满足哪一种优惠条件
                if sale == "":
                    # 免费
                    price = 0
                elif sale[0] == '*':
                    # 折扣
                    price = self.price * float(sale[1:])
                elif sale[0] == "-":
                    # 减免
                    price = self.price - float(sale[1:])
                elif sale[0] == "满":
                    # 满减
                    sale_split = sale.split("\r\n")
                    print(sale_split)
                    # 把当前课程满足的放在列表中
                    price_list = []
                    for sale_item in sale_split:
                        item = sale_item[1:]
                        condition_price, condition_sale = item.split('-')
                        if self.price >= float(condition_price):
                            price_list.append(float(condition_sale))
                    if len(price_list) > 0:
                        price = self.price - max(price_list)  # 课程原价-当前见面的价格
            # 找到活动的  价格公示
            return price

    def real_expire_price(self, expire_id=0):
        original_price = self.price
        try:
            if expire_id > 0:
                # 如果有效期id存在  则回去有效期id所对应的价格
                original_price = CourseExpire.objects.get(id=expire_id).price
        except CourseExpire.DoesNotExist:
            pass
    #
        price = original_price
        # 找到当前课程所参与的活动
        active_list = self.active_list()
    #
        if len(active_list) > 0:
            """如果课程对应的活动存在  则根据课程所参与的活动的规则来计算价格"""
            active = active_list[0]

            # 判断原价是否满足优惠的门槛
            condition = active.discount.condition
            sale = active.discount.sale

            self.price = float(price)

            if self.price >= condition:
                # 判断当前课程满足哪一种优惠条件
                if sale == "":
                    # 限时免费
                    price = 0
                elif sale[0] == "*":
                    # 折扣
                    price = self.price * float(sale[1:])
                elif sale[0] == "-":
                    # 减免
                    price = self.price - float(sale[1:])
                elif sale[0] == "满":
                    """满减  500-80  400-40 300-20 200-10"""
                    sale_split = sale.split("\r\n")
                    # 把当前课程价格所满足的条件放入列表中
                    price_list = []
                    for sale_item in sale_split:
                        item = sale_item[1:]
                        condition_price, condition_sale = item.split("-")
                        if self.price >= float(condition_price):
                            price_list.append(float(condition_sale))
                    if len(price_list) > 0:
                        price = self.price - max(price_list)  # 课程原价减去当前满足条件的最大优惠
        return "%.2f" % price

    @property
    def now_time(self):
        '''计算当前课程参与活动的剩余时间'''
        time = [],
        active_list = self.active_list()
        if len(active_list) > 0:
            active = active_list[0]
            # 获取当前的时间戳
            nows_time = datetime.now().timestamp()
            # 获取活动结束的时间戳
            end_time = active.active.end_time.timestamp()
            time = end_time - nows_time
        return int(time)

    # 有效期的书写
    @property
    def expire_list(self):
        expirse = self.course_expire.filter(is_show=True, is_delete=False)
        data = []
        for item in expirse:
            data.append({
                "id": item.id,
                "expire_text": item.expire_text,
                'price': item.price,
            })
        if self.price > 0:
            data.append({
                "id": 0,
                "expire_text": "永久有效",
                'price': self.price,
            })
        return data


class Teacher(BaseModel):
    """讲师、导师表"""
    role_choices = (
        (0, '讲师'),
        (1, '班主任'),
        (2, '教学总监'),
    )
    name = models.CharField(max_length=32, verbose_name="讲师title")
    role = models.SmallIntegerField(choices=role_choices, default=0, verbose_name="讲师身份")
    title = models.CharField(max_length=64, verbose_name="职称")
    signature = models.CharField(max_length=255, verbose_name="导师签名", help_text="导师签名", blank=True, null=True)
    image = models.ImageField(upload_to="teacher", null=True, verbose_name="讲师封面")
    brief = models.TextField(max_length=1024, verbose_name="讲师描述")

    class Meta:
        db_table = "bz_teacher"
        verbose_name = "讲师导师"
        verbose_name_plural = "讲师导师"

    def __str__(self):
        return "%s" % self.name


class CourseChapter(BaseModel):
    """课程章节"""
    course = models.ForeignKey("Course", related_name='coursechapters', on_delete=models.CASCADE, verbose_name="课程名称")
    chapter = models.SmallIntegerField(verbose_name="第几章", default=1)
    name = models.CharField(max_length=128, verbose_name="章节标题")
    summary = models.TextField(verbose_name="章节介绍", blank=True, null=True)
    pub_date = models.DateField(verbose_name="发布日期", auto_now_add=True)

    class Meta:
        db_table = "bz_course_chapter"
        verbose_name = "课程章节"
        verbose_name_plural = "课程章节"

    def __str__(self):
        return "%s:(第%s章)%s" % (self.course, self.chapter, self.name)


class CourseLesson(BaseModel):
    """课程课时"""
    section_type_choices = (
        (0, '文档'),
        (1, '练习'),
        (2, '视频')
    )
    chapter = models.ForeignKey("CourseChapter", related_name='coursesections', on_delete=models.CASCADE,
                                verbose_name="课程章节")
    name = models.CharField(max_length=128, verbose_name="课时标题")
    section_type = models.SmallIntegerField(default=2, choices=section_type_choices, verbose_name="课时种类")
    section_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="课时链接",
                                    help_text="若是video，填vid,若是文档，填link")
    duration = models.CharField(verbose_name="视频时长", blank=True, null=True, max_length=32)  # 仅在前端展示使用
    pub_date = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    free_trail = models.BooleanField(verbose_name="是否可试看", default=False)
    course = models.ForeignKey("Course", related_name="course_lesson", on_delete=models.CASCADE, verbose_name="课程")
    is_show_list = models.BooleanField(verbose_name="是否展示到课程", default=False)

    # lesson = models.IntegerField(verbose_name="第几个课时", default="第一个")

    class Meta:
        db_table = "bz_course_lesson"
        verbose_name = "课程课时"
        verbose_name_plural = "课程课时"

    def __str__(self):
        return "%s-%s" % (self.chapter, self.name)


# 满减价格表


class CourseDiscountType(BaseModel):
    """课程优惠类型"""
    name = models.CharField(max_length=32, verbose_name="优惠类型名称")
    remark = models.CharField(max_length=250, blank=True, null=True, verbose_name="备注信息")

    class Meta:
        db_table = "bz_course_discount_type"
        verbose_name = "课程优惠类型"
        verbose_name_plural = "课程优惠类型"

    def __str__(self):
        return "%s" % (self.name)


class CourseDiscount(BaseModel):
    """课程优惠折扣模型"""
    discount_type = models.ForeignKey("CourseDiscountType", on_delete=models.CASCADE, related_name='coursediscounts',
                                      verbose_name="优惠类型")
    condition = models.IntegerField(blank=True, default=0, verbose_name="满足优惠的价格条件",
                                    help_text="设置参与优惠的价格门槛，表示商品必须在xx价格以上的时候才参与优惠活动，<br>如果不填，则不设置门槛")
    sale = models.TextField(verbose_name="优惠公式", blank=True, null=True, help_text="""
    不填表示免费；<br>
    *号开头表示折扣价，例如*0.82表示八二折；<br>
    -号开头则表示减免，例如-20表示原价-20；<br>
    如果需要表示满减,则需要使用 原价-优惠价格,例如表示课程价格大于100,优惠10;大于200,优惠20,格式如下:<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;满100-10<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;满200-25<br>
    """)

    class Meta:
        db_table = "bz_course_discount"
        verbose_name = "价格优惠策略"
        verbose_name_plural = "价格优惠策略"

    def __str__(self):
        return "价格优惠:%s,优惠条件:%s,优惠值:%s" % (self.discount_type.name, self.condition, self.sale)


class Activity(BaseModel):
    """优惠活动"""
    name = models.CharField(max_length=150, verbose_name="活动名称")
    start_time = models.DateTimeField(verbose_name="优惠策略的开始时间")
    end_time = models.DateTimeField(verbose_name="优惠策略的结束时间")
    remark = models.CharField(max_length=250, blank=True, null=True, verbose_name="备注信息")

    class Meta:
        db_table = "bz_activity"
        verbose_name = "商品活动"
        verbose_name_plural = "商品活动"

    def __str__(self):
        return self.name


class CoursePriceDiscount(BaseModel):
    """课程与优惠策略的关系表"""
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="activeprices", verbose_name="课程")
    active = models.ForeignKey("Activity", on_delete=models.DO_NOTHING, related_name="activecourses", verbose_name="活动")
    discount = models.ForeignKey("CourseDiscount", on_delete=models.CASCADE, related_name="discountcourse",
                                 verbose_name="优惠折扣")

    class Meta:
        db_table = "bz_course_price_discount"
        verbose_name = "课程与优惠策略的关系表"
        verbose_name_plural = "课程与优惠策略的关系表"

    def __str__(self):
        return "课程：%s，优惠活动: %s,开始时间:%s,结束时间:%s" % (
            self.course.name, self.active.name, self.active.start_time, self.active.end_time)


class CourseExpire(BaseModel):
    """课程有效期模型"""
    course = models.ForeignKey("Course", related_name='course_expire', on_delete=models.CASCADE,
                               verbose_name="课程名称")
    expire_time = models.IntegerField(verbose_name="有效期", null=True, blank=True, help_text="有效期按天数计算")
    expire_text = models.CharField(max_length=150, verbose_name="提示文本", null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程价格", default=0)

    class Meta:
        db_table = "bz_course_expire"
        verbose_name = "课程有效期"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "课程：%s，有效期：%s，价格：%s" % (self.course, self.expire_text, self.price)
