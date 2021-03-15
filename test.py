import requests
from faceit_data import FaceitData

faceit_data = FaceitData("0b0395d8-a3ad-404c-a3ef-80fd9c64b79b")
match_details = faceit_data.match_details("1-1034fae1-4092-4c34-a16a-e6c596b0fb42")
for k, v in match_details.items():
    print("{}: {}".format(k, v))
