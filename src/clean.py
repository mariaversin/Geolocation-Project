from mongo import connectCollection
import pandas as pd
import numpy as np

db, coll = connectCollection('dbcompanies','companies') 
filter1 = [
    {"$match": {"$and":
            [{"founded_year": {"$gte": 2009}}, # Fundadas a partir del 2009
             {"deadpooled_year": None}, # Que no hayan quebrado
             {"offices.latitude": {"$exists": True, "$ne": None}}, # Que tengan latitud
             {"offices.longitude": {"$exists": True, "$ne": None}}]}}] # Que tengan longitud

offices = list(coll.aggregate(filter1))
def prepareData(bd):
    '''Function to clean data'''
    cleanedItems = []
    errors = 0
    for group in offices:
        for item in range(len(group['offices'])):
            try:
                cleanedItems.append({
                "name":group["name"],
                "employees": group['number_of_employees'],
                "year":group['founded_year'],
                "category":group['category_code'],
                "id":group['_id'],
                "money raised":group['total_money_raised'],
                "city" : group['offices'][item]['city'],
                "country" : group['offices'][item]['country_code'],
                "latitude" : group['offices'][item]['latitude'],
                "longitude" : group['offices'][item]['longitude'],
                "coordinates":{
                    "type":"Point",
                    "coordinates":[group['offices'][item]['longitude'],group['offices'][item]['latitude']]}})
            except Exception:
                errors += 1
                if errors > 0:
                    print(f"Hay {errors} errores")
    return cleanedItems

def money_clean(data):
    
    ''' Function to convert money raised to int '''
    data = pd.DataFrame(prepareData(offices))
    data['money raised']= data['money raised'].replace('[Kk]', '*100',regex = True).replace( 'M', '*1000000',regex=True)
    data['money raised']= data['money raised'].replace('[€$£]','',regex=True)
    #data['money raised']= data['money raised'].apply(np.int64)
    data['money raised']= data['money raised'].map(pd.eval)
    data=data[data!=0].dropna()
    return data

def category(data):
    
    ''' Function to clean category column '''
    
    web_design = {'search': 'web','mobile': 'web','web': 'web','games_video': 'web','ecommerce': 'web','advertising': 'web',
              'hardware': 'web','enterprise': 'web','network_hosting': 'web','software': 'web',
              'analytics': 'web','cleantech': 'web','design': 'web', 'photo_video': 'web', 'security':'web','biotech':'web','messaging':'web'}
    data = money_clean(data).replace(web_design, regex=True)
    data_new = data[data['category']== 'web']
    return data_new

def near(geo_point, radio_meters):

    """ Function to find near companies"""

    geopoint = geo_point
    return list(db.companies_clean.find({
    "coordinates.coordinates": {
        "$near": {
            "$geometry": geopoint,
            "$maxDistance": radio_meters
        }}})) 

def drop_columns(data,columns):
    data.drop(columns, axis=1 ,inplace=True)
    return data
