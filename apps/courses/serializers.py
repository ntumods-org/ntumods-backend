from rest_framework import serializers

from apps.courses.models import Course, CourseIndex, CourseProgram


class CoursePartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'id',
            'code',
            'name',
            'academic_units',
        ]


class CourseIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseIndex
        fields = [
            'id',
            'index',
            'get_information',
            'get_filtered_information',
            'schedule',
        ]


class CourseCompleteSerializer(serializers.ModelSerializer):
    indexes = CourseIndexSerializer(many=True, read_only=True)
    program_list = serializers.SerializerMethodField()
    prefix = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
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
        ]
        
    def get_program_list(self, obj):
        program_list = obj.program_list.split(', ') if obj.program_list else []
        return program_list
    
    def get_prefix(self, obj):
        return obj.prefix.prefix if obj.prefix else None


class CourseProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgram
        fields = [
            'id',
            'name',
            'value',
            'year',
        ]
