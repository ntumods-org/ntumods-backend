from bs4 import BeautifulSoup
import requests

from apps.courses.models import Course


'''
Given a soup object and Course instance, parse details from soup and save to Course instance:
description, prerequisite, mutually_exclusive, not_available, not_available_all, offered_as_ue, offered_as_bde
'''
def save_course_detail(soup: BeautifulSoup, course: Course):
    # get description which is the last td in the table
    description_td = soup.find_all('td')[-2]
    description = description_td.text.strip()
    course.description = description

    # utility function to get the text in the 2nd td of a tr in which the 1st td of a tr contains search_text
    def get_tr_text(soup, search_text):
        trs = soup.find_all('tr')
        for tr in trs:
            td = tr.find('td')
            if td and search_text in td.get_text():
                tds = tr.find_all('td')
                if len(tds) > 1:
                    return tds[1].get_text(strip=True)
        return None

    # extract information
    prerequisite = get_tr_text(soup, 'Prerequisite:')
    course.prerequisite = prerequisite
    mutually_exclusive = get_tr_text(soup, 'Mutually exclusive with:')
    course.mutually_exclusive = mutually_exclusive
    not_available = get_tr_text(soup, 'Not available to Programme:')
    course.not_available = not_available
    not_available_all = get_tr_text(soup, 'Not available to all Programme with:')
    course.not_available_all = not_available_all
    grade_type = get_tr_text(soup, 'Grade Type:')
    course.grade_type = grade_type
    not_available_as_core_to = get_tr_text(soup, 'Not available as Core to Programme:')
    course.not_offered_as_core_to = not_available_as_core_to
    not_available_as_pe_to = get_tr_text(soup, 'Not available as PE to Programme:')
    course.not_offered_as_pe_to = not_available_as_pe_to
    not_available_as_bde_ue_to = get_tr_text(soup, 'Not available as BDE/UE to Programme:')
    course.not_offered_as_bde_ue_to = not_available_as_bde_ue_to
    
    # check if the course is not offered as UE or BDE, otherwise it's True by default
    tds = soup.find_all('td')
    for td in tds:
        if 'Not offered as Unrestricted Elective' in td.get_text():
            course.offered_as_ue = False
        if 'Not offered as Broadening and Deepening Elective' in td.get_text():
            course.offered_as_bde = False
            
    # get the department that maintain / offer this course
    second_tr = soup.find_all('tr')[1]
    last_td = second_tr.find_all('td')[-1]
    last_td_text = last_td.get_text(strip=True)
    course.department_maintaining = last_td_text
    
    # save the changes
    course.save()

'''
Main function to scrape course details.
Must be called only after course scraping is completed.
For all courses from start_index to end_index:
- Send a POST request to NTU API which return the html of the course detail page
- Call save_course_detail to parse and save the details to the Course instance
'''
def perform_course_detail_scraping(start_index: int=0, end_index: int=9999):
    ENDPOINT = 'https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1'
    FORMDATA_ACADSEM = '2024_1'
    FORMDATA_ACAD = '2024'
    FORMDATA_SEMESTER = '1'
    
    courses = Course.objects.all()
    for course in courses[start_index:end_index]:
        try:
            form_data = {
                'acadsem': FORMDATA_ACADSEM,
                'r_subj_code': course.code,
                'boption': 'Search',
                'acad': FORMDATA_ACAD,
                'semester': FORMDATA_SEMESTER,
            }
            response = requests.post(
                ENDPOINT,
                data=form_data
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                save_course_detail(soup, course)
            else:
                raise Exception(f'Failed to get response, status code: {response.status_code}')
        except Exception as e:
            print(e)
            print(f'Failed to scrape {course.code}')
            continue
