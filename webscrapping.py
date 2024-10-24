import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Setup Edge WebDriver with headless option
edge_options = Options()
edge_options.use_chromium = True
edge_options.headless = True  # Enable headless mode
service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service, options=edge_options)

# Initialize an empty list to store course data
courses_data = []

# Start by navigating to the page
driver.get("https://courses.analyticsvidhya.com/collections/courses")

# Loop through multiple pages (1 to 8 in this case)
for page_num in range(1, 9):
    # Navigate to each page
    driver.get(f"https://courses.analyticsvidhya.com/collections/courses?page={page_num}")

    # Wait for the course cards to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.course-card"))
    )

    # Select all course cards
    course_cards = driver.find_elements(By.CSS_SELECTOR, "a.course-card")

    for card in course_cards:
        # Extract course title (default to "N/A" if not found)
        try:
            title = card.find_element(By.CSS_SELECTOR, "h3").text
        except Exception:
            title = "N/A"

        # Extract number of lessons (default to "N/A" if not found)
        try:
            lessons = card.find_element(By.CSS_SELECTOR, ".course-card__lesson-count strong").text
        except Exception:
            lessons = "N/A"

        # Extract price (default to "N/A" if not found)
        try:
            price = card.find_element(By.CSS_SELECTOR, ".course-card__price strong").text
        except Exception:
            price = "N/A"

        # Extract image URL (default to "N/A" if not found)
        try:
            image_url = card.find_element(By.CSS_SELECTOR, ".course-card__img").get_attribute("src")
        except Exception:
            image_url = "N/A"

        # Extract course link (default to "N/A" if not found)
        try:
            course_link = card.get_attribute("href")
            if course_link is None or not course_link.startswith("http"):
                raise ValueError("Invalid URL")
        except Exception as e:
            course_link = "N/A"
            continue  # Skip this course if there's no valid link

        # Now, go to the individual course page to extract more details
        try:
            driver.get(course_link)
            time.sleep(3)  # Wait for the page to load

            # Wait until the description (h2) is present
            description = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2"))
            ).text

            # Extract the curriculum (example CSS selector, adjust as needed)
            curriculum = driver.find_elements(By.CSS_SELECTOR, ".course-curriculum__chapter")  # Update this selector
            curriculum_list = [item.text for item in curriculum]  # Assuming each item is a lesson
            curriculum_text = "; ".join(curriculum_list) if curriculum_list else "N/A"

        except Exception as e:
            print(f"Error navigating to course page: {e}")
            description = "N/A"
            curriculum_text = "N/A"

        # Store the data in a dictionary and append it to the list
        courses_data.append({
            "Page Number": page_num,
            "Title": title,
            "Lessons": lessons,
            "Price": price,
            "Image URL": image_url,
            "Course Link": course_link,
            "Description": description,
            "Curriculum": curriculum_text,  # Add curriculum here
        })

# Quit the driver after scraping
driver.quit()

# Convert the list of dictionaries to a pandas DataFrame
courses_df = pd.DataFrame(courses_data)

# Optionally, you can save the DataFrame to a CSV file
courses_df.to_csv('analytics_course.csv', index=False)

# Display the DataFrame (optional)
print(courses_df)
