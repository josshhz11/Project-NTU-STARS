import getpass
# Libraries for web-scraping
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
# Libraries for Telegram bot
import telegram
import asyncio
from io import BytesIO
import requests

# Set up the Telegram bot
bot_token = '7397212238:AAELG46EzVmhtXJV-0gb_o0HLakpAJ8AgqE'
chat_id = '@projectntustars' # Set up your own Telegram Channel
bot = telegram.Bot(token=bot_token)

"""
To input these login information and course indexes you wish to swap
"""

username = input("Username: ")
password = getpass.getpass("Password: ")
index_to_swap = input("Old Index to Swap out of: ") # FILL THIS IN WITH YOUR OWN INDEX YOU WANT TO SWAP (DON'T NEED TO TYPE IN COURSE CODE) i.e. 01166
new_index_value = input("New Index to Swap to: ") # FILL THIS IN WITH THE NEW INDEX YOU WANT TO SWAP TO i.e. 01172


async def ntustars():
    while True:
        try:
            # Scrape every 1 min
            PATH = 'C:/Users/joshua/Downloads/chromedriver-win64/chromedriver.exe' # Change this to the path where the chrome driver you have installed is at, in this format 
            
            service = Service(PATH)
            options = Options()
            options.add_argument('--headless')  # Run headless Chrome, without a GUI
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')

            driver = webdriver.Chrome(service=service, options=options)
            url = 'https://wish.wis.ntu.edu.sg/pls/webexe/ldap_login.login?w_url=https://wish.wis.ntu.edu.sg/pls/webexe/aus_stars_planner.main'

            driver.get(url)

            """
            1st login page with just username
            """
            
            # To find the username field and fill it up
            username_field = driver.find_element(By.ID, "UID")
            username_field.send_keys(username)

            # Click the 'OK' button to proceed to the next page
            ok_button = driver.find_element(By.XPATH, "//input[@value='OK']")
            ok_button.click()

            """
            2nd login page with the password
            """

            # Wait for the password field to be present on the new page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "PW"))
            )

            # To find the password field and fill it up
            password_field = driver.find_element(By.ID, "PW")
            password_field.send_keys(password)

            # Click the 'OK' button to log in
            ok_button = driver.find_element(By.XPATH, "//input[@value='OK']")
            ok_button.click()

            """
            Main page with modules
            """

           # Wait for the table element to be present on the main page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[@bordercolor='#E0E0E0']"))
            )

            # Locate the radio button by its value attribute
            radio_button = driver.find_element(By.XPATH, f"//input[@type='radio' and @value='{index_to_swap}']")

            # Click the radio button
            radio_button.click()

            # Select the "Change Index" option from the dropdown
            dropdown = Select(driver.find_element(By.NAME, "opt"))
            dropdown.select_by_value("C")

            # Click the 'Go' button
            go_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Go']")
            go_button.click()

            """
            Swap index page after choosing the mod and index you want to swap
            """

            # Wait for the form element to be present on the swap index page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "AUS_STARS_MENU"))
            )

            # Select the "Change Index" option from the dropdown
            dropdown_element = driver.find_element(By.NAME, "new_index_nmbr")
            options = dropdown_element.find_elements(By.XPATH, f".//option[@value='{new_index_value}']")

            # Check if the element exists
            if options:
                option = options[0]
                option_text = option.text  # This should give you "01172 / 9 / 1"
                print(option_text)

                # Parse out the middle number (vacancies)
                vacancies = int(option_text.split(" / ")[1])
                print(f"The number of vacancies for index {new_index_value} is {vacancies}.")
            else:
                print("The option was not found.")
            
            driver.quit()

            # Write the Telegram message to broadcast to the channel
            if (vacancies > 0):
                caption = f"{vacancies} available slots for index {new_index_value}"
            elif (vacancies == 0):
                caption = f"No vacancies for index {new_index_value}"

            await bot.send_message(chat_id=chat_id, text=caption)
            # Sleep for 5 minutes
            '''
            function sleeps for 5 minutes after each scrape using asyncio.sleep(300)
            (300 seconds = 5 minutes).
            '''
            await asyncio.sleep(300)
        # Throw an error if the problem is network connection or url timedout 
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"HTTP request error: {e}")
            """
            blocks will now sleep for 1 minute (60 seconds) 
            before retrying after an HTTP or Telegram API error.
            """
            await asyncio.sleep(30)
        # Throw an error if the problem is telgram timed out 
        except telegram.error.TelegramError as e:
            print(f"Telegram API error: {e}")
            await asyncio.sleep(30)
if __name__ == '__main__':
    """
    asyncio is a Python module that provides infrastructure for writing single-threaded,
    asynchronous code using coroutines, event loops, and tasks.
    It allows you to write non-blocking, concurrent code that can handle many I/O-bound tasks efficiently.
    """
    asyncio.run(ntustars())
