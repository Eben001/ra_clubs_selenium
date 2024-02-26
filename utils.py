import os
import re
from urllib.parse import urljoin
import random
from webdriver_manager.chrome import ChromeDriverManager


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
from fake_useragent import UserAgent

def configure_webdriver():
    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    proxy_list = [
    "103.139.144.242:8080",
    "38.52.209.42:999",
    "67.43.227.227:2405",
    "192.99.182.243:3128",
    "72.10.164.178:2879",
    "72.10.164.178:2549",
    "192.144.30.1:8019",
    "72.10.164.178:3029",
    "45.70.200.245:999",
    "67.43.228.253:2231",
    "94.25.154.242:3128",
    "67.43.236.20:2047",
    "67.43.228.253:2507"
]

    options.add_argument(f'user-agent={user_agent}')

    options.add_argument('--disable-gpu')

    options.add_argument('--disable-extensions')
    options.add_argument('--disable-webgl')

    options.add_argument('--lang=en-US,en;q=0.9')
    options.add_argument('--disable-webrtc')

    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    options.add_argument('--no-sandbox')

    options.add_argument("start-maximized")
    options.add_argument('--auto-open-devtools-for-tabs')

    options.add_argument('--window-size=1200x800')


    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


    # Selenium Stealth settings
    # stealth(driver,
    #         languages=["en-US", "en"],
    #         vendor="Google Inc.",
    #         platform="Win32",
    #         webgl_vendor="Intel Inc.",
    #         renderer="Intel Iris OpenGL Engine",
    #         fix_hairline=True,
    #         )

    return driver


def get_current_directory_path(filename):
    return os.path.join(os.getcwd(), filename)


global_df = pd.DataFrame({'City': [], 'City URL': [], 'Club': [],
                           'Club URL': [], 'Club Logo': [], 'Status (open, closed)': [], 'Address':[], 'Phone': [],
                           'Website URL': [], 'Maps URL': [],'Followers':[],'Capacity (ex)':[], '# of events so far this year': [],
                           'About': [], 'Images (Cover photo)': []}
                         )


def extract_title(title_section_element):
    title_section = title_section_element.find('div', class_='Box-omzyfs-0 Alignment-sc-1fjm9oq-0 kLTSYd')

    title = title_section.find('span', class_='Text-sc-1t0gn2o-0 jyznYD')

    if title:
        return title.text
    
    return None
def extract_logo_url(logo_section_element): 
    logo_section = logo_section_element.find('div', class_='Box-omzyfs-0 Alignment-sc-1fjm9oq-0 iRSjjL')


    img_tag = logo_section.find('img')
    if img_tag:
        src_url = img_tag['src']
        return src_url
   
    return None

def extract_clubs_details(club_details_section):
   
    phone_li_tag = club_details_section.find('li', class_='Column-sc-18hsrnn-0 irxIMu')
    phone = phone_li_tag.find('span', class_='Text-sc-1t0gn2o-0 cPrKJv').text.strip() if phone_li_tag else ""

    num_followers_li_tag = club_details_section.find('li', class_='Column-sc-18hsrnn-0 jLvlSf')
    num_followers = num_followers_li_tag.find('span', class_='Text-sc-1t0gn2o-0 bHUVhP').text.strip() if num_followers_li_tag else ""

    website_link = club_details_section.find('a', {'class': 'Link__AnchorWrapper-k7o46r-1 gIdCJS'}, string='Website')
    map_link = club_details_section.find('a', {'class': 'Link__AnchorWrapper-k7o46r-1 gIdCJS'}, string='Maps')

    return {
        "Phone": phone,
        "Website": website_link['href'] if website_link else "",
        "Map URL": map_link['href'] if map_link else "",
        "Number of Followers": num_followers
    }

def extract_club_stats(club_stats_section):
    # Find the span containing the text "Events so far this year"
    events_so_far_span = club_stats_section.find('span', {'class': 'Text-sc-1t0gn2o-0 gvmqzU'}, string="Events so far this year")

    num_events = ""
    if events_so_far_span:
        # Find the parent div of the span
        grand_parent_of_events_so_far_span = events_so_far_span.find_parent('div', {'class': 'Box-omzyfs-0 Alignment-sc-1fjm9oq-0 gNjGdd'})
        
        # Find the span with the actual number of events
        num_events_span = grand_parent_of_events_so_far_span.find('span', class_='Text-sc-1t0gn2o-0 QVpmH')
        if num_events_span:
            num_events = num_events_span.text

    # Find the span containing the text "Capacity"
    capacity_span = club_stats_section.find('span', {'class': 'Text-sc-1t0gn2o-0 gvmqzU'}, string="Capacity")

    capacity = ""
    if capacity_span:
        # Find the parent div of the span
        grand_parent_of_capacity_span = capacity_span.find_parent('div', {'class': 'Box-omzyfs-0 Alignment-sc-1fjm9oq-0 gNjGdd'})
        
        # Find the span with the actual capacity number
        num_capacity_span = grand_parent_of_capacity_span.find('span', class_='Text-sc-1t0gn2o-0 QVpmH')
        if num_capacity_span:
            capacity = num_capacity_span.text

    return {
        "Events so far": num_events,
        "Capacity": capacity
    }


def extract_about(about_section):
    # Find the span containing the about text
    about_span = about_section.find('span', class_='Text-sc-1t0gn2o-0 CmsContent__StyledText-sc-1s0tuo4-0 jQHBrl')


    about_text = ""

    if about_span:

        about_text = about_span.text

    return about_text


def extract_city_name(city_name_section):
    city_span = city_name_section.find('span', class_='Text-sc-1t0gn2o-0 Link__StyledLink-k7o46r-0 kJVTYu Breadcrumb__StyledLink-sc-12b96lt-0 bWanaM')
    city = ""
    if city_span:
        city = city_span.text.strip()
    
    return city
    

def parse_club_details(driver, full_link_club, full_link_city, club_name, club_address):
    global global_df
    driver.get(full_link_club)
    time.sleep(1)
    

    try:
        WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//span[@class="Text-sc-1t0gn2o-0 jyznYD"]')))
        
    except Exception as e:
      print(f"Error trying to locate element {e}")
    finally:
        soup = BeautifulSoup(driver.page_source, 'lxml')
    
    title_section_element = soup.find('div', class_='Layout-sc-1j5bbdx-0 ProfileHeader__FullHeightLayout-sc-1bgczdi-0 dHjEBU')
    logo_section_element = soup.find('div', class_='Layout-sc-1j5bbdx-0 ProfileHeader__FullHeightLayout-sc-1bgczdi-0 dHjEBU')
    about_section = soup.find('ul', class_='Grid__GridStyled-sc-1l00ugd-0 ejEHkT grid')
    club_details_section = soup.find('section', class_='Section__StyledSection-sc-3xc4is-0 kbzefb')
    club_stats_section = soup.find('ul', class_='Grid__GridStyled-sc-1l00ugd-0 bTZNVF grid')
    city_name_section = soup.find('ul', class_='Box-omzyfs-0 Alignment-sc-1fjm9oq-0 kpXgBZ')
    status_section = soup.find('div', class_='Layout-sc-1j5bbdx-0 Stack-sc-1rol8jo-0 fmvEcF')
    cover_photo_section = soup.find('div', class_='Box-omzyfs-0 eQrETM')


    logo = extract_logo_url(logo_section_element) if logo_section_element else ""
    title = extract_title(title_section_element) if title_section_element else ""
    city_name = extract_city_name(city_name_section) if city_name_section else ""
    club_details = extract_clubs_details(club_details_section) if club_details_section else {}
    
    
    
    about = extract_about(about_section) if about_section else ""
    club_stats = extract_club_stats(club_stats_section) if club_stats_section else {}
    status = "Closed" if status_section else "Open"
    cover_photo = cover_photo_section.find('img')['src']  if cover_photo_section else ""
   
    print(club_name)

    new_data = pd.DataFrame({
        'City': city_name,
        'City URL': full_link_city,
        'Club': club_name,
        'Club URL': full_link_club,
        'Club Logo': logo,
        'Status (open, closed)': status, 
        'Address':club_address,
        'Phone': club_details.get("Phone", ""),
        'Website URL': club_details.get("Website", ""),
        'Maps URL': club_details.get("Map URL", ""),
        'Followers': club_details.get("Number of Followers", ""),
        'Capacity (ex)': club_stats.get("Capacity", ""),
        '# of events so far this year': club_stats.get("Events so far", ""),
        'About': about,
        'Images (Cover photo)': cover_photo 
    })

    
    global_df = pd.concat([global_df, new_data], ignore_index=True)
    return global_df




  

