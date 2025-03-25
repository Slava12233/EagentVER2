#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול דוחות בחנות WooCommerce
-----------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent לדוחות יכול להשתמש בהם
כדי לבצע פעולות על דוחות בחנות WooCommerce.
"""

from api.report_api import (
    get_sales_report,
    get_top_sellers_report,
    get_orders_report,
    get_customers_report,
    get_coupons_report,
    get_stock_report,
    get_low_stock_report,
    get_out_of_stock_report,
    get_revenue_by_date_range,
    get_revenue_by_product,
    get_revenue_by_category
)
from datetime import datetime, timedelta

def get_sales(period: str = "week", date_min: str = None, date_max: str = None):
    """
    מחזיר דוח מכירות.
    
    Args:
        period: תקופת הדוח (day, week, month, year)
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח המכירות
    """
    return get_sales_report(period, date_min, date_max)

def get_top_sellers(period: str = "week", date_min: str = None, date_max: str = None):
    """
    מחזיר דוח מוצרים מובילים.
    
    Args:
        period: תקופת הדוח (day, week, month, year)
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח המוצרים המובילים
    """
    return get_top_sellers_report(period, date_min, date_max)

def get_orders_total(period: str = "week", date_min: str = None, date_max: str = None):
    """
    מחזיר דוח הזמנות.
    
    Args:
        period: תקופת הדוח (day, week, month, year)
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח ההזמנות
    """
    return get_orders_report(period, date_min, date_max)

def get_customers_total():
    """
    מחזיר דוח לקוחות.
    
    Returns:
        דוח הלקוחות
    """
    return get_customers_report()

def get_coupons_total():
    """
    מחזיר דוח קופונים.
    
    Returns:
        דוח הקופונים
    """
    return get_coupons_report()

def get_stock():
    """
    מחזיר דוח מלאי.
    
    Returns:
        דוח המלאי
    """
    return get_stock_report()

def get_low_stock(limit: int = 10):
    """
    מחזיר דוח מוצרים במלאי נמוך.
    
    Args:
        limit: מספר המוצרים להחזרה
    
    Returns:
        דוח המוצרים במלאי נמוך
    """
    return get_low_stock_report(limit)

def get_out_of_stock():
    """
    מחזיר דוח מוצרים שאזלו מהמלאי.
    
    Returns:
        דוח המוצרים שאזלו מהמלאי
    """
    return get_out_of_stock_report()

def get_revenue_by_dates(date_min: str, date_max: str):
    """
    מחזיר דוח הכנסות לפי טווח תאריכים.
    
    Args:
        date_min: תאריך התחלה בפורמט YYYY-MM-DD
        date_max: תאריך סיום בפורמט YYYY-MM-DD
    
    Returns:
        דוח ההכנסות
    """
    return get_revenue_by_date_range(date_min, date_max)

def get_revenue_for_product(product_id: int, date_min: str = None, date_max: str = None):
    """
    מחזיר דוח הכנסות לפי מוצר.
    
    Args:
        product_id: מזהה המוצר
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח ההכנסות למוצר
    """
    return get_revenue_by_product(product_id, date_min, date_max)

def get_revenue_for_category(category_id: int, date_min: str = None, date_max: str = None):
    """
    מחזיר דוח הכנסות לפי קטגוריה.
    
    Args:
        category_id: מזהה הקטגוריה
        date_min: תאריך התחלה בפורמט YYYY-MM-DD (אופציונלי)
        date_max: תאריך סיום בפורמט YYYY-MM-DD (אופציונלי)
    
    Returns:
        דוח ההכנסות לקטגוריה
    """
    return get_revenue_by_category(category_id, date_min, date_max)

def get_daily_sales(days: int = 7):
    """
    מחזיר דוח מכירות יומי לתקופה מוגדרת.
    
    Args:
        days: מספר הימים לאחור (ברירת מחדל: 7)
    
    Returns:
        דוח המכירות היומי
    """
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    return get_sales_report("day", start_date, today)

def get_monthly_sales(months: int = 6):
    """
    מחזיר דוח מכירות חודשי לתקופה מוגדרת.
    
    Args:
        months: מספר החודשים לאחור (ברירת מחדל: 6)
    
    Returns:
        דוח המכירות החודשי
    """
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30*months)).strftime("%Y-%m-%d")
    
    return get_sales_report("month", start_date, today)

def get_yearly_sales(years: int = 3):
    """
    מחזיר דוח מכירות שנתי לתקופה מוגדרת.
    
    Args:
        years: מספר השנים לאחור (ברירת מחדל: 3)
    
    Returns:
        דוח המכירות השנתי
    """
    today = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365*years)).strftime("%Y-%m-%d")
    
    return get_sales_report("year", start_date, today)

def get_sales_summary():
    """
    מחזיר סיכום מכירות כללי.
    
    Returns:
        סיכום המכירות
    """
    # מכירות יומיות
    daily = get_daily_sales(7)
    
    # מכירות חודשיות
    monthly = get_monthly_sales(3)
    
    # מכירות שנתיות
    yearly = get_yearly_sales(1)
    
    # מוצרים מובילים
    top_sellers = get_top_sellers("month")
    
    # סיכום לקוחות
    customers = get_customers_total()
    
    return {
        "daily_sales": daily,
        "monthly_sales": monthly,
        "yearly_sales": yearly,
        "top_sellers": top_sellers,
        "customers": customers
    }

def get_inventory_summary():
    """
    מחזיר סיכום מלאי.
    
    Returns:
        סיכום המלאי
    """
    # מוצרים במלאי נמוך
    low_stock = get_low_stock(10)
    
    # מוצרים שאזלו מהמלאי
    out_of_stock = get_out_of_stock()
    
    return {
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "low_stock_count": len(low_stock),
        "out_of_stock_count": len(out_of_stock)
    }
