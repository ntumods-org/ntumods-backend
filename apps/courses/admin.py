from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from apps.courses.models import Course, CourseIndex, CoursePrefix, CourseProgram, CoursePrerequisite, PrerequisiteGraph


class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'AU', 'level', 'prefix', 'last_updated', 'indexes_count']

    def AU(self, obj):
        return obj.academic_units
    AU.short_description = 'AU'

    def indexes_count(self, obj):
        return obj.indexes.count()


class CourseIndexAdmin(admin.ModelAdmin):
    list_display = ['id', 'index', 'course']


class CoursePrefixAdmin(admin.ModelAdmin):
    list_display = ['id', 'prefix', 'last_updated', 'courses_count']
    readonly_fields = ['courses_count', 'courses_list']

    def courses_count(self, obj):
        return Course.objects.filter(code__startswith=obj.prefix).count()

    def courses_list(self, obj):
        courses = Course.objects.filter(code__startswith=obj.prefix).values_list('code', 'name')
        if courses:
            course_list_html = format_html_join(
                mark_safe('<br>'),
                '{}: {}',
                ((code, name) for code, name in courses)
            )
            return format_html('<strong>Courses:</strong><br>{}', course_list_html)
        else:
            return "No courses found."
    
    courses_list.short_description = "Courses with this prefix"


class CourseProgramAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'year', 'value', 'last_updated', 'courses_count']
    search_fields = ['name', 'year', 'value']
    list_filter = ['year']
    
    def courses_count(self, obj):
        return obj.courses.count()


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseIndex, CourseIndexAdmin)
admin.site.register(CoursePrefix, CoursePrefixAdmin)
admin.site.register(CourseProgram, CourseProgramAdmin)
admin.site.register(CoursePrerequisite)
admin.site.register(PrerequisiteGraph)
