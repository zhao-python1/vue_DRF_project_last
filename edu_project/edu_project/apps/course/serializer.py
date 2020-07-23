from rest_framework.serializers import ModelSerializer

from course.models import CourseCategory, Course, Teacher, CourseLesson, CourseChapter


class CourseCategorySerializer(ModelSerializer):
    '''
    课程的分类
    '''

    class Meta:
        model = CourseCategory
        fields = ['id', 'name']


class CourseTeacherSerlalizer(ModelSerializer):
    '''课程所属老师的序列化器'''

    class Meta:
        model = Teacher
        fields = ("id", "name", "title", "signature")


#
class CourseModelSerializer(ModelSerializer):
    '''课程列表'''
    # 序列化器嵌套查询老师信息
    teacher = CourseTeacherSerlalizer()
    '''给一个活动的名字  优惠活动的名称"activity_name" '''
    class Meta:
        model = Course
        fields = ["id", "name", "course_img", "students", "lessons",
                  "pub_lessons", "price", "teacher", "lesson_list",'brief_html',"activity_name","now_price"]


class CourseTeacherSerializer(ModelSerializer):
    '''课程对应的老师的信息'''

    class Meta:
        model = Teacher
        fields = ['id', 'name', 'signature', 'image', 'role', 'brief','title']


class CourseLessonModelSerializer(ModelSerializer):
    '''课程详细信息序列化器'''
    '''序列化器嵌套的时候 必须有外键的'''
    teacher = CourseTeacherSerializer()

    # lesson_course = CourseDetailSerializer()
    class Meta:
        model = Course
        fields = ["id", "name", "level_style", "students", "lessons",
                  "pub_lessons", "price", "teacher", "course_img","videos",'brief_html',"activity_name",'now_time',"now_price"]



class CourseLessonsModelSerializer(ModelSerializer):
    class Meta:
        model = CourseLesson
        fields = ["id","name","free_trail"]

class CourseCapterModelSerializer(ModelSerializer):

    #一对多需要many
    coursesections = CourseLessonsModelSerializer(many=True)
    '''章节对应的课时'''
    class Meta:
        model = CourseChapter
        fields= ['id',"name","chapter","coursesections"]



