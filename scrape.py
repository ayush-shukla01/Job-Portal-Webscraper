
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import os
import re
import time
import pandas as pd

# def scrape_website(url):
url = 'https://www.naukri.com/jobs-in-bangalore'
options = webdriver.ChromeOptions()
chrome_driver_path = 'chromedriver.exe'

driver = webdriver.Chrome(service= Service(chrome_driver_path),options= options)
# xpath - //div[contains(@class,"lay-2 sjw__tuple")]

driver.get(url)
time.sleep(2)
job_cards = driver.find_elements(by='xpath',value='.//a[contains(@class,"title")]')
# print("job_cards",type(job_cards),job_cards)
jobs_list = []
count = 1

for index in range(len(job_cards)):

    job_cards = driver.find_elements(by='xpath', value='.//a[contains(@class,"title")]')
    print("card_index",index+1 )
    job_card = job_cards[index]  # get the current job card
    driver.execute_script("arguments[0].scrollIntoView();", job_card)
    time.sleep(2)

    # Handle potential overlay or pop-up
    try:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "styles_privacyPolicy__yEgp3"))
        )
        close_button.click()
    except Exception as e:
        print(f"No overlay to close: {e}")

    # Try to click using JavaScript if normal click is intercepted
    driver.execute_script("arguments[0].click();", job_card)

    # print(count)
    count = count+1
    original_window = driver.current_window_handle
    driver.switch_to.window(driver.window_handles[-1])
    try:
        # Extract job title
        job_title = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "styles_jd-header-title__rZwM1"))).text
        # print(job_title)
    except Exception as e:
        print(f"An error occurred: {e}")

    # Extract company name
    tests = driver.find_element(By.CLASS_NAME, value="styles_jd-header-comp-name__MvqAI").text
    company_name = tests.split('\n')[0]
    # print(company_name)

    # Extract required experience
    try:
        experience_div = driver.find_element(By.CLASS_NAME, "styles_jhc__exp__k_giM")
        experience_required = experience_div.find_element(By.TAG_NAME, "span").text

    except Exception as e:
        experience_required = None
        print(f"An error occurred: {e}")

    # Extract salary
    try:
        salary_div = driver.find_element(By.CLASS_NAME, "styles_jhc__salary__jdfEC")
        salary = salary_div.find_element(By.TAG_NAME, "span").text

    except Exception as e:
        salary = None
        print(f"An error occurred: {e}")

    # Extract job posting stats (openings, applicants, etc.)
    try:
        stats_dict = {}
        stats_div = driver.find_element(By.CLASS_NAME, "styles_jhc__jd-stats__KrId0")
        stat_elements = stats_div.find_elements(By.CLASS_NAME, "styles_jhc__stat__PgY67")
        for stat in stat_elements:
            label_text = stat.find_element(By.TAG_NAME, "label").text
            span_text = stat.find_element(By.TAG_NAME, "span").text
            stats_dict[label_text.strip(':')] = span_text
        # print(stats_dict)
    except Exception as e:
        stats_dict = {}
        print(f"An error occurred: {e}")

    # Extract other details (location, job type, etc.)
    # try:
    #     details_dict = {}
    #     details_div = driver.find_element(By.CLASS_NAME, "styles_other-details__oEN4O")
    #     detail_elements = details_div.find_elements(By.CLASS_NAME, "styles_details__Y424J")
    #     for detail in detail_elements:
    #         label_text = detail.find_element(By.TAG_NAME, "label").text
    #         try:
    #             span_text = detail.find_element(By.TAG_NAME, "a").text
    #         except:
    #             span_text = detail.find_element(By.TAG_NAME, "span").text
    #         details_dict[label_text.strip(':')] = span_text
    #     # print(details_dict)
    # except Exception as e:
    #     details_dict = {}
    #     print(f"An error occurred: {e}")

    # Extract education requirement details (edu_dict will now be stored as a column)
    # try:
    #     edu_dict = {}
    #     education_div = driver.find_element(By.CLASS_NAME, "styles_education__KXFkO")
    #     edu_elements = education_div.find_elements(By.CLASS_NAME, "styles_details__Y424J")
    #     for edu in edu_elements:
    #         label_text = edu.find_element(By.TAG_NAME, "label").text
    #         span_text = edu.find_element(By.TAG_NAME, "span").text
    #         edu_dict[label_text.strip(':')] = span_text
        # print(edu_dict)
    # except Exception as e:
    #     edu_dict = {}
    #     print(f"An error occurred: {e}")

    # Extract required skillset
    required_skillset = []
    try:
        skills_div = driver.find_element(By.CLASS_NAME, "styles_key-skill__GIPn_")
        span_elements = skills_div.find_elements(By.TAG_NAME, "span")
        for span in span_elements:
            required_skillset.append(span.text)
    except Exception as e:
        required_skillset = []
        print(f"An error occurred: {e}")

    # extract the complete Job description
    try:
        section = driver.find_element(By.CLASS_NAME, 'styles_job-desc-container__txpYf')

        # Extract the text from the section
        jd_div = driver.execute_script("return arguments[0].innerText;", section)
        # print(jd_div)
    except Exception as e:
        jd_div = []
        print(f"An error occurred: {e}")

    patterns = {
        "Role": r"Role:\s*(.*)",
        "Industry Type": r"Industry Type:\s*(.*)",
        "Department": r"Department:\s*(.*)",
        "Employment Type": r"Employment Type:\s*(.*)",
        "Role Category": r"Role Category:\s*(.*)"
    }

    # Dictionary to store the extracted details
    details_dict = {}

    # Extract the required information and store it in details_dict
    for key, pattern in patterns.items():
        match = re.search(pattern, jd_div)
        if match:
            details_dict[key] = match.group(1).strip()

    edu_patterns = {
        "UG": r"UG:\s*(.*)",
        "PG": r"PG:\s*(.*)"
    }

    # Dictionary to store the extracted education details
    edu_dict = {}

    # Extract the required education information and store it in edu_dict
    for key, pattern in edu_patterns.items():
        match = re.search(pattern, jd_div)
        if match:
            edu_dict[key] = match.group(1).strip()

    # Close the browser

    # Prepare the data for the DataFrame
    data = {
        'URL':str(driver.current_url),
        'Job Title': job_title,
        'Company Name': company_name,
        'Experience Required': experience_required,
        'Salary': salary,
        'Required Skillset': [', '.join(required_skillset)],  # Join list into a single string
        'Education Requirements': [str(edu_dict)],
        'Job Description': [jd_div],  # Convert edu_dict to string and store as a column
    }

    # Combine all extracted dictionaries (stats_dict, details_dict) into the data dictionary
    data.update(stats_dict)
    data.update(details_dict)

    jobs_list.append(data)

    print("finished extracting data for job role: ",job_title," from the company:",company_name)

    driver.close()
    driver.switch_to.window(original_window)
    # job_cards = driver.find_elements(by='xpath', value='.//a[contains(@class,"title")]')

Jobs_DF = pd.DataFrame(jobs_list)
try:
    JD_template = Jobs_DF.to_csv("JD_template.csv")
except:
    JD_template = Jobs_DF.to_csv("JD_template.csv")

time.sleep(5)


    # return html

