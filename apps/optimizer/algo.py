from collections import OrderedDict
import random

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


def solve_with_constraints(constraint_mask, wanted_courses: list[str], include_map=None, exclude_map=None, ignore_lecture_clashes=False, shuffle=False, limit=1):
    """
    Solves the course scheduling problem with given constraints.

    Args:
        constraint_mask: Bitmask representing blocked time slots (directly from OX string)
        wanted_courses: List of course codes to schedule
        include_map: Dict mapping course codes to lists of index IDs to include (if specified, only these indices are considered)
        exclude_map: Dict mapping course codes to lists of index IDs to exclude
        ignore_lecture_clashes: If True, ignore conflicts between lecture-type schedules
        shuffle: If True, randomize the order of indices to generate different schedules
        limit: Maximum number of solutions to return

    Returns:
        List of solutions, where each solution is a list of (course_code, index_id) tuples.
        Returns empty list if no solution exists.
    """
    include_map = include_map or {}
    exclude_map = exclude_map or {}
    course_data = {}
    # Store lecture masks separately if ignore_lecture_clashes is enabled
    lecture_masks = {} if ignore_lecture_clashes else None

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
        common_lecture_mask = 0
        for schedule in common_schedules:
            if schedule.schedule:
                sched_mask = parse_schedule(schedule.schedule)
                common_schedule_mask |= sched_mask
                # Track lecture schedules separately
                if ignore_lecture_clashes and 'LEC' in schedule.type.upper():
                    common_lecture_mask |= sched_mask

        course_data[course_code] = {}
        if ignore_lecture_clashes:
            lecture_masks[course_code] = {}

        for index in indexes:
            index_id = index.index

            # Apply include/exclude filters
            if course_code in include_map:
                # If include list is specified, only consider those indices
                if index_id not in include_map[course_code]:
                    continue
            if course_code in exclude_map:
                # Skip excluded indices
                if index_id in exclude_map[course_code]:
                    continue

            index_mask = common_mask | common_schedule_mask
            index_lecture_mask = common_lecture_mask if ignore_lecture_clashes else 0

            # Add schedules from CourseSchedule model
            for schedule in index.schedules.all():
                if schedule.schedule:
                    sched_mask = parse_schedule(schedule.schedule)
                    index_mask |= sched_mask
                    # Track lecture schedules separately
                    if ignore_lecture_clashes and 'LEC' in schedule.type.upper():
                        index_lecture_mask |= sched_mask

            # Add index-specific times from filtered_information
            if index.filtered_information:
                info_mask = filtered_information_to_mask(index.filtered_information)
                index_mask |= info_mask
                # Check if filtered_information contains lecture sessions
                if ignore_lecture_clashes and 'LEC' in index.filtered_information.upper():
                    index_lecture_mask |= info_mask

            course_data[course_code][index_id] = index_mask
            if ignore_lecture_clashes:
                lecture_masks[course_code][index_id] = index_lecture_mask

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
        
        # Shuffle indices if requested
        if shuffle:
            random.shuffle(valid_indices[c_id])

    # 4. Solver
    courses = list(valid_indices.keys())
    solutions = []

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
        # If ignoring lecture clashes, also track lecture-only masks
        full_lecture_masks = {} if ignore_lecture_clashes else None

        for course_code, index_id in assignment:
            try:
                course = Course.objects.get(code=course_code)
                common_masks[course_code] = parse_schedule(course.common_schedule) if course.common_schedule else 0
            except Course.DoesNotExist:
                common_masks[course_code] = 0

            # Build lecture mask if needed
            if ignore_lecture_clashes:
                lec_mask = 0
                # Common lecture schedules
                for cs in CourseSchedule.objects.filter(common_schedule_for_course=course_code):
                    if cs.schedule and 'LEC' in cs.type.upper():
                        lec_mask |= parse_schedule(cs.schedule)
                # Index-specific lecture schedules
                try:
                    idx_obj = CourseIndex.objects.get(index=index_id)
                    for s in idx_obj.schedules.all():
                        if s.schedule and 'LEC' in s.type.upper():
                            lec_mask |= parse_schedule(s.schedule)
                    # Check filtered_information for lectures
                    if idx_obj.filtered_information and 'LEC' in idx_obj.filtered_information.upper():
                        lec_mask |= filtered_information_to_mask(idx_obj.filtered_information)
                except CourseIndex.DoesNotExist:
                    pass
                full_lecture_masks[course_code] = lec_mask

        courses_list = list(full_masks.keys())

        # Check 1: Full mask vs full mask (standard conflict check)
        for i in range(len(courses_list)):
            for j in range(i + 1, len(courses_list)):
                ci = courses_list[i]
                cj = courses_list[j]

                if ignore_lecture_clashes:
                    # Calculate non-lecture portions
                    ci_non_lec = full_masks[ci] & ~full_lecture_masks[ci]
                    cj_non_lec = full_masks[cj] & ~full_lecture_masks[cj]
                    ci_lec = full_lecture_masks[ci]
                    cj_lec = full_lecture_masks[cj]

                    # Check conflicts: non-lec vs all, lec vs non-lec (but not lec vs lec)
                    conflict = (ci_non_lec & full_masks[cj]) | (cj_non_lec & full_masks[ci])
                    if conflict:
                        return False
                else:
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

                if ignore_lecture_clashes:
                    # Determine if common schedule is lecture
                    ci_common_lec = 0
                    try:
                        for cs in CourseSchedule.objects.filter(common_schedule_for_course=ci):
                            if cs.schedule and 'LEC' in cs.type.upper():
                                ci_common_lec |= parse_schedule(cs.schedule)
                    except:
                        pass
                    ci_common_non_lec = common_masks[ci] & ~ci_common_lec

                    cj_non_lec = full_masks[cj] & ~full_lecture_masks[cj]

                    # Check: ci common non-lec vs cj full, ci common lec vs cj non-lec
                    conflict = (ci_common_non_lec & full_masks[cj]) | (ci_common_lec & cj_non_lec)
                    if conflict:
                        return False
                else:
                    if common_masks[ci] & full_masks[cj]:
                        return False

        return True

    def backtrack(depth, current_mask, current_assignment):
        if len(solutions) >= limit:
            return

        if depth == len(courses):
            # perform final rigorous validation before accepting
            if _assignment_is_valid(current_assignment):
                solutions.append(current_assignment)
            return

        c_id = courses[depth]
        for idx_id in valid_indices[c_id]:
            if len(solutions) >= limit:
                return

            idx_mask = course_data[c_id][idx_id]

            # Calculate the conflict check mask
            if ignore_lecture_clashes:
                # Exclude lecture portions from both current and new masks for conflict checking
                idx_lecture_mask = lecture_masks[c_id][idx_id]
                idx_non_lecture_mask = idx_mask & ~idx_lecture_mask

                # Build current non-lecture mask from assignment
                current_lecture_mask = 0
                for assigned_course, assigned_idx in current_assignment:
                    current_lecture_mask |= lecture_masks[assigned_course][assigned_idx]
                current_non_lecture_mask = current_mask & ~current_lecture_mask

                # Check for conflicts:
                # 1. New non-lecture times vs all current times
                # 2. New lecture times vs current non-lecture times
                # (lecture-to-lecture conflicts are ignored)
                conflict = (idx_non_lecture_mask & current_mask) | (idx_lecture_mask & current_non_lecture_mask)
            else:
                # Normal conflict check - all schedules
                conflict = idx_mask & current_mask

            if conflict == 0:
                backtrack(depth + 1, current_mask | idx_mask, current_assignment + [(c_id, idx_id)])

    backtrack(0, constraint_mask, [])
    return solutions


def optimize_index(optimizer_input_data: OrderedDict):
    """
    Optimizes course index selection based on constraints.

    Args:
        optimizer_input_data: Dictionary with 'courses' and optional 'occupied' fields
            - courses: List of dicts with 'code', optional 'include', 'exclude'
            - occupied: 192-char string ('O' or 'X') representing blocked time slots
            - ignore_lecture_clashes: Boolean flag to ignore lecture conflicts
            - shuffle: Boolean flag to randomize the order of indices
            - limit: Maximum number of solutions to return

    Returns:
        List of solutions, where each solution is a list of dicts with 'code' and 'index' fields.
        Returns empty list if no solution found.
    """
    # Extract course codes
    wanted_courses = [course_data['code'] for course_data in optimizer_input_data['courses']]

    # Extract include/exclude maps
    include_map = {}
    exclude_map = {}
    for course_data in optimizer_input_data['courses']:
        code = course_data['code']
        if 'include' in course_data and course_data['include']:
            include_map[code] = course_data['include']
        if 'exclude' in course_data and course_data['exclude']:
            exclude_map[code] = course_data['exclude']

    # Convert occupied string directly to bitmask
    occupied = optimizer_input_data.get('occupied', '')
    constraint_mask = occupied_str_to_mask(occupied)

    # Get ignore_lecture_clashes flag
    ignore_lecture_clashes = optimizer_input_data.get('ignore_lecture_clashes', False)
    
    # Get shuffle flag
    shuffle = optimizer_input_data.get('shuffle', False)

    # Get limit
    limit = optimizer_input_data.get('limit', 1)

    # Call the solver
    results = solve_with_constraints(
        constraint_mask=constraint_mask,
        wanted_courses=wanted_courses,
        include_map=include_map,
        exclude_map=exclude_map,
        ignore_lecture_clashes=ignore_lecture_clashes,
        shuffle=shuffle,
        limit=limit
    )

    # Format the result - ensure index_id is a string
    formatted_results = []
    for result in results:
        formatted_results.append([{"code": course_code, "index": str(index_id)} for course_code, index_id in result])
    
    return formatted_results
