#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API ללקוחות בחנות WooCommerce
-----------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על לקוחות בחנות.
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

def get_customer_by_id(customer_id):
    """
    מחזיר לקוח לפי מזהה.
    
    Args:
        customer_id: מזהה הלקוח
    
    Returns:
        הלקוח שנמצא
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"customers/{customer_id}").json()

def get_customers_by_search(search_term, **params):
    """
    מחזיר לקוחות לפי חיפוש.
    
    Args:
        search_term: מונח חיפוש
        **params: פרמטרים נוספים
    
    Returns:
        הלקוחות שנמצאו
    """
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.wcapi.get("customers", params=params).json()

def get_all_customers(**params):
    """
    מחזיר את כל הלקוחות.
    
    Args:
        **params: פרמטרים לסינון
    
    Returns:
        כל הלקוחות שנמצאו
    """
    client = get_woocommerce_client()
    return client.wcapi.get("customers", params=params).json()

def create_new_customer(data):
    """
    יוצר לקוח חדש.
    
    Args:
        data: נתוני הלקוח
    
    Returns:
        הלקוח שנוצר
    """
    client = get_woocommerce_client()
    return client.wcapi.post("customers", data).json()

def update_existing_customer(customer_id, data):
    """
    מעדכן לקוח קיים.
    
    Args:
        customer_id: מזהה הלקוח
        data: נתוני הלקוח לעדכון
    
    Returns:
        הלקוח המעודכן
    """
    client = get_woocommerce_client()
    return client.wcapi.put(f"customers/{customer_id}", data).json()

def delete_existing_customer(customer_id, force=True):
    """
    מוחק לקוח קיים.
    
    Args:
        customer_id: מזהה הלקוח
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.wcapi.delete(f"customers/{customer_id}", params={"force": force}).json()

def get_customer_by_email(email):
    """
    מחזיר לקוח לפי כתובת אימייל.
    
    Args:
        email: כתובת האימייל של הלקוח
    
    Returns:
        הלקוח שנמצא, או None אם לא נמצא
    """
    client = get_woocommerce_client()
    customers = client.wcapi.get("customers", params={"email": email}).json()
    
    if not customers:
        return None
    
    return customers[0]

def get_customer_orders(customer_id, **params):
    """
    מחזיר את ההזמנות של לקוח.
    
    Args:
        customer_id: מזהה הלקוח
        **params: פרמטרים נוספים
    
    Returns:
        ההזמנות של הלקוח
    """
    client = get_woocommerce_client()
    params["customer"] = customer_id
    return client.wcapi.get("orders", params=params).json()

def get_customer_downloads(customer_id):
    """
    מחזיר את ההורדות של לקוח.
    
    Args:
        customer_id: מזהה הלקוח
    
    Returns:
        ההורדות של הלקוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"customers/{customer_id}/downloads").json()
