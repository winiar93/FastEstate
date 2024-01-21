from src.otodom import PageScraper
import pytest
from unittest.mock import patch
from testing_data import raw_data, raw_data_list

@pytest.mark.parametrize("province,district,city", [("test_province", "test_district", "test_city")])
def test_page_scraper_class(province, district, city):
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
    estate_offers_lst = ps.process_raw_data(offers_data=raw_data)
    assert estate_offers_lst[0].get("offer_id") > 1


def test_mock_get_data_by_pagination():
    with patch("src.otodom.PageScraper.get_data_by_pagination", return_value=raw_data_list):
        ps = PageScraper()
        test_data_list = ps.get_data_by_pagination()
        estate_offers_lst = ps.process_raw_data(test_data_list)
        assert estate_offers_lst[0].get("offer_id") == 64629218


@pytest.mark.parametrize("raw_data", [raw_data])
def test_mock_get_page_count(raw_data):
    ps = PageScraper()
    ps._offers_raw_data = raw_data
    page_count = ps.get_page_count()
    assert isinstance(page_count, int)
    assert page_count == 3
