'''
Important note!!!

Currently, exam schedule html has to be saved manually from NTU website.
Save the html as `exam_schedule.html` in `modsoptimizer/utils/scraping_files/` folder.
Accessing the page directly is not possible due to the need of entering NTU credentials.
This is quite problematic as one has to update the html file manually to the repo,
in order to update the exam schedule in the database.
Looking for a better solution to automate this process!
'''

from bs4 import BeautifulSoup
from datetime import datetime as dt
from typing import Dict, List
import os

from apps.courses.models import Course


'''
Get HTML content from file_path and return a BeautifulSoup object
'''
def get_soup_from_html_file(file_path: str) -> BeautifulSoup:
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return BeautifulSoup(html_content, "lxml")

'''
Takes as input a BeautifulSoup object and returns a list of dictionaries containing:
date, day, time, course_code, course_title, duration
'''
def get_raw_data(soup: BeautifulSoup) -> List[Dict[str, str]]:
    raw_data = []
    exam_table = soup.find_all('table')[1] # exam schedule is the 2nd table
    rows = exam_table.find_all('tr')[2:] # data starts from 3rd row
    for row in rows:
        cells = row.find_all('td')
        if not cells: break
        raw_data.append({
            'date': cells[0].text.strip(),
            'day': cells[1].text.strip(),
            'time': cells[2].text.strip(),
            'course_code': cells[3].text.strip(),
            'course_title': cells[4].text.strip(),
            'duration': cells[5].text.strip(),
        })
    return raw_data

'''
Takes as input raw data from get_raw_data and returns a list of dictionaries containing:
course_code, exam_schedule_str (both processed data)
Refer to courses/models.py for the format of exam_schedule_str
'''
def process_data(raw_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    data = []
    for exam in raw_data:
        # extract date in DDMMYY format for first 6 characters
        date = exam['date']
        date_object = dt.strptime(date, "%d %B %Y")
        date_str = date_object.strftime("%Y-%m-%d")

        # extract exam time, 'X' for occupied, 'O' for unoccupied
        # assume that exam can only start at '00' minute or '30' minute
        exam_time_list = ['O'] * 32 # 8am to 12am, 16 hours in total, every 30 mins interval
        hour, am_pm = exam['time'].split(' ')
        hour_start, min_start = map(int, hour.split('.'))
        duration_list = exam['duration'].split(' ')
        duration_hour = int(duration_list[0])
        duration_min = int(duration_list[2]) if len(duration_list) > 2 and duration_list[2] != '' else 0

        start_index = (hour_start - 8) * 2 + (1 if min_start == '30' else 0) \
            if am_pm == 'am' else \
            hour_start * 2 + (1 if min_start == '30' else 0) + 8
        end_index = start_index + duration_hour * 2 + \
            (2 if duration_min > 30 else 1 if duration_min != 0 else 0)
        exam_time_list[start_index:end_index] = ['X'] * (end_index - start_index)
        exam_time_str = ''.join(exam_time_list)

        # assume duration can only be x hour, 0/15/30/45 min, where x is positive integer
        # note: currently per 10/12/2023 for AY2324 Sem 2, only found 0/30 min duration,
        # but previously on AY2324 Sem 1, found with 15/45 min duration, please check again
        hour_start = hour_start + 12 if am_pm == 'pm' else hour_start
        min_end = min_start + duration_min
        hour_end = hour_start + duration_hour
        if min_end >= 60:
            hour_end += 1
            min_end -= 60
        time_str = f'{hour_start:02d}:{min_start:02d}-{hour_end:02d}:{min_end:02d}'

        data.append({
            'course_code': exam['course_code'],
            'exam_schedule_str': date_str + time_str + exam_time_str,
        })
    return data

'''
Takes as input processed data from process_data and simply save the exam schedule to Course instance
'''
def save_exam_schedule(data: List[Dict]) -> None:
    for exam_data in data:
        try:
            course = Course.objects.get(code=exam_data['course_code'])
            course.exam_schedule = exam_data['exam_schedule_str']
            course.save()
        except Course.DoesNotExist:
            print(f'Course code {exam_data["course_code"]} does not exist')

'''
Main function to perform exam schedule scraping.
Must be called only after course scraping is completed.
Perform the following steps in order:
- `get_soup_from_html_file`: get BeautifulSoup object from html file saved in FILE_PATH
- `get_raw_data`: get raw data from BeautifulSoup object
- `process_data`: process raw data to get processed data
- `save_exam_schedule`: save processed data to the database
'''
def perform_exam_schedule_scraping():
    try:
        FILE_PATH = os.path.join('apps', 'scraper', 'utils', 'scraping_files', 'exam_schedule.html')
        soup = get_soup_from_html_file(FILE_PATH)
        raw_data = get_raw_data(soup)
        data = process_data(raw_data)
        save_exam_schedule(data)
    except Exception as e:
        print(f'Exam Schedule Scraper Error: {e}')
