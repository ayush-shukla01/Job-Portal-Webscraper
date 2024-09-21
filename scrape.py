import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
import time
import re
import pandas as pd


def request_url():
    # Ask the user if they want to enter a URL
    user_choice = input("Do you want to enter a URL related to naukri.com? (Y/N): ").strip().upper()

    # If the user enters 'Y', prompt for the URL
    if user_choice == 'Y':
        url = input("Please enter the Naukri URL: ").strip()
    else:
        # Use default URL if user enters 'N' or anything else
        url = 'https://www.naukri.com/jobs-in-bangalore'

    # Return the final URL
    return url



# URL to start from
url =  request_url()
options = webdriver.ChromeOptions()
chrome_driver_path = 'chromedriver.exe'  # Set your correct path for the chromedriver

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
driver.get(url)
time.sleep(2)

# List to store job data
jobs_list = []
count = 1



def request_pages_input():
    # Request user input for the number of pages
    pages = int(input("Enter the number of pages you want to extract data from: "))

    # Display the number of pages entered
    print(f"You have chosen to extract data from {pages} page(s).")
    return pages
pages = request_pages_input()

i=1
# Function to extract job data from each job card
def extract_job_data(job_card,i):
    original_window = driver.current_window_handle
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView();", job_card)

    driver.execute_script("arguments[0].click();", job_card)

    driver.switch_to.window(driver.window_handles[-1])
    try:
        # Extract job title
        job_title = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "styles_jd-header-title__rZwM1"))
        ).text
    except Exception as e:
        print(f"An error occurred while extracting job title: {e}")
        job_title = None

    # Extract company name
    try:
        company_name = driver.find_element(By.CLASS_NAME, value="styles_jd-header-comp-name__MvqAI").text.split('\n')[0]
    except Exception as e:
        print(f"An error occurred while extracting company name: {e}")
        company_name = None

    # Extract experience required
    try:
        experience_required = driver.find_element(By.CLASS_NAME, "styles_jhc__exp__k_giM").find_element(By.TAG_NAME,
                                                                                                        "span").text
    except Exception as e:
        print(f"An error occurred while extracting experience: {e}")
        experience_required = None

    # Extract salary
    try:
        salary = driver.find_element(By.CLASS_NAME, "styles_jhc__salary__jdfEC").find_element(By.TAG_NAME, "span").text
    except Exception as e:
        print(f"An error occurred while extracting salary: {e}")
        salary = None

    # Extract job description and other details from the text
    try:
        section = driver.find_element(By.CLASS_NAME, 'styles_job-desc-container__txpYf')
        jd_div = driver.execute_script("return arguments[0].innerText;", section)
    except Exception as e:
        jd_div = ""
        print(f"An error occurred while extracting job description: {e}")

    # Extract required skillset
    try:
        skills_div = driver.find_element(By.CLASS_NAME, "styles_key-skill__GIPn_")
        required_skillset = [span.text for span in skills_div.find_elements(By.TAG_NAME, "span")]
    except Exception as e:
        required_skillset = []
        print(f"An error occurred while extracting skillset: {e}")

    # Extract job-related details using regex patterns
    patterns = {
        "Role": r"Role:\s*(.*)",
        "Industry Type": r"Industry Type:\s*(.*)",
        "Department": r"Department:\s*(.*)",
        "Employment Type": r"Employment Type:\s*(.*)",
        "Role Category": r"Role Category:\s*(.*)"
    }
    details_dict = {key: re.search(pattern, jd_div).group(1).strip() if re.search(pattern, jd_div) else None for
                    key, pattern in patterns.items()}

    # Extract education details using regex patterns
    edu_patterns = {
        "UG": r"UG:\s*(.*)",
        "PG": r"PG:\s*(.*)"
    }
    edu_dict = {key: re.search(pattern, jd_div).group(1).strip() if re.search(pattern, jd_div) else None for
                key, pattern in edu_patterns.items()}

    # Store job data
    data = {
        'Job Title': job_title,
        'Company Name': company_name,
        'Experience Required': experience_required,
        'Salary': salary,
        'Required Skillset': ', '.join(required_skillset),
        'Education Requirements': str(edu_dict),
        'Job Description': [jd_div],
        'URL': str(driver.current_url)
    }
    data.update(details_dict)

    # Append data to the jobs list
    jobs_list.append(data)
    print(f"finished extracting data for job role: {i}", job_title, " from the company:", company_name)
    driver.close()
    driver.switch_to.window(original_window)


# Function to move to the next page
def go_to_next_page():
    try:
        # Wait until at least two elements with the class 'styles_btn-secondary__2AsIP' are present
        buttons = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles_btn-secondary__2AsIP'))
        )

        # Check if there are at least two buttons found
        if len(buttons) < 2:
            print("Next button not found or there aren't enough buttons.")
            return False

        next_button = buttons[1]  # Select the second button (the 'Next' button)

        # Scroll the "Next" button into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(1)  # Allow time for the scroll to complete

        # Click the "Next" button
        next_button.click()
        print("Navigating to the next page.")
        return True

    except (TimeoutException, ElementClickInterceptedException) as e:
        print(f"Error while navigating to the next page: {e}")
        return False


# Iterate over the first 10 pages
for page in range(pages):
    print(f"Scraping page {page + 1}...")

    # Find job cards
    job_cards = WebDriverWait(driver, 3).until(
        EC.presence_of_all_elements_located((By.XPATH, './/a[contains(@class,"title")]'))
    )

    # Extract data from each job card (20 per page)
    for index in range(len(job_cards)):
        job_cards = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.XPATH, './/a[contains(@class,"title")]'))
        )  # Re-fetch in case DOM changes
        extract_job_data(job_cards[index],i)
        i= i+1

    # Go to the next page if it's not the last iteration
    if page < 9:
        if not go_to_next_page():
            break
    time.sleep(5)  # Wait for the next page to load

# Convert the jobs list to a DataFrame and save to CSV
Jobs_DF = pd.DataFrame(jobs_list)
Jobs_DF.to_csv("JD_template.csv", index=False)
print("Job data has been saved to JD_template.csv")

# Close the WebDriver
driver.quit()
