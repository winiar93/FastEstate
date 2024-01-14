import requests
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
import logging
from typing import List, Dict

logging.getLogger().setLevel(logging.INFO)


class PageScraper:
    def __init__(self, min_price: int = 300000,
                 max_price: int = 450000,
                 province: str = "malopolskie",
                 district: str = "wielicki",
                 city: str = "wieliczka",
                 ) -> None:

        self.base_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie"
        self.headers: dict = {"User-Agent": "Mozilla/5.0"}
        self.min_price = min_price
        self.max_price = max_price
        self.province = province
        self.district = district
        self.city = city
        self.url_page: int = 1
        self._offers_raw_data: dict = dict()
        self._page_count: int = 0
        self.direction = "DESC"
        self.view_type = "listing"

    def url_builder(self, page: int, limit=36):

        link = f"{self.base_url}?&page={page}&limit={limit}&ownerTypeSingleSelect=ALL&priceMin={self.min_price}&" \
               f"priceMax={self.max_price}"
        link += f"&by=DEFAULT&direction={self.direction}&viewType={self.view_type}"

        if self.province and self.district and self.city:
            location_str = f"{self.province}/{self.district}/{self.city}"
            link += f"&locations=%5B{location_str}%5D"

        return link

    def perform_request(self, url: str) -> requests.Response():
        try:
            response = requests.get(url, allow_redirects=True, headers=self.headers)
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            logging.error("Http Error:", err)
        except requests.exceptions.ConnectionError as err:
            logging.error("Error Connecting:", err)
        except requests.exceptions.Timeout as err:
            logging.error("Timeout Error:", err)
        except requests.exceptions.RequestException as err:
            logging.error("OOps: Something Else", err)

        return response

    def get_data(self) -> List[Dict[str, str]]:
        response_data = self.perform_request(self.url_builder(page=1))
        soup = bs(response_data.content, "html.parser")
        soup_list = soup.find(type="application/json")

        self._offers_raw_data = json.loads(soup_list.text)

        return self._offers_raw_data

    def get_page_count(self) -> int:
        try:
            self._page_count = self._offers_raw_data["props"]["pageProps"]["data"]["searchAds"]["pagination"][
                "totalPages"
            ]
            logging.info(f"Detected {self._page_count} pages with offers.")
        except KeyError:
            logging.error('Error processing data, totalPages value not fount')

        return self._page_count

    def get_data_by_pagination(self) -> List[Dict[str, str]]:

        offers_data = self._offers_raw_data["props"]["pageProps"]["data"]["searchAds"]["items"]
        for page in range(1, self._page_count + 1):
            try:
                url = self.url_builder(page=page)
                data = self.perform_request(url)
                soup = bs(data.content, "html.parser")
                soup_list = soup.find(type="application/json")
                data = json.loads(soup_list.text)
                new_offers = data["props"]["pageProps"]["data"]["searchAds"]["items"]
                offers_data.extend(new_offers)

            except Exception as e:
                logging.error(f'Error with performing request on page {page} \n more details: {e}')

        logging.info(f"Downloaded {len(offers_data)} flat offers.")
        return offers_data

    @staticmethod
    def process_raw_data(offers_data: list) -> List[Dict[str, str]]:
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
                try:
                    location_list = d.get("location").get('reverseGeocoding').get('locations')
                    if len(location_list) >= 1:
                        location = location_list[-1].get('fullName')
                except Exception as err:
                    logging.error(f"Error with parsing location data: {d} \n", err)
                    location = None
                    pass

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
                logging.error(
                    f"Error with processing data \n Error: {error} \n Item: {d}"
                )

        return estate_offers_lst

    def run(self):
        self.get_data()
        self.get_page_count()
        data = self.get_data_by_pagination()

        return self.process_raw_data(data)
