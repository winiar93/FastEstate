from src.otodom import PageScraper
import pytest

from unittest.mock import patch, Mock
import requests

offert_test_data = {'offer_id': 64629218, 'offer_title': '2-pokojowe mieszkanie 33m2 + balkon Bezpośrednio',
                    'street': 'ul. Długa', 'location': 'Czarnochowice, Wieliczka, wielicki, małopolskie',
                    'total_price': 376403, 'area_square_meters': 33.31,
                    'date_created_in_service': '2024-01-21 14:40:19',
                    'offer_url': 'https://www.otodom.pl/pl/oferta/2-pokojowe-mieszkanie-33m2-balkon-bezposrednio-ID4nb0K',
                    'agency_name': 'PM Development Paweł Mleko',
                    'rooms_number': 2, 'investment_estimated_delivery': None,
                    'price_per_square_meter': 11300}

raw_data_list = [{'id': 64629218, 'title': '2-pokojowe mieszkanie 33m2 + balkon Bezpośrednio', 'slug': '2-pokojowe-mieszkanie-33m2-balkon-bezposrednio-ID4nb0K', 'estate': 'FLAT', 'developmentId': 64629204, 'developmentTitle': 'Ecco Panorama', 'developmentUrl': 'https://www.otodom.pl/pl/oferta/ecco-panorama-ID4nb0v', 'transaction': 'SELL', 'location': {'mapDetails': {'radius': 0, '__typename': 'MapDetails'}, 'address': {'street': {'name': 'ul. Długa', 'number': '', '__typename': 'Street'}, 'city': {'name': 'Czarnochowice', '__typename': 'City'}, 'province': {'name': 'małopolskie', '__typename': 'Province'}, '__typename': 'Address'}, 'reverseGeocoding': {'locations': [{'fullName': 'małopolskie', '__typename': 'BasicLocationObject'}, {'fullName': 'wielicki, małopolskie', '__typename': 'BasicLocationObject'}, {'fullName': 'Wieliczka, wielicki, małopolskie', '__typename': 'BasicLocationObject'}, {'fullName': 'Czarnochowice, Wieliczka, wielicki, małopolskie', '__typename': 'BasicLocationObject'}], '__typename': 'ReverseGeocoding'}, '__typename': 'LocationDetails'}, 'images': [{'medium': 'https://ireland.apollo.olxcdn.com/v1/files/eyJmbiI6IjZkZjIzNnYxdDFibDMtRUNPU1lTVEVNIiwidyI6W3siZm4iOiJlbnZmcXFlMWF5NGsxLUFQTCIsInMiOiIxNCIsInAiOiIxMCwtMTAiLCJhIjoiMCJ9XX0.6wTqRpjypvzdFCNDwi4YouVmPtKywBb_rOajcJPfKtE/image;s=655x491;q=80', 'large': 'https://ireland.apollo.olxcdn.com/v1/files/eyJmbiI6IjZkZjIzNnYxdDFibDMtRUNPU1lTVEVNIiwidyI6W3siZm4iOiJlbnZmcXFlMWF5NGsxLUFQTCIsInMiOiIxNCIsInAiOiIxMCwtMTAiLCJhIjoiMCJ9XX0.6wTqRpjypvzdFCNDwi4YouVmPtKywBb_rOajcJPfKtE/image;s=1280x1024;q=80', '__typename': 'AdImage'}, {'medium': 'https://ireland.apollo.olxcdn.com/v1/files/eyJmbiI6Im9lM2N2cmxib3V5YjMtRUNPU1lTVEVNIiwidyI6W3siZm4iOiJlbnZmcXFlMWF5NGsxLUFQTCIsInMiOiIxNCIsInAiOiIxMCwtMTAiLCJhIjoiMCJ9XX0.pnlY3WJE6G4pKp-TD7OLy6xNrjsuLprsPd-XIbIybVk/image;s=655x491;q=80', 'large': 'https://ireland.apollo.olxcdn.com/v1/files/eyJmbiI6Im9lM2N2cmxib3V5YjMtRUNPU1lTVEVNIiwidyI6W3siZm4iOiJlbnZmcXFlMWF5NGsxLUFQTCIsInMiOiIxNCIsInAiOiIxMCwtMTAiLCJhIjoiMCJ9XX0.pnlY3WJE6G4pKp-TD7OLy6xNrjsuLprsPd-XIbIybVk/image;s=1280x1024;q=80', '__typename': 'AdImage'}], 'isExclusiveOffer': False, 'isPrivateOwner': False, 'isPromoted': False, 'agency': {'id': 8130402, 'name': 'PM Development Paweł Mleko', 'slug': 'pm-development-pawel-mleko-ID8130402', 'imageUrl': None, 'type': 'DEVELOPER', 'brandingVisible': False, 'highlightedAds': False, '__typename': 'AgencyListingDetails'}, 'openDays': '', 'totalPrice': {'value': 376403, 'currency': 'PLN', '__typename': 'Money'}, 'rentPrice': None, 'priceFromPerSquareMeter': None, 'pricePerSquareMeter': {'value': 11300, 'currency': 'PLN', '__typename': 'Money'}, 'areaInSquareMeters': 33.31, 'terrainAreaInSquareMeters': None, 'roomsNumber': 'TWO', 'hidePrice': False, 'floorNumber': 'FIRST', 'investmentState': None, 'investmentUnitsAreaInSquareMeters': None, 'peoplePerRoom': None, 'dateCreated': '2024-01-21 14:40:19', 'dateCreatedFirst': '2023-09-20 12:10:54', 'investmentUnitsNumber': None, 'investmentUnitsRoomsNumber': None, 'investmentEstimatedDelivery': None, 'pushedUpAt': '2024-01-21T14:40:19+01:00', 'specialOffer': None, 'shortDescription': '2-pokojowe mieszkanie numer 10  na 1. piętrze w budynku A w Inwestycji ECCO PANORAMA Dewelopera PM Development Paweł MlekoPonadstandardowa wysokość pomieszczeńPuszcza Niepołomicka (20 minut samochodem...', '__typename': 'AdvertListItem', 'totalPossibleImages': 8}]


class ResponseGetMock(object):
    def json(self):
        return {'avatar_url': 'test'}


@pytest.mark.parametrize("province,district,city", [("test_province", "test_district", "test_city")])
def test_page_scraper_class(province,district,city):
    ps = PageScraper(province=province, district=district, city=city)

    assert ps.province == "test_province"
    assert ps.district == "test_district"
    assert ps.city == "test_city"


@pytest.mark.parametrize("page_number", [6, 8, 42])
def test_page_scraper(page_number) -> None:

    ps = PageScraper()
    link = ps.url_builder(page=page_number)
    assert "https://www.otodom.pl" in link


def test_get_data():
    ps = PageScraper()
    ps.get_data()
    page_cnt_int = ps.get_page_count()
    assert isinstance(page_cnt_int, int)
    assert page_cnt_int > 0

    ps._page_count = 1
    raw_data = ps.get_data_by_pagination()
    assert isinstance(raw_data, list)
    estate_offers_lst = ps.process_raw_data(offers_data=raw_data[:1])
    assert estate_offers_lst[0].get("offer_id") > 1

def test_mock_data():
    with patch("src.otodom.PageScraper.get_data_by_pagination", return_value=raw_data_list):
        ps = PageScraper()
        test_data_list = ps.get_data_by_pagination()
        estate_offers_lst = ps.process_raw_data(test_data_list)
        assert estate_offers_lst[0].get("offer_id") == 64629218
@pytest.mark.parametrize("raw_data_list", [raw_data_list])
def test_mock_data(raw_data_list):

    ps = PageScraper()
    ps._offers_raw_data = raw_data_list
    test_data_list = ps.get_data_by_pagination()
    assert test_data_list[0].get("offer_id") == 64629218

