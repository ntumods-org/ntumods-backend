from bs4 import BeautifulSoup
from django.db.utils import IntegrityError
from typing import Dict, List
import re
import requests

from apps.courses.models import Course, CourseProgram


def get_soup_from_url() -> BeautifulSoup:
    URL = 'https://wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main'
    with requests.get(URL) as fp:
        soup = BeautifulSoup(fp.content, 'html.parser')
        return soup

def get_programs_data(soup: BeautifulSoup) -> List[Dict[str, str]]:
    select_element = soup.find('select', {'name': 'r_course_yr'})
    html_str = str(select_element)
    programs_raw_data = html_str.split('option')

    programs_data = []
    pattern = r'value="([^"]+)">(.*?)(?:\n|<)'
    for raw_str in programs_raw_data:
        match = re.match(pattern, raw_str.strip())
        if match:
            value = match.group(1)
            name = match.group(2)
            year = None
            try:
                year = int(value.split(';')[2])
            except ValueError:
                pass
            programs_data.append({
                'name': name,
                'value': value,
                'year': year,
            })
    
    return programs_data

def save_programs_data(programs_data: List[Dict[str, str]]):
    for program in programs_data:
        try:
            CourseProgram.objects.create(
                name=program['name'],
                value=program['value'],
                year=program['year'],
            )
        except IntegrityError:
            pass

def save_single_program_courses(soup: BeautifulSoup, program: CourseProgram):
    tables = soup.find_all('table')
    for table in tables:
        first_tr = table.find('tr')
        if first_tr:
            first_td = first_tr.find('td')
            if first_td:
                code = first_td.get_text(strip=True)
                course_code_instance = Course.objects.filter(code=code).first()
                if not course_code_instance:
                    print(f'Course with code {code} not found')
                    continue
                program.courses.add(course_code_instance)
                programs_list = course_code_instance.program_list.split(', ') \
                    if course_code_instance.program_list else []
                programs_list.append(program.name)
                unique_programs_list = list(set(programs_list))
                course_code_instance.program_list = ', '.join(unique_programs_list)
                course_code_instance.save()

def save_programs_courses():
    ENDPOINT = 'https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1'
    FORMDATA_ACADSEM = '2024_1'
    FORMDATA_ACAD = '2024'
    FORMDATA_SEMESTER = '1'
    
    programs = CourseProgram.objects.all()
    for program in programs:
        try:
            print('program: ', program.name)
            form_data = {
                'acadsem': FORMDATA_ACADSEM,
                'r_course_yr': program.value,
                'r_subj_code': '',
                'boption': 'CLoad',
                'acad': FORMDATA_ACAD,
                'semester': FORMDATA_SEMESTER,
            }
            response = requests.post(
                ENDPOINT,
                data=form_data
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                save_single_program_courses(soup, program)
            else:
                raise Exception(f'Failed to get response, status code: {response.status_code}')
        except Exception as e:
            print(e)
            print(f'Failed to scrape program {program.name}')
            continue

def perform_program_scraping():
    try:
        soup = get_soup_from_url()
        programs_data = get_programs_data(soup)
        save_programs_data(programs_data)
        save_programs_courses()
    except Exception as e:
        print(f'Program Scraper Error: {e}')
