from constants import places
from mongo import connectCollection
import pandas as pd
import numpy as np
import requests
import pprint
import re
from dotenv import load_dotenv
load_dotenv()

db, coll = connectCollection('dbcompanies','companies_clean')
companies = db.companies_clean.find({ 
    "money_raised":{
        "$gte": 1000000
    }}) 

data_companies = pd.DataFrame(companies)
geo_point = []
for loc in range(len(data_companies)):
    geo_point.append(data_companies.coordinates[loc]) 

def near(geo_point, radio_meters):

    """ Function to find near companies"""

        geopoint = geo_point
        return list(db.companies_clean.find({
        "coordinates.coordinates": {
         "$near": {
             "$geometry": geopoint,
             "$maxDistance": radio_meters
         }}})) 

radio_meters = 5000
list_number_offices = []
list_offices=[]
for i in range(len(data_companies)):
    num_offices =  near(geo_point[i], radio_meters)
    list_offices.append(num_offices)
    list_number_offices.append(len(num_offices))
data_companies['offices near'] = list_number_offices
data_companies = data_companies[data_companies['offices near'] > 1]

geo = []
for coords in data_companies['coordinates']:
    geo.append(coords['coordinates'])

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

# Hacemos las requests a todas las coordenadas,
# y de los 4 criterios que necesitamos -starbucks, airports, school y party-
for coord in geo:
    for place, value in places.items():
        try:
            request = (getNearby(coord[1],coord[0],value['api'],value['distance']))
        except:
            Exception: "Ha habido problemas con {}".formate(place)
