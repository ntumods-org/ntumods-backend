from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.courses.validations import (
    validate_index,
    validate_exam_schedule,
    validate_information,
    validate_weekly_schedule,
)


class CoursePrefix(models.Model):
    '''
    Store unique course code prefixes, e.g. 'MH', 'SC', 'E', 'AAA', etc.
    Used for a filter feature in the frontend for searching courses by prefix.
    '''
    prefix = models.CharField(max_length=3, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Course Prefixes'
    
    def __str__(self):
        return f'<{self.prefix}>'


class Course(models.Model):
    '''
    General information about a course.

    `code` is the course code, e.g. 'MH1100', 'SC1007', 'MH3700', etc.
    `name` is the course title, e.g. 'Calculus I', 'Data Structures and Algorithms', etc.
    `academic_units` is the number of academic units for the course.
    `last_updated` is the last date and time the Course instance was updated.
    '''
    code = models.CharField(max_length=6, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    academic_units = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    last_updated = models.DateTimeField(auto_now=True)

    '''
    Derived information: can be gained from the course code, but stored separately for easier access.
    
    `level` is determined by the first non-letter character in the course code.
    Currently, only levels 1 to 5 are stored, with the rest stored as 10.
    If the number after the letters is less than 4 digits, it is stored as 10.
    Example: lv1: MH1101, SC1003; lv3: MH3700, E3102L; level 10: AAA28R, AGE18A, ES9003.

    `program_code` are the characters up to and excluding the first non-letter character in the course code.
    Example: MH1101 -> program_code = 'MH'; SC1003 -> program_code = 'SC';
    AAA28R -> program_code = 'AAA'; E3102L -> program_code = 'E'.
    '''
    level = models.CharField(max_length=2, null=True, blank=True)
    prefix = models.CharField(max_length=3, null=True, blank=True)

    '''
    Additional information: further details about a course.
    All of these data are stored as strings, and may not be present for all courses.
    '''
    description = models.TextField(null=True, blank=True)
    prerequisite = models.TextField(null=True, blank=True)
    mutually_exclusive = models.TextField(null=True, blank=True)
    not_available = models.TextField(null=True, blank=True)
    not_available_all = models.TextField(null=True, blank=True)
    offered_as_ue = models.BooleanField(default=True)
    offered_as_bde = models.BooleanField(default=True)
    grade_type = models.CharField(max_length=300, null=True, blank=True)
    not_offered_as_core_to = models.TextField(null=True, blank=True)
    not_offered_as_pe_to = models.TextField(null=True, blank=True)
    not_offered_as_bde_ue_to = models.TextField(null=True, blank=True)
    department_maintaining = models.CharField(max_length=50, null=True, blank=True)
    program_list = models.CharField(max_length=1000, null=True, blank=True)
    
    '''
    Exam and Course schedule.

    Let (S) denotes a 32 character string, each character represent 30 minutes interval,
    from 8am to 24pm, 16 hours in total. The character is 'X' if the interval is occupied,
    otherwise it is 'O'. The first character represents 8am to 8.30am, and so on.
    For example, 'OOOXXXXOOOOOOOOOOOOOOOOOOOOOOOOO' means that 9.30am to 11.30am is occupied.

    `exam_schedule` is stored in the following format:
    YYYY-MM-DDHH:MM-HH:MM(S)
    Example: 2023-11-0713:00-15:00OOOOOOOOOOXXXXOOOOOOOOOOOOOOOOOO
    Interpretation: Exam is on 7 Nov 2023, 1pm to 3pm.

    `common_schedule` is stored in the following format:
    (S)(S)(S)(S)(S)(S)
    Each (S) represents a day of the week, from Monday to Saturday.
    Common schedule are the occupied time slots that are common in all indexes of the course.
    '''
    exam_schedule = models.CharField(max_length=53, blank=True, validators=[validate_exam_schedule])
    common_schedule = models.CharField(max_length=192, validators=[validate_weekly_schedule], null=True, blank=True)

    '''
    Information that is common across all indexes of the course.
    This field is derived from `information` field in CourseIndex model.
    A single information group is stored in the following format:
    type^group^day^time^venue^remark, with '^' as the separator.
    '''
    common_information = models.TextField(null=True, blank=True, validators=[validate_information])

    prerequisites_tree = models.JSONField(null=True, blank=True)

    scraped_for = models.CharField(max_length=100, null=True, blank=True)

    @property
    def get_common_information(self):
        def serialize_info(info):
            single_infos = info.split('^')
            return {
                'type': single_infos[0],
                'group': single_infos[1],
                'day': single_infos[2],
                'time': single_infos[3],
                'venue': single_infos[4],
                'remark': single_infos[5],
            }
        return [serialize_info(info_group) for info_group in self.common_information.split(';')] if \
            self.common_information else []
    
    @property
    def get_exam_schedule(self):
        if self.exam_schedule == '':
            return None
        return {
            'date': self.exam_schedule[:10],
            'time': self.exam_schedule[10:21],
            'timecode': self.exam_schedule[21:],
        }

    class Meta:
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f'<{self.code}: {self.name}>'


class CourseIndex(models.Model):
    '''
    General information about a course index.

    `course` is the course that the index belongs to.
    `index` is a unique index number, e.g. '70501', '70523', '15104', etc.
    `information` stores the information about the index, in the following format:
    type^group^day^time^venue^remark;type^group^day^time^venue^remark;...
    Example: LEC^1^MON^08:30-10:30^LT1^;TUT^1^WED^08:30-10:30^TR1^
    `schedule` stores the weekly schedule of the index, in the following format:
    (S)(S)(S)(S)(S)(S), refer to `common_schedule` in Course model for more details.
    '''
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='indexes', to_field='code')
    index = models.CharField(max_length=5, unique=True, validators=[validate_index], primary_key=True)
    # schedule = models.CharField(max_length=192)
    
    '''
    Filtered information are `information` that are not common across all indexes of the course.
    '''
    filtered_information = models.TextField(null=True, blank=True, validators=[validate_information])
    
    def serialize_info(self, info):
        single_infos = info.split('^')
        return {
            'type': single_infos[0],
            'group': single_infos[1],
            'day': single_infos[2],
            'time': single_infos[3],
            'venue': single_infos[4],
            'remark': single_infos[5],
        }
    
    @property
    def get_filtered_information(self):
        return [self.serialize_info(info_group) for info_group in self.filtered_information.split(';')] if \
            self.filtered_information else []

    class Meta:
        verbose_name_plural = 'Course Indexes'

    def __str__(self):
        return f'<Index {self.index} for course {self.course_code}>'


class CourseSchedule(models.Model):
    index = models.ForeignKey(CourseIndex, on_delete=models.CASCADE, related_name='schedules', to_field='index', null=True)
    type = models.CharField(max_length=200)
    group = models.CharField(max_length=200)
    day = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    remark = models.CharField(max_length=200)
    schedule = models.CharField(max_length=200)
    common_schedule_for_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='common_schedules', to_field='code', null=True)


class CourseProgram(models.Model):
    '''
    CourseProgram and Course are in a many-to-many relationship.
    CourseProgram instances also include minor programs and bachelor degree program with year, examples:
    - Mathematical And Computer Sciences Year 4
    - Minor in Computing And Data Analysis
    etc.

    `name` is the name of the program, e.g. 'Accountancy (GA) Year 1'.
    `value` is based on the value attribute in the HTML option tag of the html, e.g. 'ACC;GA;1;F'.
    `last_updated` is the last date and time the CourseProgram instance was updated.
    `year` is the year of the program, derived from the value attribute, may be empty if not applicable (such as minor programs).
    '''
    name = models.CharField(max_length=300, unique=True)
    value = models.CharField(max_length=300, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    courses = models.ManyToManyField(Course, related_name='programs')
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Course Programs'

    def __str__(self):
        return f'<CourseProgram #{self.id}: {self.name}>'


class CoursePrerequisite(models.Model):
    '''
    Stores the prerequisite requirements for a given course.
    CoursePrerequisite and Course have a one-to-one relationship.

    `course` is the course that the prerequisite belongs to.
    `child_nodes` is a JSON structure specifying the prerequisite courses required for the `course`.
    Example:
    - "MH1810"
    - {"or": [{"and": ["MH1200", "MH1811"]}, {"and": ["MH1100", {"and": ["MH1810", "MH1300"]}]}]}
    '''
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    child_nodes = models.JSONField()

    class Meta:
        verbose_name_plural = 'Course Prerequisites'

    def __str__(self):
        return f'<CoursePrerequisite for course {self.course.code}: {self.child_nodes}>'

class PrerequisiteGraph(models.Model):
    '''
    Stores the prerequisite graph for all courses.
    '''
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    prerequisite_graph = models.JSONField()

    class Meta:
        verbose_name_plural = 'Prerequisite Graph'

    def __str__(self):
        return f'<Prerequisite graph for course {self.course.code}: {self.prerequisite_graph}>'