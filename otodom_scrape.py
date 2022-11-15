from playwright.sync_api import sync_playwright
import time
import pandas as pd

def clear_txt(text):

    try:
        return int(''.join(filter(str.isdigit,text.replace("²",""))))
    except ValueError: 
        return 0 

data_records = []

def get_page_content():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context()
        page = context.new_page()

        for page_number in range(1,15):

            page.goto(f"https://www.otodom.pl/pl/wyszukiwanie/sprzedaz/mieszkanie/malopolskie/wielicki/wieliczka?page={page_number}&limit=10&market=ALL&distanceRadius=0&priceMin=300000&priceMax=400000&by=PRICE&direction=ASC")
            time.sleep(1)
            if page_number == 1:
                page.get_by_role("button", name="Akceptuję").click()
                time.sleep(1)
            page.mouse.wheel(0, 6000)
            time.sleep(1)
            flats = page.query_selector_all("li[class*='css-p74l73 es62z2j19']")
            print(len(flats))
            for f in flats:
                url = f.query_selector('xpath=//a[@data-cy="listing-item-link"]').get_attribute("href")
                url = "https://www.otodom.pl"+url
                pirce = clear_txt(f.query_selector("span[class*='css-s8wpzb eclomwz2']").inner_text())
                try:
                    price_per_m2 = clear_txt(f.query_selector("span[class*='css-s8wpzb eclomwz2'] strong").inner_text())
                except AttributeError:
                    price_per_m2 = 0
                square_m = float(f.query_selector("span[class*='css-s8wpzb eclomwz2']:nth-child(4)").inner_text().replace("m²","").strip())
                location = f.query_selector('//p[@class="css-80g06k es62z2j12"]').inner_text().replace(",","")

                data_row = [url, pirce, price_per_m2, square_m, location]
                print(data_row)
                data_records.append(data_row)

get_page_content()

df = pd.DataFrame(data_records, columns = ['URL', 'Price', 'Pln/m2', 'Square meters', 'location'])
print(df.shape)
print(df.head())
df.drop_duplicates(subset=['URL'])
df = df.sort_values(['Price', 'Square meters'],
              ascending = [True, True])
df.to_csv("ceny_mieszkan.csv", sep=';', index=False)


        