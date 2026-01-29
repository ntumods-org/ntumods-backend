from collections import OrderedDict

from apps.courses.models import Course, CourseIndex, CourseSchedule


def parse_schedule(schedule_str):
    mask = 0
    for i, char in enumerate(schedule_str):
        if char == 'X': mask |= (1 << i)
    return mask


def occupied_str_to_mask(occupied_str):
    """
    Converts a 192-character 'OX' string directly to a bitmask.
    occupied_str: 192 chars (6 days * 32 slots), where 'X' means blocked.
    Returns: Integer bitmask where each bit represents a blocked slot.
    """
    if not occupied_str:
        return 0

    mask = 0
    for i, char in enumerate(occupied_str):
        if char == 'X':
            mask |= (1 << i)
    return mask


def time_to_slot_index(time_str):
    """
    Convert time string like '0930' to slot index (0-31, starting from 8am).
    8:00 = slot 0, 8:30 = slot 1, 9:00 = slot 2, etc.
    """
    hour = int(time_str[:2])
    minute = int(time_str[2:4])
    slot = (hour - 8) * 2 + (1 if minute >= 30 else 0)
    return slot


def filtered_information_to_mask(filtered_info_str):
    """
    Convert filtered_information string to schedule mask.
    Format: type^group^day^time^venue^remark (semicolon-separated for multiple sessions)
    Example: TUT^T1^MON^0930-1020^SPMS-TR+4^Teaching Wk2-13
    Returns: Integer bitmask representing the scheduled time slots.
    """
    if not filtered_info_str:
        return 0

    day_map = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5}
    mask = 0

    # Split by semicolon for multiple sessions
    sessions = filtered_info_str.split(';')
    for session in sessions:
        if not session:
            continue

        parts = session.split('^')
        if len(parts) < 4:
            continue

        day = parts[2].strip()
        time_range = parts[3].strip()

        if day not in day_map:
            continue

        # Parse time range (e.g., "0930-1020")
        if '-' not in time_range:
            continue

        start_time, end_time = time_range.split('-')
        start_slot = time_to_slot_index(start_time)
        end_slot = time_to_slot_index(end_time)

        # Set bits for all slots in the range (inclusive of end_slot)
        day_offset = day_map[day] * 32
        for slot in range(start_slot, end_slot + 1):
            if 0 <= slot < 32:
                mask |= (1 << (day_offset + slot))

    return mask


def solve_with_constraints(constraint_mask, wanted_courses: list[str]):
    """
    Solves the course scheduling problem with given constraints.

    Args:
        constraint_mask: Bitmask representing blocked time slots (directly from OX string)
        wanted_courses: List of course codes to schedule

    Returns:
        List of (course_code, index_id) tuples representing the solution, or None if no solution exists
    """
    course_data = {}

    for course_code in wanted_courses:
        try:
            course = Course.objects.get(code=course_code)
        except Course.DoesNotExist:
            continue

        # Common schedule for the course (applies to all indices)
        common_mask = parse_schedule(course.common_schedule) if course.common_schedule else 0

        # Fetch indices with their schedules
        indexes = CourseIndex.objects.filter(course_code=course_code).prefetch_related('schedules')
        if not indexes.exists():
            continue

        # Common schedules stored in CourseSchedule (optional)
        common_schedules = CourseSchedule.objects.filter(common_schedule_for_course=course_code)
        common_schedule_mask = 0
        for schedule in common_schedules:
            if schedule.schedule:
                common_schedule_mask |= parse_schedule(schedule.schedule)

        course_data[course_code] = {}

        for index in indexes:
            index_id = index.index
            index_mask = common_mask | common_schedule_mask

            # Add schedules from CourseSchedule model
            for schedule in index.schedules.all():
                if schedule.schedule:
                    index_mask |= parse_schedule(schedule.schedule)

            # Add index-specific times from filtered_information
            if index.filtered_information:
                index_mask |= filtered_information_to_mask(index.filtered_information)

            course_data[course_code][index_id] = index_mask

    # 1. Calculate Fixed Masks (Sessions common to all indices of a course)
    fixed_masks = {}
    for c_id, indices in course_data.items():
        if not indices:
            continue
        f_mask = list(indices.values())[0]
        for mask in indices.values():
            f_mask &= mask
        fixed_masks[c_id] = f_mask

    # 2. Constraint Mask is passed as parameter
    # (Skip create_constraint_mask - work directly with the bitmask)

    # 3. Build valid_indices - just filter out indices with no schedule when constraints exist
    # Don't try to be clever with fixed_masks since it misses index-specific conflicts
    valid_indices = {}
    for c_id in course_data:
        valid_indices[c_id] = []
        for idx_id, mask in course_data[c_id].items():
            # Reject indices with no schedule data when constraints are specified
            if constraint_mask != 0 and mask == 0:
                continue
            # Check against user constraints only (not other courses - backtracker handles that)
            if (mask & constraint_mask) == 0:
                valid_indices[c_id].append(idx_id)

    # 4. Solver
    courses = list(valid_indices.keys())

    def _build_full_mask_for_assignment(assignment):
        """Given an assignment list of (course_code, index_id), return dict of full masks for each course."""
        full_masks = {}
        for course_code, index_id in assignment:
            try:
                course = Course.objects.get(code=course_code)
            except Course.DoesNotExist:
                full_masks[course_code] = 0
                continue
            m = parse_schedule(course.common_schedule) if course.common_schedule else 0
            # include CourseSchedule entries common to course
            for cs in CourseSchedule.objects.filter(common_schedule_for_course=course_code):
                if cs.schedule:
                    m |= parse_schedule(cs.schedule)
            # include index-specific schedules
            try:
                idx_obj = CourseIndex.objects.get(index=index_id)
            except CourseIndex.DoesNotExist:
                full_masks[course_code] = m
                continue
            for s in idx_obj.schedules.all():
                if s.schedule:
                    m |= parse_schedule(s.schedule)
            # include filtered_information
            if idx_obj.filtered_information:
                m |= filtered_information_to_mask(idx_obj.filtered_information)
            full_masks[course_code] = m
        return full_masks

    def _assignment_is_valid(assignment):
        """Verify that the assignment has no pairwise conflicts (including commons vs index-specific)."""
        full_masks = _build_full_mask_for_assignment(assignment)

        # Also need common-only masks for each course
        common_masks = {}
        for course_code, index_id in assignment:
            try:
                course = Course.objects.get(code=course_code)
                common_masks[course_code] = parse_schedule(course.common_schedule) if course.common_schedule else 0
            except Course.DoesNotExist:
                common_masks[course_code] = 0

        courses_list = list(full_masks.keys())

        # Check 1: Full mask vs full mask (standard conflict check)
        for i in range(len(courses_list)):
            for j in range(i + 1, len(courses_list)):
                ci = courses_list[i]
                cj = courses_list[j]
                if full_masks[ci] & full_masks[cj]:
                    return False

        # Check 2: Each course's common schedule vs other courses' full masks
        # This catches cases where a common schedule conflicts with another course's index-specific times
        for i in range(len(courses_list)):
            for j in range(len(courses_list)):
                if i == j:
                    continue
                ci = courses_list[i]
                cj = courses_list[j]
                if common_masks[ci] & full_masks[cj]:
                    return False

        return True

    def backtrack(depth, current_mask, current_assignment):
        if depth == len(courses):
            # perform final rigorous validation before accepting
            if _assignment_is_valid(current_assignment):
                return current_assignment
            return None

        c_id = courses[depth]
        for idx_id in valid_indices[c_id]:
            idx_mask = course_data[c_id][idx_id]
            if (idx_mask & current_mask) == 0:
                res = backtrack(depth + 1, current_mask | idx_mask, current_assignment + [(c_id, idx_id)])
                if res:
                    return res
        return None

    return backtrack(0, constraint_mask, [])


def optimize_index(optimizer_input_data: OrderedDict):
    """
    Optimizes course index selection based on constraints.

    Args:
        optimizer_input_data: Dictionary with 'courses' and optional 'occupied' fields
            - courses: List of dicts with 'code', optional 'include', 'exclude'
            - occupied: 192-char string ('O' or 'X') representing blocked time slots

    Returns:
        List of dicts with 'code' and 'index' fields, or None if no solution found
    """
    # Extract course codes
    wanted_courses = [course_data['code'] for course_data in optimizer_input_data['courses']]

    # Convert occupied string directly to bitmask
    occupied = optimizer_input_data.get('occupied', '')
    constraint_mask = occupied_str_to_mask(occupied)

    # Call the solver
    result = solve_with_constraints(
        constraint_mask=constraint_mask,
        wanted_courses=wanted_courses
    )

    # Return None if no solution found
    if result is None:
        return None

    # Format the result - ensure index_id is a string
    return [{"code": course_code, "index": str(index_id)} for course_code, index_id in result]
