import argparse
import os
import time
from datetime import datetime

import openpyxl
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# Initialize the Excel workbook and sheet
def initialize_excel():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Queries and Links"
    sheet.append(["Question Number", "Query", "Link"])  # Add headers
    return workbook, sheet


# Get the current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# Initialize the Chrome driver with options
def initialize_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument(
        "--window-size=1080x1920"
    )  # Set window size to ensure full-page screenshot
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )


# Take a screenshot of the first link for a given question number
def take_screenshot(driver, question_number, timestamp, png_output_dir):
    print("--------- START -----------")
    print(f"-- Starting process for question number {question_number}...")

    try:
        print("Opening Google...")
        driver.get("https://www.google.com")
        time.sleep(2)
        # Handle the cookie consent pop-up
        try:
            print("Checking for cookie pop-up")
            WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="W0wltc"]/div'))
            ).click()
            print("Bypassed popup")
        except (TimeoutException, NoSuchElementException):
            print("Cookie pop-up not found or not clickable")

        # Find the search box and enter the query
        search_box = driver.find_element(By.NAME, "q")
        query = f'google cloud "Exam Professional Machine Learning Engineer topic 1 question {question_number}"'
        print(f"Entering search query: {query}")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Click on the first link
        print("Clicking on the first link...")
        try:
            first_link = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//h3[@class="LC20lb MBeuO DKV0Md"]')
                )
            )
            first_link.click()
        except Exception as e:
            try:
                print(f"Error clicking on the first link: {e}")
                print("Clicking on the alternative discussion link...")
                a_element = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".discussion-link"))
                )
                a_element.click()
                print("Clicked on the <a> element.")
            except Exception as e:
                print(f"Error clicking on the alternative link: {e}")
        # Get the current URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}")

        # Handle the "Show Suggested Answer" button
        try:
            print("Clicking on the 'Show Suggested Answer' button...")
            show_answer_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//a[@class="btn btn-primary reveal-solution" and text()="Show Suggested Answer"]',
                    )
                )
            )
            show_answer_button.click()
            print("Clicked on the 'Show Suggested Answer' button.")
        except Exception as e:
            try:
                print(f"Error clicking on the first link:")  # {e}")
                print("Clicking on the alternative discussion link...")
                discussion_link_text = f"Exam Professional Machine Learning Engineer topic 1 question {question_number} discussion"
                discussion_link = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f'//a[@class="discussion-link" and contains(normalize-space(), "{discussion_link_text}")]',
                        )
                    )
                )
                discussion_link.click()

                print("Clicked on the alternative link.")
            except Exception as e:
                print(f"Error clicking on the alternative link: {e}")
        # Take a screenshot with timestamp
        screenshot_filename = f"screenshot_question_{question_number}_{timestamp}.png"
        screenshot_path = os.path.join(png_output_dir, screenshot_filename)
        print(f"Taking screenshot and saving to {screenshot_path}...")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        print("------- END ---------")

        return query, current_url, screenshot_filename

    except Exception as e:
        print(
            f"An error occurred during the process for question number {question_number}: {e}"
        )
        return None, None, None


# Merge PNG files into a PDF
def merge_png_to_pdf(png_files, pdf_filename):
    images = [Image.open(png) for png in png_files]
    images[0].save(pdf_filename, save_all=True, append_images=images[1:])
    print(f"PDF file saved as '{pdf_filename}'")


# Main function
def main(start_question, end_question):
    # Initialize Excel
    workbook, sheet = initialize_excel()

    # Get the current timestamp
    timestamp = get_timestamp()

    # Create output directory with question range and timestamp
    output_dir = os.path.join("./outputs", f"{start_question}_{end_question}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # Create subdirectory for PNG files
    png_output_dir = os.path.join(output_dir, f"{start_question}_{end_question}_{timestamp}_pngs")
    os.makedirs(png_output_dir, exist_ok=True)

    # Initialize the Chrome driver
    driver = initialize_driver()

    # List to store screenshot paths
    screenshot_filenames = []

    # Loop through the question numbers and take screenshots
    for question_number in range(start_question, end_question + 1):
        query, current_url, screenshot_filename = take_screenshot(
            driver, question_number, timestamp, png_output_dir
        )
        if query and current_url and screenshot_filename:
            sheet.append([question_number, query, current_url])
            screenshot_filenames.append(screenshot_filename)

    # Save the Excel workbook with timestamp and question range
    excel_filename = os.path.join(
        output_dir,
        f"queries_and_links_{start_question}_to_{end_question}_{timestamp}.xlsx",
    )
    workbook.save(excel_filename)
    print(f"Excel file saved as '{excel_filename}'")

    # Merge PNG files into a PDF
    pdf_filename = os.path.join(
        output_dir, f"screenshots_{start_question}_to_{end_question}_{timestamp}.pdf"
    )
    screenshot_paths = [
        os.path.join(png_output_dir, filename) for filename in screenshot_filenames
    ]
    merge_png_to_pdf(screenshot_paths, pdf_filename)
    # Close the browser
    driver.quit()
    print("Browser closed.")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Take screenshots of Google search results and save them to an Excel file and PDF."
    )
    parser.add_argument("start_question", type=int, help="The starting question number")
    parser.add_argument("end_question", type=int, help="The ending question number")
    args = parser.parse_args()

    # Run the main function with the provided arguments
    main(args.start_question, args.end_question)
