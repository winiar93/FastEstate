import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
#import chromedriver_autoinstaller
import time
import re
import pandas as pd
import numpy as np

class PageScraper:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")   
    #chrome_options.add_argument('window-size=1200x600')
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

    def get_data(page_limit: int = 100):

        data = []
        website = f'https://www.otodom.pl/pl/wyszukiwanie/sprzedaz/mieszkanie/malopolskie/wielicki/wieliczka?page=1&limit={page_limit}&market=ALL&distanceRadius=0&priceMin=300000&priceMax=450000&by=PRICE&direction=ASC'
        
        driver.maximize_window()
        driver.get(website)

        time.sleep(2)

        #CHECK
        #cookies_button = driver.find_element(by=By.XPATH, value='//button[@id="onetrust-accept-btn-handler"]')
        cookies_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        time.sleep(1)
        cookies_button.click()
        time.sleep(2)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        location = driver.find_elements(by=By.XPATH, value='//span[@class="css-17o293g es62z2j9"]')
        urls = driver.find_elements(by=By.XPATH, value='//a[@data-cy="listing-item-link"]')
        flats_data = driver.find_elements(by=By.XPATH, value='//span[@class="css-s8wpzb e1brl80i2"]')

        flats_data = [data.text for data in flats_data]
        flats_data_grouped = np.array_split(flats_data, len(flats_data)/4)
        for f, u, l in zip(flats_data_grouped, urls, location):
            row_data = list(f)
            row_data.append(u.get_attribute('href'))
            row_data.append(l.text)
            data.append(row_data)

        df = pd.DataFrame(data, columns =['Price', 'Price per m2', 'Rooms', 'Size M2', 'URL', 'Location'])
        df.drop_duplicates(subset=['URL'])

        df['Price'] = df['Price'].apply(clear_txt)
        df['Price per m2'] = df['Price per m2'].apply(clear_txt)
        df['Size M2'] = df['Size M2'].apply(clear_txt)

        df = df.sort_values(['Price', 'Size M2'],
                    ascending = [True, True])
        output = df.to_dict("records")   

        df.to_csv("flats_data.csv", sep='\t')  

        driver.quit()
        return  output
