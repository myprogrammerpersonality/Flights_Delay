import requests
from requests import RequestException
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from logger import Logger
import logging
import time

logger = Logger(__name__, loglevel=logging.INFO).get_logger()

BASE_URL = "https://fids.airport.ir/2/%D8%A7%D8%B7%D9%84%D8%A7%D8%B9%D8%A7%D8%AA-%D9%BE%D8%B1%D9%88%D8%A7%D8%B2-%D9%81%D8%B1%D9%88%D8%AF%DA%AF%D8%A7%D9%87-%D9%85%D9%87%D8%B1%D8%A2%D8%A8%D8%A7%D8%AF"
DATA_FILE = "flights.csv"

class FlightScraper:
    def __init__(self, url=BASE_URL):
        self.url = url
        self.flight_list = []

    def _fetch_page_content(self):
        try:
            page = requests.get(self.url, timeout=10)
            page.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            logger.info("Fetched")
            return page.content
        except RequestException as e:
            logger.error(f"Error fetching the page content: {e}")
            return None

    @staticmethod
    def _process_input(bs4_object, field_name):
        if not bs4_object:
            logger.error(f"Encountered a None object for field '{field_name}' when trying to process input with bs4.")
            return None
        try:
            return bs4_object.text.strip()
        except AttributeError as e:
            logger.error(f"Error parsing the page with bs4: {e}")
            return None

    @staticmethod
    def _calc_delay(formal_time, real_time):
        if not formal_time or not real_time:
            return None
        formal_datetime = datetime.strptime(formal_time[-5:], '%H:%M')
        real_datetime = datetime.strptime(real_time[-5:], '%H:%M')
        return abs((real_datetime - formal_datetime).total_seconds() // 60)

    def _parse_flight_info(self, flight):
        return {
            "flight_destination": self._process_input(flight.find("td", class_="cell-dest"), "flight_destination"),
            "flight_airline": self._process_input(flight.find("td", class_="cell-airline"), "flight_airline"),
            "flight_official_date": self._process_input(flight.find("td", class_="cell-day"), "flight_official_date"),
            "flight_number": self._process_input(flight.find("td", class_="cell-fno"), "flight_number"),
            "flight_status": self._process_input(flight.find("td", class_="cell-status"), "flight_status"),
            "flight_real_date": self._process_input(flight.find("td", class_="cell-dateTime2"), "flight_real_date"),
        }

    def scrape_flights(self):
        content = self._fetch_page_content()
        if content:
            soup = BeautifulSoup(content, "html.parser")
            job_elements = soup.find_all("tr", class_="status-default")
            for flight in job_elements:
                # filter out exiting flights
                if flight.find("td", class_="cell-dest"):
                    flight_info = self._parse_flight_info(flight)
                    self.flight_list.append(flight_info)
                else:
                    pass
            return True
        else:
            return False
    
    def save_to_csv(self):
        flight_df = pd.DataFrame(self.flight_list)
        flight_df = flight_df[flight_df.flight_status == "پرواز كرد"]
        flight_df['delay_min'] = flight_df.apply(lambda x: self._calc_delay(x['flight_official_date'], x['flight_real_date']), axis=1)
        try:
            flights = pd.read_csv(DATA_FILE, encoding="utf-8")
            flights = pd.concat([flights, flight_df], axis=0)
            flights = flights.drop_duplicates()
            flights.to_csv(DATA_FILE, index=False, encoding="utf-8")
            logger.info("Data Attached to Previous File.")
        except:
            flight_df.to_csv(DATA_FILE, index=False, encoding="utf-8")
            logger.info("A New File Created for Data!")


if __name__ == "__main__":
    scraper = FlightScraper()
    status = scraper.scrape_flights()
    if status:
        scraper.save_to_csv()

time.sleep(3)
