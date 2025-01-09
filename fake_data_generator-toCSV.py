import subprocess
import sys

# قائمة المكتبات المطلوبة
required_libraries = [
    "pandas",
    "faker",
    "faker_airtravel",
    "flatten_json",
    "numpy"
]
for library in required_libraries:
    try:
        __import__(library)
    except ImportError:
        print(f"Installing {library}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library])

"""
This script will generate fake data which can be used to demo DOT. See below
for code to generate each test type scenario. Script saves data to CSV files.
"""
import pandas as pd
from faker import Faker
from faker_airtravel import AirTravelProvider
from flatten_json import flatten
import numpy as np
from datetime import datetime
from datetime import timedelta
import random
import uuid



NUMBER_OF_FLIGHTS = 1000

np.random.seed(seed=12345)
Faker.seed(0)
fake = Faker()
# this is to seed the custom provider of airports for deterministic results
random.seed(10)

start_time = "01/01/2022 11:13:08.230010"
date_format_str = "%d/%m/%Y %H:%M:%S.%f"
flight_time = datetime.strptime(start_time, date_format_str)

fake.add_provider(AirTravelProvider)

flight_data = []
airport_data = []

# Generate data
for i in range(NUMBER_OF_FLIGHTS):
    flight_time = flight_time + timedelta(seconds=i * 10)
    f = flatten(fake.flight())
    f["departure_time"] = flight_time
    flight_data.append(f)
flight_data = pd.DataFrame(flight_data)

# Make SQL friendly
flight_data = flight_data.replace("'", "''", regex=True)
airport_data = flight_data[["origin_airport", "origin_iata"]].drop_duplicates()

print("Adding test fail scenarios to generated data ...")
print("Adding a broken relationship ...")
# Remove a row from airports so there isn't a relationship to it from flights
airport_data = airport_data.drop(3)

print("Adding unique value exception ...")
duplicate = airport_data.iloc[4]
airport_data = airport_data.append(duplicate)

print("Adding not negative exception ...")
flight_data.loc[2, "price"] = -100
airport_data = airport_data.append(duplicate)

print("Adding null values, and associated values not null, exceptions ...")
nan_mat = np.random.random(flight_data.shape) < 0.05
flight_data = flight_data.mask(nan_mat)

print("Adding accepted values exceptions ...")
flight_data.loc[6, "stops"] = 97

print("Adding duplicate forms (records) ...")
duplicate = flight_data.iloc[4]
flight_data = flight_data.append(duplicate)

print("Expect similar means across reporters (airlines) ...")
duplicate = flight_data.iloc[4]
flight_data.loc[flight_data["airline"] == "British Airways", "price"] = (
    0.1 * flight_data.loc[flight_data["airline"] == "British Airways", "price"]
)

flight_data = flight_data.reset_index(drop=True)
airport_data = airport_data.reset_index(drop=True)

# Save data to CSV
flight_data.to_csv('./dot/flight_data.csv', index=False)
airport_data.to_csv('./dot/airport_data.csv', index=False)

print("Data saved as CSV files:")
print("- flight_data.csv")
print("- airport_data.csv")
