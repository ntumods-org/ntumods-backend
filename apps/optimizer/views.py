from rest_framework import generics
from rest_framework.response import Response

from apps.optimizer.serializers import OptimizerInputSerialzer
from apps.optimizer.algo import optimize_index

from apps.optimizer.models import IndexSchedule

from apps.courses.models import (
    Course,
    CourseIndex,
    CourseSchedule,
)

combinations_threshold = 1000 # limit to 1000 combinations

class OptimizeView(generics.CreateAPIView):
    serializer_class = OptimizerInputSerialzer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = optimize_index(serializer.validated_data)
        return Response(output)

# bruteforce approach to generate schedule with all possible combinations of indices (select one index per course)
class GenScheduleView(generics.CreateAPIView):
    serializer_class = OptimizerInputSerialzer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        courses_code = serializer.validated_data['courses']
        courses = Course.objects.filter(code__in=courses_code)
        
        indices = CourseIndex.objects.filter(course__in=courses).select_related("course_code")
        course_idx_map = {}

        for idx in indices:
            course_idx_map.setdefault(idx.course_code.code, []).append(idx)
            
        # preprocess indices into IndexSchedule objects
        preprocessed = {}
        for course in courses:
            for idx in course_idx_map[course.code]:
                preprocessed[idx.index] = IndexSchedule(idx)
        
        # weekly mask: dictionary keyed by day
        days = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]
        empty_weekly_mask = {day: 0 for day in days}

        # exam map: date → bitmask
        empty_exam_map = {}
        
        def has_weekly_conflict(weekly_mask, idx: IndexSchedule):
            for day, mask in idx.week.items():
                if (weekly_mask.get(day, 0) & mask) != 0:
                    return True
            return False
        
        def has_exam_conflict(exam_map, idx: IndexSchedule):
            if idx.exam_date is None:
                return False
            
            if idx.exam_date not in exam_map:
                return False
            
            # conflict if overlapping exam slots
            if (exam_map[idx.exam_date] & idx.exam_mask) != 0:
                return True
            return False

        def merge_weekly(current_mask, idx: IndexSchedule):
            new_mask = current_mask.copy()
            for day, mask in idx.week.items():
                new_mask[day] = new_mask.get(day, 0) | mask
            return new_mask
        
        def merge_exam(exam_map, idx: IndexSchedule):
            new_map = exam_map.copy()
            if idx.exam_date:
                if idx.exam_date not in new_map:
                    new_map[idx.exam_date] = idx.exam_mask
                else:
                    new_map[idx.exam_date] |= idx.exam_mask
            return new_map
        
        results = []
        is_enough = [False]
        
        # dfs to explore all combinations
        def dfs(course_idx, chosen, weekly_mask, exam_map):
            if course_idx == len(courses):
                results.append(chosen.copy())
                if (len(results) >= combinations_threshold):
                    is_enough[0] = True
                return
            
            course_code = courses[course_idx].code
            for index_obj in course_idx_map[course_code]:
                if is_enough[0]:
                    return

                idx_schedule = preprocessed.get(index_obj.index)
                if not idx_schedule:
                    continue

                # check weekly conflict
                if has_weekly_conflict(weekly_mask, idx_schedule):
                    continue
                
                # check exam conflict
                if has_exam_conflict(exam_map, idx_schedule):
                    continue
                
                # choose
                new_weekly_mask = merge_weekly(weekly_mask, idx_schedule)
                new_exam_map = merge_exam(exam_map, idx_schedule)
                
                chosen.append(idx_schedule.index)
                dfs(course_idx + 1, chosen, new_weekly_mask, new_exam_map)
                if is_enough[0]:
                    return
                chosen.pop()

        dfs(0, [], empty_weekly_mask, empty_exam_map)
    
        return Response({
            "total_schedules": len(results),
            "schedules": results,
        })

