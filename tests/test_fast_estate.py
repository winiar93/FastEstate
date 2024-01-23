import pytest
from src.db_connector import DBConnector
from src.otodom import PageScraper
from src.sql_models import FlatOffers
from unittest.mock import patch, PropertyMock, MagicMock
from testing_data import raw_data, raw_data_list
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture(params=None, name="page_scraper")
def page_scraper():
    ps = PageScraper()
    return ps


@pytest.mark.parametrize(
    "province,district,city", [("test_province", "test_district", "test_city")]
)
def test_page_scraper_class(province, district, city):
    ps = PageScraper(province=province, district=district, city=city)

    assert ps.province == "test_province"
    assert ps.district == "test_district"
    assert ps.city == "test_city"


@pytest.mark.parametrize("page_number", [6, 8, 42])
def test_page_scraper(page_scraper, page_number) -> None:
    link = page_scraper.url_builder(page=page_number)
    assert "https://www.otodom.pl" in link


def test_get_data(page_scraper):
    page_scraper.get_data()
    page_cnt_int = page_scraper.get_page_count()
    assert isinstance(page_cnt_int, int)
    assert page_cnt_int > 0

    page_scraper._page_count = 1
    raw_data = page_scraper.get_data_by_pagination()
    assert isinstance(raw_data, list)
    estate_offers_lst = page_scraper.process_raw_data(offers_data=raw_data)
    assert estate_offers_lst[0].get("offer_id") > 1


@patch.object(
    PageScraper,
    "get_data_by_pagination",
    return_value=raw_data_list,
)
def test_mock_get_data_by_pagination(scraper_mock, page_scraper):
    test_data_list = page_scraper.get_data_by_pagination()
    estate_offers_lst = page_scraper.process_raw_data(test_data_list)
    assert estate_offers_lst[0].get("offer_id") == 64629218
    scraper_mock.assert_called_with()


@pytest.mark.parametrize("raw_data", [raw_data])
def test_mock_get_page_count(page_scraper, raw_data):
    page_scraper._offers_raw_data = raw_data
    page_count = page_scraper.get_page_count()
    assert isinstance(page_count, int)
    assert page_count == 3


def test_patch_get_page_count(page_scraper):
    with patch.object(page_scraper, "_offers_raw_data", new=raw_data):
        page_count = page_scraper.get_page_count()
        assert isinstance(page_count, int)
        assert page_count == 3


@patch("src.db_connector.DBConnector.get_sqlmodel_engine")
def test_database_connection(mock_create_engine):
    db_connector = DBConnector(
        pg_user="mock_user",
        pg_dbname="mock_database",
        pg_password="mock_password",
        pg_host="mock_host",
        pg_port="mock_port",
    )

    assert (
        db_connector.pg_con_string
        == "postgresql+psycopg2://mock_user:mock_password@mock_host:mock_port/mock_database"
    )


def test_create_offer():
    offer_data = {"offer_id": 123, "street": "Street 123", "offer_title": "Offer Title"}
    test_single_offer = FlatOffers(**offer_data)
    assert test_single_offer
    assert test_single_offer.offer_id == offer_data["offer_id"]
    assert test_single_offer.street == offer_data["street"]
    assert test_single_offer.offer_title == offer_data["offer_title"]
