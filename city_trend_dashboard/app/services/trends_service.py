from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
from .db_service import collection

pytrends = TrendReq(hl='en-US', tz=330)

cities = {
    "Mumbai": "IN-MH",
    "Delhi": "IN-DL",
    "Bangalore": "IN-KA",
    "Hyderabad": "IN-TG",
    "Ahmedabad": "IN-GJ",
    "Chennai": "IN-TN",
    "Kolkata": "IN-WB",
    "Jaipur": "IN-RJ",
    "Lucknow": "IN-UP",
    "Bhopal": "IN-MP"
}

products = ["Mobile phones", "Footwear", "Jewellery",
            "Headphones", "Smartwatches", "Books"]

def fetch_and_store_trends():
    all_data = []
    for city, geo_code in cities.items():
        for product in products:
            pytrends.build_payload([product], timeframe='now 7-d', geo=geo_code)
            data = pytrends.interest_over_time()
            if not data.empty:
                data.reset_index(inplace=True)
                data.rename(columns={product: "trend_score"}, inplace=True)
                data['city'] = city
                data['product'] = product
                data['fetched_at'] = datetime.utcnow()
                data.drop(columns=['isPartial'], inplace=True)

                records = data.to_dict("records")
                collection.insert_many(records)
                all_data.extend(records)
    return {"inserted": len(all_data)}


def get_trends_for_city_product(city, product):
    # Query MongoDB for trends matching city and product
    results = list(collection.find({"city": city, "product": product}, {"_id": 0}))
    return results

def fetch_trends_for_city_product_timeframe(city, product, timeframe):
    geo_code = cities.get(city)
    if not geo_code:
        return []
    pytrends = TrendReq(hl='en-US', tz=330)
    pytrends.build_payload([product], timeframe=timeframe, geo=geo_code)
    data = pytrends.interest_over_time()
    if not data.empty:
        data.reset_index(inplace=True)
        data.rename(columns={product: "trend_score"}, inplace=True)
        data['city'] = city
        data['product'] = product
        data['fetched_at'] = datetime.utcnow()
        data.drop(columns=['isPartial'], inplace=True)
        return data.to_dict("records")
    return []