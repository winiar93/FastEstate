import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
#import chromedriver_autoinstaller
import time
import re
import pandas as pd

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")   
chrome_options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
#for local testing
# path = 'chromedriver.exe'
# driver = webdriver.Chrome(executable_path=path)#, options=chrome_options)

def clear_txt(text):

    try:
        if "Zapytaj" in text:
            return text
        else:
            text_str = "".join(text.split()).split("z")[0].replace("m²","")
            return text_str
    except ValueError: 
        return 0 

def get_data():
    website = 'https://www.otodom.pl/pl/wyszukiwanie/sprzedaz/mieszkanie/malopolskie/wielicki/wieliczka?page=1&limit=400&market=ALL&distanceRadius=0&priceMin=300000&priceMax=450000&by=PRICE&direction=ASC'
    
    
    driver.maximize_window()
    driver.get(website)

    # time.sleep(6)
    # cookies_button = driver.find_element(by=By.XPATH, value='//button[@id="onetrust-accept-btn-handler"]')
    # time.sleep(1)
    # cookies_button.click()
    time.sleep(2)

    location = []
    prices = []
    m2_price = []
    rooms = []
    m2 = []
    urls = []


    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    loc = driver.find_elements(by=By.XPATH, value='//p[@class="css-80g06k es62z2j12"]')
    details = driver.find_elements(by=By.XPATH, value='//span[@class="css-s8wpzb eclomwz2"]')
    links = driver.find_elements(by=By.XPATH, value='//a[@data-cy="listing-item-link"]')

    # create a list of locations
    for t in loc:
        location.append(t.text)

    # create a list of listing details
    x = 0
    while x < len(details):
        prices.append(details[x].text)
        m2_price.append(details[x+1].text)
        rooms.append(details[x + 2].text)
        m2.append(details[x + 3].text)
        x += 4

    for l in links:
        urls.append(l.get_attribute('href'))

    df = pd.DataFrame(list(zip(location, prices, m2_price, m2, rooms, urls)),
                columns =['Location', 'Price', 'Price per m2', 'Size M2', 'Rooms', 'URL'])
    df.drop_duplicates(subset=['URL'])

    df['Price'] = df['Price'].apply(clear_txt)
    df['Price per m2'] = df['Price per m2'].apply(clear_txt)
    df['Size M2'] = df['Size M2'].apply(clear_txt)

    df = df.sort_values(['Price', 'Size M2'],
                ascending = [True, True])
    output = df.to_dict("record")     

    driver.quit()
    return  output

#print(get_data())