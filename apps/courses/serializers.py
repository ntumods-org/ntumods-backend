from rest_framework import serializers

from apps.courses.models import Course, CourseIndex, CourseProgram, CourseSchedule


class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = [
            'type',
            'group',
            'day',
            'time',
            'venue',
            'remark',
            'schedule',
        ]

class CoursePartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'code',
            'name',
            'academic_units',
        ]


class CourseIndexSerializer(serializers.ModelSerializer):
    schedules = CourseScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = CourseIndex
        fields = [
            'index',
            'get_information',
            'get_filtered_information',
            'schedules',
        ]


class CourseCompleteSerializer(serializers.ModelSerializer):
    indexes = CourseIndexSerializer(many=True, read_only=True)
    program_list = serializers.SerializerMethodField()
    common_schedules = CourseScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'code',
            'name',
            'academic_units',
            'prefix',
            'level',
            'last_updated',
            'get_exam_schedule',
            'get_common_information',
            'common_schedule',
            'indexes',
            'description',
            'prerequisite',
            'mutually_exclusive',
            'not_available',
            'not_available_all',
            'offered_as_ue',
            'offered_as_bde',
            'grade_type',
            'not_offered_as_core_to',
            'not_offered_as_pe_to',
            'not_offered_as_bde_ue_to',
            'department_maintaining',
            'program_list',
            'common_schedules',
        ]
        
    def get_program_list(self, obj):
        program_list = obj.program_list.split(', ') if obj.program_list else []
        return program_list


class CourseProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgram
        fields = [
            'id',
            'name',
            'value',
            'year',
        ]