import pandas as pd
import numpy as np
import os
import json
from dotenv import load_dotenv
load_dotenv()
import requests


def getNearby(lat,lng,query,radius):

    """ Function for queries """
    
    CLIENT_ID = os.getenv("client_id")
    CLIENT_SECRET = os.getenv("client_secret")
    url = 'https://api.foursquare.com/v2/venues/explore'
    queryParams = dict(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        v='20181023', # DONDE ESTOY
        ll=f"{lat},{lng}", #QUE QUIERO
        query=query, # A QUE DISTANCIA
        radius=radius
    )
    res = requests.get(url, params=queryParams)
    return res.json()

def curateResponse(data):
    """ Function for clean request and clean errors """
    places = []
    for item in data:
        try:
            for i in item["response"]["groups"][0]["items"]:
                if i["venue"]['location']['city'] != None:
                    places.append({
                        "name":i["venue"]['name'],
                        "distance": i["venue"]['location']["distance"],
                        "country": i["venue"]['location']["country"],
                        "city": i["venue"]['location']['city'],
                        "latitude": i["venue"]['location']["lat"],
                        "longitude": i["venue"]['location']["lng"],
                        "coordinates": {
                        "type":"Point",
                        "coordinates":[i["venue"]['location']["lng"], i["venue"]['location']["lat"]]
                            }})
        except:
            print(f"Ha ocurrido algún error.")
    return places

def chooseCat(prod):
    for groupName, groupItems in groups.items():
        if prod in groupItems:
            return groupName
    return "OTHER"