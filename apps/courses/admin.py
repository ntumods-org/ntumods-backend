from django.contrib import admin
from apps.courses.models import Course, CourseIndex


class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'last_updated', 'indexes_count']

    def indexes_count(self, obj):
        return obj.indexes.count()


class CourseIndexAdmin(admin.ModelAdmin):
    list_display = ['id', 'index', 'course']


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseIndex, CourseIndexAdmin)
