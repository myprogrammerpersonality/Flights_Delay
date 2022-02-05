import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

URL = "https://fids.airport.ir/2/%D8%A7%D8%B7%D9%84%D8%A7%D8%B9%D8%A7%D8%AA-%D9%BE%D8%B1%D9%88%D8%A7%D8%B2-%D9%81%D8%B1%D9%88%D8%AF%DA%AF%D8%A7%D9%87-%D9%85%D9%87%D8%B1%D8%A2%D8%A8%D8%A7%D8%AF"
page = requests.get(URL)
print("Fetched")

soup = BeautifulSoup(page.content, "html.parser")

def process_input(bs4_object):
    try:
        return bs4_object.text.strip()
    except AttributeError:
        return None
    
def calc_delay(formal_time, real_time):
    if not formal_time or not real_time:
        return None
    else:
        formal_datetime = datetime.strptime(formal_time[-5:], '%H:%M')
        real_datetime = datetime.strptime(real_time[-5:], '%H:%M')
        return abs((real_datetime - formal_datetime).total_seconds() // 60)
    
    
job_elements = soup.find_all("tr", class_="status-default")
flight_list = [] 
for flight in job_elements:
    flight_destination = process_input(flight.find("td", class_="cell-dest"))
    flight_origin = process_input(flight.find("td", class_="cell-orig"))
    flight_airline = process_input(flight.find("td", class_="cell-airline"))
    flight_day = process_input(flight.find("td", class_="cell-day"))
    flight_no = process_input(flight.find("td", class_="cell-fno"))
    flight_status = process_input(flight.find("td", class_="cell-status"))
    flight_date = process_input(flight.find("td", class_="cell-date"))
    flight_real_date = process_input(flight.find("td", class_="cell-dateTime2"))
    
    flight_dict =  {"flight_destination" : flight_destination,
                    "flight_origin" : flight_origin,
                    "flight_airline" : flight_airline,
                    "flight_day" : flight_day,
                    "flight_no" : flight_no,
                    "flight_status" : flight_status,
                    "flight_date" : flight_date,
                    "flight_real_date" : flight_real_date,}
    flight_list.append(flight_dict)
    
flight_df = pd.DataFrame(flight_list)
flight_df = flight_df[flight_df.flight_status == "پرواز كرد"]
flight_df['delay_min'] = flight_df.apply(lambda x: calc_delay(x['flight_day'], x['flight_real_date']), axis=1)

try:
    flights = pd.read_csv("flights.csv")
    flights = pd.concat([flights, flight_df], axis=0)
    flights = flights.drop_duplicates()
    flights.to_csv("flights.csv", index=False)
    print("Attached")
except:
    flight_df.to_csv("flights.csv", index=False)
    print("Created")
