from apps.courses.models import (
    Course,
    CourseIndex,
    CourseSchedule,
)

def mask_from_string(schedule_str: str) -> int:
    mask = 0
    for i, char in enumerate(schedule_str):
        if char == 'X':
            mask |= (1 << i)
    return mask

class IndexSchedule:
    def __init__(self, index: CourseIndex):
        self.index = index.index
        self.course = index.course_code.code
        
        converted_weekly_schedules = {}
        for sched in index.schedules.all():
            mask = mask_from_string(sched.schedule)
            converted_weekly_schedules[sched.day] = mask
        self.week = converted_weekly_schedules
        
        exam = index.course_code.get_exam_schedule
        if exam:
            self.exam_date = exam.get("date")
            timecode = exam.get("timecode", "")
            self.exam_mask = mask_from_string(timecode) if timecode else 0
        else:
            self.exam_date = None
            self.exam_mask = None
