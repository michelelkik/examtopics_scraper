
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


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


def take_screenshot(question_number, timestamp, png_output_dir, results):
    driver = initialize_driver()
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

        results.append((question_number, query, current_url, screenshot_filename))

    except Exception as e:
        print(
            f"An error occurred during the process for question number {question_number}: {e}"
        )
        results.append((question_number, None, None, None))
    finally:
        driver.quit()
