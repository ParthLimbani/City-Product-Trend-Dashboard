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