import xadmin

from course.models import Course, CourseCategory, CourseLesson, CourseChapter, Teacher, CourseDiscountType, \
    CourseDiscount, Activity, CoursePriceDiscount, CourseExpire


# 课程分类表
class CourseCateModelAdmin(object):
    pass


xadmin.site.register(CourseCategory, CourseCateModelAdmin)


# 课程信息表
class CourseModelAdmin(object):
    pass


xadmin.site.register(Course, CourseModelAdmin)


# 课程课时表
class CourseLessonModelAdmin(object):
    pass


xadmin.site.register(CourseLesson, CourseLessonModelAdmin)


# 课程章节表
class CourseChapterModelAdmin(object):
    pass


xadmin.site.register(CourseChapter, CourseChapterModelAdmin)


# 教师表
class TeacherModelAdmin(object):
    pass


xadmin.site.register(Teacher, TeacherModelAdmin)

"""课程优惠类型"""


class CourseDiscountTypeModelAdmin(object):
    pass


xadmin.site.register(CourseDiscountType, CourseDiscountTypeModelAdmin)


class CourseDiscountModelAdmin(object):
    """课程优惠折扣模型"""
    pass
xadmin.site.register(CourseDiscount, CourseDiscountModelAdmin)


class ActivityModelAdmin(object):
    """优惠活动"""
    pass
xadmin.site.register(Activity, ActivityModelAdmin)

class CoursePriceDiscountModelAdmin(object):
    """课程与优惠策略的关系表"""
    pass
xadmin.site.register(CoursePriceDiscount, ActivityModelAdmin)

class CourseExpireModelAdmin(object):
    """课程有效期模型"""
    pass
xadmin.site.register(CourseExpire, CourseExpireModelAdmin)