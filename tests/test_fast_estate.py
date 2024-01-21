from src.otodom import PageScraper
import pytest

from unittest.mock import patch, Mock
import requests

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
