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
data = pd.DataFrame(curateResponse(p))
groups= {
    "Coffee Shop": 'Starbucks',
    "Airport":['San Carlos Airport (SQL) (San Carlos Airport)',
                "Santa Monica Airport (SMO) (Santa Monica Airport)","London City Airport (LCY) (London City Airport)",
                "St. Petersburg - Clearwater International Airport (PIE)",
                "Stockholm-Bromma Airport (BMA) (Stockholm-Bromma Airport)",
                "San Francisco International Airport (SFO) (San Francisco International Airport)",
                "LaGuardia Airport (LGA) (LaGuardia Airport)"],
    "Bar":["Bar","Nightcub","Cocktail Bar","Pub","Plunge Rooftop Bar & Lounge","Audio Nightclub","Temple Nightclub",
            "Momofuku Ssäm Bar","Absinthe Brasserie & Bar","Cue Bar","Ritz Bar & Lounge"],
    "School": ["Petite Sorbonne Preschool","Trinity Preschool","Preschool of America","School","MS 297 Middle School",
               "Village Community School","Chelsea School","Public School 3","St. Matthew Catholic School",
              "De School Van Mieke Petiet","Goethe Instituut","Altra College","AltSchool",
               "Alta Vista School","Mission Montessori","Step by Step Early Childhood",
               "Grace Church School","Greenwich Village School","Santa Monica High School",
               "Stuyvesant High School","Norman Thomas High School","North Shoreview Montessori",
               "Highland Montessori","St. Timothy Catholic School","High Point Elementary School"],
    "Vegan": ["Thai Vegan ","Maoz Vegan" , "Urban Vegan Kitchen", "Golden Era Vegan", 
              "Vegan Junk Food Bar","Garden Fresh Vegan Cuisine ","Elovate Vegan Kitchen","Vegetarian Oasis","Maoz"]
}

def chooseCat(prod):
    for groupName, groupItems in groups.items():
        if prod in groupItems:
            return groupName
    return "OTHER"
data["category"] = data.name.apply(chooseCat)

# Puntuación en función de la distancia de cada categría:

