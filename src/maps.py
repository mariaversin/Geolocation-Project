from mongo import connectCollection
import requests
import pprint
import pandas as pd
import json
import folium
from folium import plugins
from folium.plugins import MarkerCluster
from constants import *
import clean as c

# Queries collection
db, coll = connectCollection('companies','queries')
queries = db.queries.find({ 
    "score":{
        "$lte": 4
    }})

locations = pd.DataFrame(queries)

map2 = folium.Map(location=[37.5579101647, -122.3221364075], tiles='CartoDB positron', zoom_start=11)

marker_cluster = folium.plugins.MarkerCluster().add_to(map2)

for index,row in locations.iterrows():
    folium.Marker(location=[row["latitude"], row["longitude"]],
                popup = [row['name']],
                icon=folium.Icon(color=colors[row['score']], icon = icons[row['category']],
                icon_color='white', angle=0, prefix='fa')).add_to(marker_cluster)


# Companies collection

db, coll2 = connectCollection('companies','best')
best = db.best.find({ 
    "category":{
        "$eq": 'web'
    }})

locations_comp = pd.DataFrame(best)
data = c.drop_columns(locations_comp,columns = ['coordinates','_id','id'])

for index,row in locations_comp.iterrows():
    folium.Marker(location=[row["latitude"], row["longitude"]],
                popup = [row['name']],
                icon=folium.Icon(color=colors2[row['number offices near']], icon = icons2[row['category']],
                icon_color='white', angle=0, prefix='fa')).add_to(marker_cluster)