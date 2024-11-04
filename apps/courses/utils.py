import re
from apps.courses.models import Course, CoursePrerequisite


def getPrerequisites():
    '''
    Utility function to populate the CoursePrerequisite table with each course's prerequisites
    '''
    OPERATORS = {
        "&": "and",
        "|": "or"
    }
    all_course_codes = list(Course.objects.values_list('code', flat=True))
    for course in Course.objects.all():
        if course.prerequisite:
            def parse(tokens):
                '''
                Recursive helper function to parse course prerequisites
                '''
                result = {}
                prerequisites = []
                operator = None

                while tokens:
                    token = tokens.pop(0)

                    if token == '(':
                        # Start of expression, parse it recursively
                        nested = parse(tokens)
                        # Store parsed nested expression into prerequisites, ignore result if empty
                        if nested:
                            # Check if previous course is a corequisite
                            if "Corequisite" in nested and len(prerequisites) > 0:
                                prerequisites.append({"corequisite": prerequisites.pop(-1)})
                            else:
                                prerequisites.append(nested)
                    elif token == ')':
                        # End of expression, break out of recursive loop
                        break
                    elif token == '&' or token == '|':
                        # Token is an operator
                        operator = OPERATORS[token]
                    elif token == 'Corequisite':
                        # Previous course is a corequisite; remove parantheses to avoid treating it as expression
                        result[token] = ""
                        if tokens and tokens[0] == ")":
                            tokens.pop(0)
                        return result
                    else:
                        # Token is a word, check if its a valid course code and add to prerequisites
                        if token in all_course_codes:
                            prerequisites.append(token)
                
                if len(prerequisites) == 0:
                    # No prerequisites found, return empty result
                    pass
                elif len(prerequisites) == 1:
                    # Only one prerequisite found, return string result
                    result = prerequisites[0]
                else:
                    # Return prerequisite expression, e.g. {'or': ['SC1004', 'MH1812']}
                    result[operator] = prerequisites
                return result

            # Replace OR with | for tokenisation
            prerequisite_str = course.prerequisite.replace(" OR ", " | ")
            # Tokenise string on (, ), \, &, and words
            tokens = re.findall(r'\(|\)|\w+|\||&', prerequisite_str)
            parsed_prerequisites = parse(tokens)

            if parsed_prerequisites:
                # Create CoursePrerequisite object
                CoursePrerequisite.objects.create(
                    course=course,
                    child_nodes=parsed_prerequisites,
                )
                print(f"Created CoursePrerequisite object for {course.code}:\n  {parsed_prerequisites}")
