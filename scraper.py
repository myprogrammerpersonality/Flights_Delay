import requests
from requests import RequestException
from bs4 import BeautifulSoup
import pandas as pd
from logger import Logger
import logging
import time
import json
from typing import List
from models import Flight
from utils import calc_delay

logger = Logger(__name__, loglevel=logging.INFO).get_logger()

with open("urls.json", "r", encoding="utf-8") as f:
    CITY_URL_MAPPING = json.load(f)

DATA_FILE = "C:/Users/aliyz/OneDrive/Desktop/Repos/Personal/Flights_Delay/flights.csv"

class FlightScraper:
    def __init__(self, url, city):
        self.url = url
        self.city = city
        self.flight_list: List[Flight] = []

    def _fetch_page_content(self):
        max_retries = 3
        for _ in range(max_retries):
            try:
                page = requests.get(self.url, timeout=10)
                page.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
                logger.info("Data Fetched Successfully.")
                return page.content
            except RequestException as e:
                logger.error(f"Attempt { _ + 1 }: Error fetching the page content: {e}")
                if _ < max_retries - 1:  # Only sleep if we are going to retry
                    time.sleep(1)  # Sleep for a second before trying again, this can be adjusted
                else:
                    logger.error("Max retries reached. Giving up.")
                    return None

    @staticmethod
    def _process_input(bs4_object, field_name):
        if not bs4_object:
            logger.warning(f"Encountered a None object for field '{field_name}' when trying to process input with bs4.")
            return None
        try:
            return bs4_object.text.strip()
        except AttributeError as e:
            logger.error(f"Error parsing the page with bs4: {e}")
            return None

    def _parse_flight_info(self, flight):
        return Flight(
            flight_origin=self.city,
            flight_destination=self._process_input(flight.find("td", class_="cell-dest"), "flight_destination"),
            flight_airline=self._process_input(flight.find("td", class_="cell-airline"), "flight_airline"),
            flight_official_date=self._process_input(flight.find("td", class_="cell-day"), "flight_official_date"),
            flight_number=self._process_input(flight.find("td", class_="cell-fno"), "flight_number"),
            flight_status=self._process_input(flight.find("td", class_="cell-status"), "flight_status"),
            flight_real_date=self._process_input(flight.find("td", class_="cell-dateTime2"), "flight_real_date"),
        )

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


if __name__ == "__main__":
    flights_list = []
    for city, url in list(CITY_URL_MAPPING.items()):
        scraper = FlightScraper(url=url, city=city)
        status = scraper.scrape_flights()
        if status:
            flights_list_temp = scraper.flight_list
        else:
            logger.warning(f"Data for {city} is empty!")
            flights_list_temp = []
        flights_list.extend(flights_list_temp)
        logger.info(f"Data for {city} Scraped Successfully!")
        time.sleep(0.2)
    flight_dicts = [flight.model_dump() for flight in flights_list]
    final_df = pd.DataFrame.from_records(flight_dicts)

    # Filter out not completed flights
    final_df = final_df.dropna(subset=["flight_real_date"])
    final_df = final_df[final_df["flight_status"] == 'پرواز كرد']

    if not final_df.empty:
        final_df["flight_delay"] = final_df.apply(lambda x: calc_delay(x["flight_official_date"], x["flight_real_date"]), axis=1)
    else:
        final_df["flight_delay"] = None

    try:
        flights = pd.read_csv(DATA_FILE, encoding="utf-8")
        flights = pd.concat([flights, final_df], axis=0)
        flights = flights.drop_duplicates()
        flights.to_csv(DATA_FILE, index=False, encoding="utf-8")
        logger.info("Data Attached to Previous File.")
    except FileNotFoundError:
        final_df.to_csv(DATA_FILE, index=False, encoding="utf-8")
        logger.info("A New File Created for Data!")   

time.sleep(3)
