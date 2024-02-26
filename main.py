from utils import *
import os
import re
from urllib.parse import urljoin
import random
# import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains


driver = configure_webdriver()

base_url = 'https://ra.co/clubs'
url = 'https://ra.co/clubs/uk/london'
driver.get(url)
time.sleep(2)

try:
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="Box-omzyfs-0 hrYUzb"]')))
    
    
    soup =  BeautifulSoup(driver.page_source, 'lxml')

    clubs = soup.find_all('div', class_='Box-omzyfs-0 hrYUzb')

    for club in clubs: 
        link_element = club.find('a', class_='Link__AnchorWrapper-k7o46r-1 cCjFlH')
        link = link_element['href']
        full_link_club = urljoin(base_url, link)
        club_name = club.find('span', class_='Text-sc-1t0gn2o-0 Link__StyledLink-k7o46r-0 fUgzMh').text
        club_address = club.find('span', class_='Text-sc-1t0gn2o-0 hoJWcj').text

        parse_club_details(driver, full_link_club, url, club_name, club_address)
        break

except Exception as e:
    print(f"Error while trying to find the club items element: {str(e)}")

finally:
    csv_file_path = get_current_directory_path('ra_clubs_data.csv')
    global_df.to_csv(csv_file_path, index=False)
    driver.save_screenshot("result.png")
    driver.quit()
