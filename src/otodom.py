import requests
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import logging

logging.getLogger().setLevel(logging.INFO)


class PageScraper:
    def __init__(self, min_price: int = 300000, max_price: int = 450000) -> None:
        self.headers: dict = {"User-Agent": "Mozilla/5.0"}
        self.offers_data: list = None
        self.min_price = min_price
        self.max_price = max_price
        self.url_page: int = 1
        # self.url: str = f"https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/wielicki/wieliczka?distanceRadius=0&page={self.url_page}&limit=36&priceMin={self.min_price}&priceMax={self.max_price}&ownerTypeSingleSelect=ALL&by=PRICE&direction=ASC&viewType=listing"

    def url_builder(self, page: int):
        url = f"https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/wielicki/wieliczka?distanceRadius=0&page={page}&limit=36&priceMin={self.min_price}&priceMax={self.max_price}&ownerTypeSingleSelect=ALL&by=PRICE&direction=ASC&viewType=listing"
        return url

    def perform_request(self, url):
        try:
            response = requests.get(url, allow_redirects=True, headers=self.headers)
            response.raise_for_status()

        except requests.exceptions.HTTPError as errh:
            logging.warning("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            logging.warning("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            logging.warning("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            logging.warning("OOps: Something Else", err)

        return response

    def get_data(self):
        response_data = self.perform_request(self.url_builder(page=1))
        soup = bs(response_data.content, "html.parser")
        soup_list = soup.find(type="application/json")
        data = json.loads(soup_list.text)
        page_count = data["props"]["pageProps"]["data"]["searchAds"]["pagination"][
            "totalPages"
        ]
        logging.info(f"Detected {page_count} pages with offers.")
        offers_data = data["props"]["pageProps"]["data"]["searchAds"]["items"]

        for page in range(1, page_count + 1):
            # TODO: consider better url handling
            url = self.url_builder(page=page)
            data = response_data = self.perform_request(url)
            soup = bs(data.content, "html.parser")
            soup_list = soup.find(type="application/json")
            data = json.loads(soup_list.text)
            new_offers = data["props"]["pageProps"]["data"]["searchAds"]["items"]
            offers_data.extend(new_offers)

        logging.info(f"Downloaded {len(offers_data)} flat offers.")
        return offers_data

    def process_raw_data(self, offers_data):
        output = list()
        for d in offers_data:
            offer_enitity = dict()
            try:
                offer_id = d.get("id")
                offer_title = d.get("title")
                address = d.get("location").get("address").get("street")
                if address:
                    street = address.get("name", "empty")

                location = d.get("locationLabel").get("value")
                total_price = d.get("totalPrice").get("value")
                area_square_meters = d.get("areaInSquareMeters")
                date_created_in_service = d.get("dateCreated")
                offer_url = "https://www.otodom.pl/pl/oferta/" + d.get("slug")
                agency = d.get("agency")
                if agency:
                    agency_name = agency.get("name")
                rooms_number = d.get("roomsNumber")
                investment_estimated_delivery = d.get("investmentEstimatedDelivery")
                price_per_square_meter = d.get("pricePerSquareMeter").get("value")

                offer_enitity["offer_id"] = offer_id
                offer_enitity["offer_title"] = offer_title
                offer_enitity["street"] = street
                offer_enitity["location"] = location
                offer_enitity["total_price"] = total_price
                offer_enitity["area_square_meters"] = area_square_meters
                offer_enitity["date_created_in_service"] = date_created_in_service
                offer_enitity["offer_url"] = offer_url
                offer_enitity["agency_name"] = agency_name
                offer_enitity["rooms_number"] = rooms_number
                offer_enitity[
                    "investment_estimated_delivery"
                ] = investment_estimated_delivery
                offer_enitity["price_per_square_meter"] = price_per_square_meter

                output.append(offer_enitity)

            except Exception as error:
                logging.warning(
                    f"Error with prosicessing data \n Error: {error} \n Item: {d}"
                )

        return output

    def run(self):
        data = self.get_data()

        output_data = self.process_raw_data(data)
        return output_data
