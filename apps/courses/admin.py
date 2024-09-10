from django.contrib import admin
from apps.courses.models import Course, CourseIndex, CourseProgram


class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'last_updated', 'indexes_count']

    def indexes_count(self, obj):
        return obj.indexes.count()


class CourseIndexAdmin(admin.ModelAdmin):
    list_display = ['id', 'index', 'course']


class CourseProgramAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'year', 'value', 'last_updated', 'courses_count']
    search_fields = ['name', 'year', 'value']
    list_filter = ['year']
    
    def courses_count(self, obj):
        return obj.courses.count()


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseIndex, CourseIndexAdmin)
admin.site.register(CourseProgram, CourseProgramAdmin)
