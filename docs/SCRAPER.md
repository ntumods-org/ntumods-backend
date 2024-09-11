# Scraper App

This is a documentation for the scraper app (`/apps/scraper`). The scraper app is used to scrape data from NTU website, and store it in the database.

There are 4 scrapers in the app:

- [Course Basic Scraper](#course-basic-scraper)
- [Course Details Scraper](#course-details-scraper)
- [Exam Scraper](#exam-scraper)
- [Program Scraper](#program-scraper)

Note that 'Course Basic Scraper' should be run before the other scrapers. Currently, all scrapers should be run manually by calling an API, accessible only by superusers.

When the data changes, the scrapers should be run again to update the database. The scrapers are capable of overwriting existing data without making duplicates, but it cannot delete data that is no longer present in the website.In the future, a CRON job can be set up to run the scrapers automatically at a certain time. It is still a work in progress.

The sections below briefly describe each scraper, where it gets data from, and what does it achieve. For detailed information on the scraping process, please refer to the files in `apps/scraper/utils`.

## Course Basic Scraper

This scraper gets data from [this page](https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1?acadsem=2024;1&staff_access=true&r_search_type=F&boption=Search&r_subj_code=) (please change the acadsem query parameter appropriately). It scrapes the course code, course title, academic units, and all available indexes along with its schedule information. The data is then processed and stored in Course, CourseIndex, and CoursePrefix tables. This scraper takes around 1 minute to complete.

## Course Details Scraper

The next scraper gets detailed information about each course, such as its description, prerequisites, not available remarks, not offered remarks, etc. The information has to be scraped from the individual course pages by making a POST request to `https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1`, passing in the following form data (please change the values appropriately):

```
{
    "acadsem": 2024_1,
    "r_subj_code": "MH1100",
    "boption": "Search",
    "acad": 2024,
    "semester": 1
}
```

This process is time-consuming and may take over 10 minutes to scrape all courses. In order to prevent timeouts, you can pass on the query parameter `start_index` and `end_index` to the API to scrape a subset of courses. For example, you can scrape courses from index 0 to 100 (exclusive), then from 100 to 200, and so on. The scraper will overwrite existing data if it is already present in the database. Reminder that this scraper should be run after the Course Basic Scraper.

## Exam Scraper

This scraper scrapes exam data and update each course's exam information. The exam data is gained by logging in via [this link](https://wis.ntu.edu.sg/webexe/owa/exam_timetable_und.main), and saving the HTML content at `apps/scraper/utils/scraping_files/exam_schedule.html`. Unfortunately due to the nature of the website, the exam HTML has to be updated manually in the repository. It would be great if we can find a way to update the exam data, without changing the HTML file in the repository manually. This scraper should be quick and takes only around 10 seconds to complete.

## Program Scraper

This scraper scrapes all the available programs from [this page](https://wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main) and stores in CourseProgram table. Then, for every program it calls another POST request to `https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1` (same as Course Details Scraper) but with `boption=CLoad` and `r_course_yr` set to the value attribute of the option tag in the program page, and fill the many to many relationship between Course and CourseProgram. This scraper also takes a few minutes to complete, especially the second part. In order to prevent timeouts, you can pass on the query parameter `start_index` and `end_index` to the API to scrape a subset of programs, similar to the Course Details Scraper.
