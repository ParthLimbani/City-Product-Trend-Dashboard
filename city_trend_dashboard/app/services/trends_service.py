def get_related_queries(city, product):
    geo_code = cities.get(city)
    dummy = {
        "top": [
            {"query": f"{product} features", "value": 100},
            {"query": f"{product} price in {city}", "value": 90},
            {"query": f"{product} reviews", "value": 80},
        ],
        "rising": [
            {"query": f"Best {product} 2025", "value": 200},
            {"query": f"{product} offers in {city}", "value": 150},
        ]
    }
    if not geo_code:
        return dummy
    retry_count = 0
    while retry_count < 3:
        try:
            pytrends.build_payload([product], timeframe='today 3-m', geo=geo_code)
            related = pytrends.related_queries()
            queries = related.get(product, {})
            def extract_records(df):
                if df is not None and not df.empty:
                    cols = [c for c in ['query', 'value'] if c in df.columns]
                    return df[cols].to_dict('records')
                return []
            result = {
                "top": extract_records(queries.get("top")),
                "rising": extract_records(queries.get("rising")),
            }
            if not result["top"] and not result["rising"]:
                return dummy
            return result
        except TooManyRequestsError:
            retry_count += 1
            wait_time = 60 * retry_count
            print(f"Rate limited by Google. Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error fetching related queries for {city}, {product}: {e}")
            return dummy
    return dummy

def get_related_topics(city, product):
    geo_code = cities.get(city)
    dummy = {
        "top": [
            {"topic_title": f"{product} Technology", "topic_mid": "mid1", "value": 100},
            {"topic_title": f"{product} Reviews", "topic_mid": "mid2", "value": 85},
            {"topic_title": f"{product} Price", "topic_mid": "mid3", "value": 70},
        ],
        "rising": [
            {"topic_title": f"Best {product} in {city}", "topic_mid": "mid4", "value": 200},
            {"topic_title": f"{product} Offers", "topic_mid": "mid5", "value": 150},
        ]
    }
    if not geo_code:
        return dummy
    retry_count = 0
    while retry_count < 3:
        try:
            pytrends.build_payload([product], timeframe='today 3-m', geo=geo_code)
            related = pytrends.related_topics()
            topics = related.get(product, {})
            def extract_records(df):
                if df is not None and not df.empty:
                    cols = [c for c in ['topic_title', 'topic_mid', 'value'] if c in df.columns]
                    return df[cols].to_dict('records')
                return []
            result = {
                "top": extract_records(topics.get("top")),
                "rising": extract_records(topics.get("rising")),
            }
            # If both are empty, return dummy
            if not result["top"] and not result["rising"]:
                return dummy
            return result
        except TooManyRequestsError:
            retry_count += 1
            wait_time = 60 * retry_count
            print(f"Rate limited by Google. Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error fetching related topics for {city}, {product}: {e}")
            return dummy
    return dummy

def get_interest_by_region(city, product):
    geo_code = cities.get(city)
    dummy = [
        {"region": f"{city} Central", "trend_score": 90},
        {"region": f"{city} North", "trend_score": 75},
        {"region": f"{city} South", "trend_score": 60},
        {"region": f"{city} East", "trend_score": 55},
        {"region": f"{city} West", "trend_score": 45},
    ]
    if not geo_code:
        return dummy
    retry_count = 0
    while retry_count < 3:
        try:
            pytrends.build_payload([product], timeframe='today 3-m', geo=geo_code)
            region_df = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=True)
            if region_df is not None and not region_df.empty:
                region_df = region_df.reset_index()
                if product in region_df.columns:
                    region_df = region_df[[region_df.columns[0], product]]
                    region_df.columns = ['region', 'trend_score']
                    result = region_df.to_dict('records')
                    if not result:
                        return dummy
                    return result
            return dummy
        except TooManyRequestsError:
            retry_count += 1
            wait_time = 60 * retry_count
            print(f"Rate limited by Google. Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error fetching interest by region for {city}, {product}: {e}")
            return dummy
    return dummy
def get_90_days_trend_with_analysis(city, product, window=7):
    """
    Fetch 90 days of trend data for a city/product from live pytrends and perform moving average, ARIMA, and SARIMA analysis.
    Returns a list of dicts with date, trend_score, moving_average, arima_pred, and sarima_pred.
    """
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    import numpy as np
    geo_code = cities.get(city)
    if not geo_code:
        return []
    retry_count = 0
    while retry_count < 3:
        try:
            pytrends.build_payload([product], timeframe='today 3-m', geo=geo_code)
            data = pytrends.interest_over_time()
            if data.empty:
                return []
            data.reset_index(inplace=True)
            data.rename(columns={product: "trend_score"}, inplace=True)
            # Use 'date' as index for time series
            data["date"] = pd.to_datetime(data["date"])
            df = data.set_index("date")
            df = df[["trend_score"]]
            # Fill missing days if any
            df = df.resample("D").mean().fillna(method="ffill")
            df = df.tail(90)
            # Calculate moving average
            df["moving_average"] = df["trend_score"].rolling(window=window, min_periods=1).mean()
            # ARIMA model (simple, order can be tuned)
            try:
                arima_model = ARIMA(df["trend_score"], order=(2,1,2))
                arima_fit = arima_model.fit()
                df["arima_pred"] = arima_fit.predict(start=0, end=len(df)-1, typ="levels")
            except Exception as e:
                df["arima_pred"] = np.nan
            # SARIMA model (simple, order can be tuned)
            try:
                sarima_model = SARIMAX(df["trend_score"], order=(1,1,1), seasonal_order=(1,1,1,7))
                sarima_fit = sarima_model.fit(disp=False)
                df["sarima_pred"] = sarima_fit.predict(start=0, end=len(df)-1, typ="levels")
            except Exception as e:
                df["sarima_pred"] = np.nan
            # Prepare output
            output = [
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "trend_score": float(row["trend_score"]),
                    "moving_average": float(row["moving_average"]),
                    "arima_pred": float(row["arima_pred"]) if not pd.isna(row["arima_pred"]) else None,
                    "sarima_pred": float(row["sarima_pred"]) if not pd.isna(row["sarima_pred"]) else None
                }
                for d, row in df.iterrows()
            ]
            return output
        except TooManyRequestsError:
            retry_count += 1
            wait_time = 60 * retry_count
            print(f"Rate limited by Google. Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error fetching 90 days trends for {city}, {product}: {e}")
            return []
    return []

from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime
from .db_service import collection
import time
from pytrends.exceptions import TooManyRequestsError

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
            retry_count = 0
            while retry_count < 3:
                try:
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
                    time.sleep(2)  # polite delay between requests
                    break
                except TooManyRequestsError:
                    retry_count += 1
                    wait_time = 60 * retry_count
                    print(f"Rate limited by Google. Sleeping for {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"Error fetching trends for {city}, {product}: {e}")
                    break
    return {"inserted": len(all_data)}


def get_trends_for_city_product(city, product):
    # Query MongoDB for trends matching city and product
    results = list(collection.find({"city": city, "product": product}, {"_id": 0}))
    return results

def fetch_trends_for_city_product_timeframe(city, product, timeframe):
    geo_code = cities.get(city)
    if not geo_code:
        return []
    retry_count = 0
    while retry_count < 3:
        try:
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
        except TooManyRequestsError:
            retry_count += 1
            wait_time = 60 * retry_count
            print(f"Rate limited by Google. Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error fetching trends for {city}, {product}: {e}")
            return []
    return []