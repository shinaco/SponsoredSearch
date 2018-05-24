from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

#CHROME_PATH         = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
#CHROMEDRIVER_PATH   = '/usr/local/bin/chromedriver'
CHROME_PATH         = '/usr/bin/google-chrome'
CHROMEDRIVER_PATH   = '/usr/bin/chromedriver'
WINDOW_SIZE         = "1920x1080"

chrome_options = Options()  
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH

def make_screenshot(url, output):
    if not url.startswith('http'):
        raise Exception('URLs need to start with "http"')

    driver = webdriver.Chrome(
        chrome_options=chrome_options,
        executable_path=CHROMEDRIVER_PATH
    )  
    driver.get(url)
    driver.save_screenshot(output)
    driver.close()
