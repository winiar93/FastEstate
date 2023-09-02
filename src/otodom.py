import requests
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import logging

logging.getLogger().setLevel(logging.INFO)


class PageScraper:
    def __init__(self, min_price: int = 300000, max_price: int = 450000) -> None:
        self.headers: dict = {"User-Agent": "Mozilla/5.0"}
        self.min_price = min_price
        self.max_price = max_price
        self.url_page: int = 1

    def url_builder(self, page: int):
        url = f"https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/malopolskie/wielicki/wieliczka?distanceRadius=0" \
              f"&page={page}&limit=36&priceMin={self.min_price}&pri" \
              f"ceMax={self.max_price}&ownerTypeSingleSelect=ALL&by=PRICE&direction=ASC&viewType=listing"
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
            data = self.perform_request(url)
            soup = bs(data.content, "html.parser")

            soup_list = soup.find(type="application/json")

            data = json.loads(soup_list.text)

            new_offers = data["props"]["pageProps"]["data"]["searchAds"]["items"]
            offers_data.extend(new_offers)

        logging.info(f"Downloaded {len(offers_data)} flat offers.")
        return offers_data

    @staticmethod
    def process_raw_data(offers_data):
        estate_offers_lst = list()
        for d in offers_data:
            estate_offer = dict()
            try:
                offer_id = d.get("id")
                offer_title = d.get("title")
                address = d.get("location").get("address").get("street")
                street = None
                if address:
                    street = address.get("name", "empty")

                location = d.get("locationLabel", {}).get("value")
                total_price_dict = d.get("totalPrice")

                total_price = None
                if total_price_dict:
                    total_price = total_price_dict.get("value")

                area_square_meters = d.get("areaInSquareMeters")
                date_created_in_service = d.get("dateCreated")
                offer_url = "https://www.otodom.pl/pl/oferta/" + d.get("slug")
                agency = d.get("agency")
                agency_name = None
                if agency:
                    agency_name = agency.get("name")

                rooms_number = d.get("roomsNumber")
                investment_estimated_delivery = d.get("investmentEstimatedDelivery", {})
                price_per_square_meter_dict = d.get("pricePerSquareMeter")
                price_per_square_meter = None
                if price_per_square_meter_dict:
                    price_per_square_meter = price_per_square_meter_dict.get("value")

                estate_offer["offer_id"] = offer_id
                estate_offer["offer_title"] = offer_title
                estate_offer["street"] = street
                estate_offer["location"] = location
                estate_offer["total_price"] = total_price
                estate_offer["area_square_meters"] = area_square_meters
                estate_offer["date_created_in_service"] = date_created_in_service
                estate_offer["offer_url"] = offer_url
                estate_offer["agency_name"] = agency_name
                estate_offer["rooms_number"] = rooms_number
                estate_offer[
                    "investment_estimated_delivery"
                ] = investment_estimated_delivery
                estate_offer["price_per_square_meter"] = price_per_square_meter

                estate_offers_lst.append(estate_offer)

            except Exception as error:
                logging.warning(
                    f"Error with processing data \n Error: {error} \n Item: {d}"
                )

        return estate_offers_lst

    def run(self):
        data = self.get_data()
        return self.process_raw_data(data)
