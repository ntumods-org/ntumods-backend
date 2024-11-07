import re
from apps.courses.models import Course, CoursePrerequisite, PrerequisiteGraph


def getPrerequisites():
    '''
    Utility function to populate the CoursePrerequisite table with each course's prerequisites
    '''
    OPERATORS = {
        "&": "and",
        "|": "or"
    }
    all_course_codes = list(Course.objects.values_list('code', flat=True))
    all_course_codes.extend(["SC1003", "SC1004", "SC2000", "SC2001", "SC2002"]) # add this line for testing with sample_data.json
    
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
                
def dfsPrerequisites(course):
    '''
    Depth-first search to find all prerequisites for a given course
    '''
    
    # Helper function to get children of a course
    # currently only return list of Course objects without the relationship (e.g. 'or', 'and')
    def getChildren(prerequisites):
        listOfChildren = []
        if (isinstance(prerequisites, str)): # only one prerequisite e.g. 'MH1811' -> 'MH1810'
            child = Course.objects.get(code=prerequisites)
            listOfChildren.append(child)
        elif (isinstance(prerequisites, dict)): # have more than one prerequisites
            for key, value in prerequisites.items():
                # key is 'or' or 'and' or 'corequisite' or ...
                # val is list of prerequisites
                for val in value:
                    child = None
                    if (isinstance(val, str)):
                        child = Course.objects.filter(code=val).first()
                        if child != None:
                            listOfChildren.append(child)
                    elif (isinstance(val, dict)):
                        child = getChildren(val) # recursive call
                        for c in child:
                            listOfChildren.append(c)
                            
        return listOfChildren
    
    def dfs(node, graph):
        courseAndPrerequisites = CoursePrerequisite.objects.filter(course=node).first()
        graph.append({"course": node.code, "prerequisites": courseAndPrerequisites.child_nodes if courseAndPrerequisites != None else None})
        
        if courseAndPrerequisites != None:
            prerequisites = courseAndPrerequisites.child_nodes
            
            if prerequisites != None:
                children = getChildren(prerequisites)
                for child in children:
                    dfs(child, graph)
    
    graph = []
    dfs(course, graph)
    
    PrerequisiteGraph.objects.create(
        course=course, 
        prerequisite_graph=graph
    )

def makePrerequisiteGraph():
    '''
    Utility function to create a graph of prerequisites for each course
    '''
    for course in Course.objects.all():
        dfsPrerequisites(course)