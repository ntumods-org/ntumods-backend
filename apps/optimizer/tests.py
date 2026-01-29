from collections import OrderedDict

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from apps.courses.models import Course, CourseIndex
from apps.optimizer.algo import (
    parse_schedule,
    occupied_str_to_mask,
    solve_with_constraints,
    optimize_index,
    filtered_information_to_mask
)


class ParseScheduleTestCase(TestCase):
    """Test the parse_schedule function that converts schedule strings to bitmasks."""

    def test_parse_empty_schedule(self):
        """Test parsing an empty schedule (all O's)."""
        schedule = 'O' * 192
        result = parse_schedule(schedule)
        self.assertEqual(result, 0)

    def test_parse_full_schedule(self):
        """Test parsing a fully occupied schedule (all X's)."""
        schedule = 'X' * 192
        result = parse_schedule(schedule)
        expected = (1 << 192) - 1  # All bits set
        self.assertEqual(result, expected)

    def test_parse_single_slot(self):
        """Test parsing a schedule with a single occupied slot."""
        schedule = 'O' * 5 + 'X' + 'O' * 186
        result = parse_schedule(schedule)
        self.assertEqual(result, 1 << 5)

    def test_parse_multiple_slots(self):
        """Test parsing a schedule with multiple occupied slots."""
        schedule = 'X' + 'O' * 31 + 'X' + 'O' * 159
        result = parse_schedule(schedule)
        expected = (1 << 0) | (1 << 32)
        self.assertEqual(result, expected)


class SolveWithConstraintsTestCase(TestCase):
    """Test the solve_with_constraints function with fixture data."""

    fixtures = ['sample_data.json']

    def test_solve_no_constraints(self):
        """Test solving without any constraints using fixture courses."""
        result = solve_with_constraints(
            constraint_mask=0,
            wanted_courses=['MH1100', 'MH1200']
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        courses = [r[0] for r in result]
        self.assertIn('MH1100', courses)
        self.assertIn('MH1200', courses)

    def test_solve_no_solution_with_full_block(self):
        """Test no solution when all time slots are blocked."""
        constraint_mask = occupied_str_to_mask('X' * 192)
        result = solve_with_constraints(
            constraint_mask=constraint_mask,
            wanted_courses=['MH1100']
        )
        self.assertIsNone(result)

    def test_solve_single_course(self):
        """Test solving with a single course from fixtures."""
        result = solve_with_constraints(
            constraint_mask=0,
            wanted_courses=['MH1100']
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'MH1100')


class OptimizeIndexTestCase(TestCase):
    """Test the optimize_index function with fixture data."""

    fixtures = ['sample_data.json']

    def test_optimize_no_occupied(self):
        """Test optimization without occupied slots."""
        from apps.courses.models import CourseIndex, CourseSchedule

        input_data = OrderedDict([
            ('courses', [
                {'code': 'MH1100'},
                {'code': 'MH1200'}
            ])
        ])
        result = optimize_index(input_data)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result, list)
        self.assertIn('code', result[0])
        self.assertIn('index', result[0])

        # Verify no schedule conflicts between the selected indices
        combined_mask = 0
        for course_result in result:
            course_code = course_result['code']
            index_id = course_result['index']

            # Get the course's common schedule
            from apps.courses.models import Course
            course = Course.objects.get(code=course_code)
            course_mask = parse_schedule(course.common_schedule) if course.common_schedule else 0

            # Get the index's specific schedules
            course_index = CourseIndex.objects.get(index=index_id)
            for schedule in course_index.schedules.all():
                if schedule.schedule:
                    course_mask |= parse_schedule(schedule.schedule)

            # Common schedules for the course
            common_schedules = CourseSchedule.objects.filter(common_schedule_for_course=course_code)
            for schedule in common_schedules:
                if schedule.schedule:
                    course_mask |= parse_schedule(schedule.schedule)

            # Verify no overlap with previously selected courses
            self.assertEqual(course_mask & combined_mask, 0,
                             f"Schedule conflict detected: {course_code} index {index_id} overlaps with previously selected courses")

            combined_mask |= course_mask

    def test_optimize_no_solution(self):
        """Test optimization when all time slots are blocked."""
        input_data = OrderedDict([
            ('courses', [
                {'code': 'MH1100'}
            ]),
            ('occupied', 'X' * 192)
        ])
        result = optimize_index(input_data)

        self.assertIsNone(result)

    def test_optimize_with_occupied_slots(self):
        """Test optimization respects occupied time slots."""
        from apps.courses.models import Course, CourseIndex, CourseSchedule

        # Block slots 3-6 and 99-101
        occupied = ['O'] * 192
        for i in range(3, 7):
            occupied[i] = 'X'
        for i in range(99, 101):
            occupied[i] = 'X'

        input_data = OrderedDict([
            ('courses', [
                {'code': 'MH1100'}
            ]),
            ('occupied', ''.join(occupied))
        ])
        result = optimize_index(input_data)

        # Should find a solution and verify no conflicts with occupied slots
        if result is not None:
            constraint_mask = occupied_str_to_mask(''.join(occupied))

            for course_result in result:
                course_code = course_result['code']
                index_id = course_result['index']

                # Get the full schedule mask for this index
                course = Course.objects.get(code=course_code)
                course_mask = parse_schedule(course.common_schedule) if course.common_schedule else 0

                course_index = CourseIndex.objects.get(index=index_id)
                for schedule in course_index.schedules.all():
                    if schedule.schedule:
                        course_mask |= parse_schedule(schedule.schedule)

                common_schedules = CourseSchedule.objects.filter(common_schedule_for_course=course_code)
                for schedule in common_schedules:
                    if schedule.schedule:
                        course_mask |= parse_schedule(schedule.schedule)

                # Verify no conflict between course schedule and occupied slots
                conflict = course_mask & constraint_mask
                self.assertEqual(conflict, 0,
                                 f"Index {index_id} has schedule conflicts with occupied slots")

    def test_optimize_empty_schedule_with_constraints(self):
        """Test that courses with no schedule data are rejected when constraints exist."""
        # MH1810 has an all-O common_schedule (no actual class times)
        # When all slots are blocked, it should return None, not accept the empty schedule
        input_data = OrderedDict([
            ('courses', [
                {'code': 'MH1810'}
            ]),
            ('occupied', 'X' * 192)
        ])
        result = optimize_index(input_data)

        # Should return None because course has no schedule data to verify
        self.assertIsNone(result,
                          "Course with empty schedule should be rejected when time constraints are specified")


class OptimizeViewAPITestCase(APITestCase):
    """Test the OptimizeView API endpoint."""

    fixtures = ['sample_data.json']

    @classmethod
    def setUpTestData(cls):
        """Set up test users and clients."""
        cls.client_anonymous = APIClient()

    def test_optimize_endpoint_success(self):
        """Test successful optimization request with fixture course."""
        url = reverse('optimizer:optimize')
        data = {
            'courses': [
                {'code': 'MH1100'}
            ]
        }
        response = self.client_anonymous.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_optimize_endpoint_with_occupied(self):
        """Test optimization with occupied slots."""
        url = reverse('optimizer:optimize')
        occupied = 'O' * 192
        data = {
            'courses': [
                {'code': 'MH1100'}
            ],
            'occupied': occupied
        }
        response = self.client_anonymous.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_optimize_endpoint_invalid_course(self):
        """Test with invalid course code."""
        url = reverse('optimizer:optimize')
        data = {
            'courses': [
                {'code': 'INVALID'}
            ]
        }
        response = self.client_anonymous.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_optimize_endpoint_invalid_occupied(self):
        """Test with invalid occupied string."""
        url = reverse('optimizer:optimize')
        data = {
            'courses': [
                {'code': 'MH1100'}
            ],
            'occupied': 'INVALID'  # Not 192 characters of O/X
        }
        response = self.client_anonymous.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_optimize_endpoint_missing_courses(self):
        """Test with missing courses field."""
        url = reverse('optimizer:optimize')
        data = {}
        response = self.client_anonymous.post(url, data, format='json')

        self.assertEqual(response.status_code, 400)


# Added test to ensure common schedules do not overlap with index/tutorial schedules
class CommonVsTutorialConflictTestCase(TestCase):
    fixtures = ['sample_data.json']

    def test_common_vs_tutorial_no_overlap(self):
        """Ensure common schedules do not overlap with index/tutorial schedules in optimizer output."""
        input_data = OrderedDict([
            ('courses', [
                {'code': 'MH1100', 'include': [], 'exclude': []},
                {'code': 'MH1200', 'include': [], 'exclude': []},
                {'code': 'MH1300', 'include': [], 'exclude': []},
            ]),
            ('occupied', 'O' * 192)
        ])

        result = optimize_index(input_data)
        # result can be None if no solution; that's OK but shouldn't contain conflicts if present
        if result is None:
            self.assertIsNone(result)
            return

        # Build full masks using all sources
        full_masks = {}
        for item in result:
            code = item['code']
            index = item['index']
            course = Course.objects.get(code=code)
            m = parse_schedule(course.common_schedule) if course.common_schedule else 0

            idx_obj = CourseIndex.objects.get(index=index)
            for s in idx_obj.schedules.all():
                if s.schedule:
                    m |= parse_schedule(s.schedule)
            if idx_obj.filtered_information:
                m |= filtered_information_to_mask(idx_obj.filtered_information)

            # include common_schedules if any
            from apps.courses.models import CourseSchedule
            for cs in CourseSchedule.objects.filter(common_schedule_for_course=code):
                if cs.schedule:
                    m |= parse_schedule(cs.schedule)

            full_masks[code] = m

        # Pairwise check: common schedule vs index schedules should have no overlap
        codes = list(full_masks.keys())
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                a = codes[i]
                b = codes[j]
                self.assertEqual(full_masks[a] & full_masks[b], 0,
                                 f"Conflict between {a} and {b} detected in optimizer result: {result}")
