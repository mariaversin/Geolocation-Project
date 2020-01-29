from constants import places, groups
from mongo import connectCollection
import pandas as pd
import numpy as np
import pprint
import re
import functions as f
import clean as c


db, coll = connectCollection('companies','companies_clean')
companies = db.companies_clean.find({ 
    "money_raised":{
        "$gte": 1000000
    }}) 

data_companies = pd.DataFrame(companies)
geo_point = []
for loc in range(len(data_companies)):
    geo_point.append(data_companies.coordinates[loc]) 

def numberOffices(data_companies):
    number_offices = []
    list_offices=[]
    for i in range(len(data_companies)):
        num_offices =  c.near(geo_point[i], radio_meters=3000)
        list_offices.append(num_offices)
        number_offices.append(len(num_offices))
    data_companies['number offices near'] = number_offices
    return data_companies

data_companies = numberOffices(data_companies)
data = data_companies[data_companies['number offices near'] > 1]
data.to_csv('./best_companies.csv') 

geo = []
for coords in data_companies['coordinates']:
    geo.append(coords['coordinates'])

# Hacemos las requests a todas las coordenadas,
# y de los 4 criterios que necesitamos -starbucks, airports, school y party-
info = []
for coord in geo:
    for place, value in places.items():
        try:
            request = (f.getNearby(coord[1],coord[0],value['api'],value['distance']))
            info.append(request)
        except:
            Exception: "Ha habido problemas con {}".format(place)

data = pd.DataFrame(f.curateResponse(info))
data["category"] = data.name.apply(f.chooseCat)




