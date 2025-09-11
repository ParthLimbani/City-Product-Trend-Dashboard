from fastapi import APIRouter, Query
from app.services.trends_service import cities, products, fetch_trends_for_city_product_timeframe
from app.services.db_service import collection

router = APIRouter()

@router.get("/cities")
def get_cities():
    return list(cities.keys())

@router.get("/products")
def get_products():
    return products

@router.get("/timeframes")
def get_timeframes():
    return [
        {"label": "Last 4 hours", "value": "now 4-H"},
        {"label": "Last day", "value": "now 1-d"},
        {"label": "Last 7 days", "value": "now 7-d"},
        {"label": "Last 30 days", "value": "today 1-m"},
        {"label": "Last 90 days", "value": "today 3-m"},
        {"label": "Last 12 months", "value": "today 12-m"},
        {"label": "Last 5 years", "value": "today 5-y"}
    ]

@router.get("/")
def get_trends(
    city: str = Query(None),
    product: str = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    timeframe: str = Query("now 7-d")
):
    if city and product and timeframe:
        return fetch_trends_for_city_product_timeframe(city, product, timeframe)
    query = {}
    if city:
        query["city"] = {"$regex": f"^{city}$", "$options": "i"}
    if product:
        query["product"] = {"$regex": f"^{product}$", "$options": "i"}
    data = list(collection.find(query, {"_id": 0}).limit(limit))
    return data