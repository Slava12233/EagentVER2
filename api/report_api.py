#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API לדוחות בחנות WooCommerce
---------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על דוחות בחנות.
"""

from api.woocommerce_client import WooCommerceClient
from config import get_woocommerce_config
from datetime import datetime, timedelta

def get_woocommerce_client():
    """מחזיר מופע של WooCommerceClient."""
    config = get_woocommerce_config()
    return WooCommerceClient(
        url=config["url"],
        consumer_key=config["consumer_key"],
        consumer_secret=config["consumer_secret"]
    )

def get_sales_report(period="week", date_min=None, date_max=None):
    """
    מחזיר דוח מכירות.
    
    Args:
        period: תקופת הדוח (day, week, month, year)
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח המכירות
    """
    client = get_woocommerce_client()
    params = {"period": period}
    
    if date_min:
        params["date_min"] = date_min
    
    if date_max:
        params["date_max"] = date_max
    
    return client.wcapi.get("reports/sales", params=params).json()

def get_top_sellers_report(period="week", date_min=None, date_max=None):
    """
    מחזיר דוח מוצרים מובילים.
    
    Args:
        period: תקופת הדוח (day, week, month, year)
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח המוצרים המובילים
    """
    client = get_woocommerce_client()
    params = {"period": period}
    
    if date_min:
        params["date_min"] = date_min
    
    if date_max:
        params["date_max"] = date_max
    
    return client.wcapi.get("reports/top_sellers", params=params).json()

def get_orders_report(period="week", date_min=None, date_max=None):
    """
    מחזיר דוח הזמנות.
    
    Args:
        period: תקופת הדוח (day, week, month, year)
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח ההזמנות
    """
    client = get_woocommerce_client()
    params = {"period": period}
    
    if date_min:
        params["date_min"] = date_min
    
    if date_max:
        params["date_max"] = date_max
    
    return client.wcapi.get("reports/orders/totals", params=params).json()

def get_customers_report():
    """
    מחזיר דוח לקוחות.
    
    Returns:
        דוח הלקוחות
    """
    client = get_woocommerce_client()
    return client.wcapi.get("reports/customers/totals").json()

def get_coupons_report():
    """
    מחזיר דוח קופונים.
    
    Returns:
        דוח הקופונים
    """
    client = get_woocommerce_client()
    return client.wcapi.get("reports/coupons/totals").json()

def get_stock_report():
    """
    מחזיר דוח מלאי.
    
    Returns:
        דוח המלאי
    """
    client = get_woocommerce_client()
    return client.wcapi.get("reports/stock").json()

def get_low_stock_report(limit=10):
    """
    מחזיר דוח מוצרים במלאי נמוך.
    
    Args:
        limit: מספר המוצרים להחזרה
    
    Returns:
        דוח המוצרים במלאי נמוך
    """
    client = get_woocommerce_client()
    
    # קבלת כל המוצרים
    products = client.get_products(per_page=100, stock_status="instock")
    
    # מיון המוצרים לפי כמות במלאי
    products_with_stock = [p for p in products if p.get("stock_quantity") is not None]
    low_stock_products = sorted(products_with_stock, key=lambda p: p.get("stock_quantity", 0))
    
    return low_stock_products[:limit]

def get_out_of_stock_report():
    """
    מחזיר דוח מוצרים שאזלו מהמלאי.
    
    Returns:
        דוח המוצרים שאזלו מהמלאי
    """
    client = get_woocommerce_client()
    return client.get_products(per_page=100, stock_status="outofstock")

def get_revenue_by_date_range(date_min, date_max):
    """
    מחזיר דוח הכנסות לפי טווח תאריכים.
    
    Args:
        date_min: תאריך התחלה בפורמט YYYY-MM-DD
        date_max: תאריך סיום בפורמט YYYY-MM-DD
    
    Returns:
        דוח ההכנסות
    """
    client = get_woocommerce_client()
    params = {
        "date_min": date_min,
        "date_max": date_max,
        "period": "custom"
    }
    
    return client.wcapi.get("reports/sales", params=params).json()

def get_revenue_by_product(product_id, date_min=None, date_max=None):
    """
    מחזיר דוח הכנסות לפי מוצר.
    
    Args:
        product_id: מזהה המוצר
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח ההכנסות למוצר
    """
    client = get_woocommerce_client()
    
    # קבלת כל ההזמנות
    params = {"per_page": 100, "status": "completed"}
    
    if date_min:
        params["after"] = f"{date_min}T00:00:00"
    
    if date_max:
        params["before"] = f"{date_max}T23:59:59"
    
    orders = client.get_orders(**params)
    
    # חישוב ההכנסות למוצר
    revenue = 0
    quantity = 0
    
    for order in orders:
        for item in order.get("line_items", []):
            if item.get("product_id") == product_id:
                revenue += float(item.get("total", 0))
                quantity += item.get("quantity", 0)
    
    return {
        "product_id": product_id,
        "revenue": revenue,
        "quantity": quantity,
        "date_min": date_min,
        "date_max": date_max
    }

def get_revenue_by_category(category_id, date_min=None, date_max=None):
    """
    מחזיר דוח הכנסות לפי קטגוריה.
    
    Args:
        category_id: מזהה הקטגוריה
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח ההכנסות לקטגוריה
    """
    client = get_woocommerce_client()
    
    # קבלת כל המוצרים בקטגוריה
    products = client.get_products(per_page=100, category=category_id)
    
    # קבלת כל ההזמנות
    params = {"per_page": 100, "status": "completed"}
    
    if date_min:
        params["after"] = f"{date_min}T00:00:00"
    
    if date_max:
        params["before"] = f"{date_max}T23:59:59"
    
    orders = client.get_orders(**params)
    
    # חישוב ההכנסות לקטגוריה
    revenue = 0
    quantity = 0
    product_ids = [p.get("id") for p in products]
    
    for order in orders:
        for item in order.get("line_items", []):
            if item.get("product_id") in product_ids:
                revenue += float(item.get("total", 0))
                quantity += item.get("quantity", 0)
    
    return {
        "category_id": category_id,
        "revenue": revenue,
        "quantity": quantity,
        "date_min": date_min,
        "date_max": date_max
    }
