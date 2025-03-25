#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API לקופונים בחנות WooCommerce
-----------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על קופונים בחנות.
"""

from api.woocommerce_client import WooCommerceClient
from config import get_woocommerce_config

def get_woocommerce_client():
    """מחזיר מופע של WooCommerceClient."""
    config = get_woocommerce_config()
    return WooCommerceClient(
        url=config["url"],
        consumer_key=config["consumer_key"],
        consumer_secret=config["consumer_secret"]
    )

def get_coupon_by_id(coupon_id):
    """
    מחזיר קופון לפי מזהה.
    
    Args:
        coupon_id: מזהה הקופון
    
    Returns:
        הקופון שנמצא
    """
    client = get_woocommerce_client()
    return client.get_coupon(coupon_id)

def get_coupons_by_search(search_term, **params):
    """
    מחזיר קופונים לפי חיפוש.
    
    Args:
        search_term: מונח חיפוש
        **params: פרמטרים נוספים
    
    Returns:
        הקופונים שנמצאו
    """
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_coupons(**params)

def get_all_coupons(**params):
    """
    מחזיר את כל הקופונים.
    
    Args:
        **params: פרמטרים לסינון
    
    Returns:
        כל הקופונים שנמצאו
    """
    client = get_woocommerce_client()
    return client.get_coupons(**params)

def create_new_coupon(data):
    """
    יוצר קופון חדש.
    
    Args:
        data: נתוני הקופון
    
    Returns:
        הקופון שנוצר
    """
    client = get_woocommerce_client()
    return client.create_coupon(data)

def update_existing_coupon(coupon_id, data):
    """
    מעדכן קופון קיים.
    
    Args:
        coupon_id: מזהה הקופון
        data: נתוני הקופון לעדכון
    
    Returns:
        הקופון המעודכן
    """
    client = get_woocommerce_client()
    return client.update_coupon(coupon_id, data)

def delete_existing_coupon(coupon_id, force=True):
    """
    מוחק קופון קיים.
    
    Args:
        coupon_id: מזהה הקופון
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.delete_coupon(coupon_id, force)

def get_coupon_by_code(code):
    """
    מחזיר קופון לפי קוד.
    
    Args:
        code: קוד הקופון
    
    Returns:
        הקופון שנמצא, או None אם לא נמצא
    """
    client = get_woocommerce_client()
    coupons = client.get_coupons(code=code)
    
    if not coupons:
        return None
    
    return coupons[0]

def create_percentage_discount_coupon(code, amount, description="", expiry_date=None, **kwargs):
    """
    יוצר קופון הנחה באחוזים.
    
    Args:
        code: קוד הקופון
        amount: אחוז ההנחה
        description: תיאור הקופון (אופציונלי)
        expiry_date: תאריך תפוגה בפורמט YYYY-MM-DD (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקופון שנוצר
    """
    data = {
        "code": code,
        "discount_type": "percent",
        "amount": str(amount),
        "description": description,
        **kwargs
    }
    
    if expiry_date:
        data["date_expires"] = f"{expiry_date}T23:59:59"
    
    return create_new_coupon(data)

def create_fixed_discount_coupon(code, amount, description="", expiry_date=None, **kwargs):
    """
    יוצר קופון הנחה בסכום קבוע.
    
    Args:
        code: קוד הקופון
        amount: סכום ההנחה
        description: תיאור הקופון (אופציונלי)
        expiry_date: תאריך תפוגה בפורמט YYYY-MM-DD (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקופון שנוצר
    """
    data = {
        "code": code,
        "discount_type": "fixed_cart",
        "amount": str(amount),
        "description": description,
        **kwargs
    }
    
    if expiry_date:
        data["date_expires"] = f"{expiry_date}T23:59:59"
    
    return create_new_coupon(data)
