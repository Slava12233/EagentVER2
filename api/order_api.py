#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API להזמנות בחנות WooCommerce
-----------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על הזמנות בחנות.
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

def get_order_by_id(order_id):
    """
    מחזיר הזמנה לפי מזהה.
    
    Args:
        order_id: מזהה ההזמנה
    
    Returns:
        ההזמנה שנמצאה
    """
    client = get_woocommerce_client()
    return client.get_order(order_id)

def get_orders_by_search(search_term, **params):
    """
    מחזיר הזמנות לפי חיפוש.
    
    Args:
        search_term: מונח חיפוש
        **params: פרמטרים נוספים
    
    Returns:
        ההזמנות שנמצאו
    """
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_orders(**params)

def get_all_orders(**params):
    """
    מחזיר את כל ההזמנות.
    
    Args:
        **params: פרמטרים לסינון
    
    Returns:
        כל ההזמנות שנמצאו
    """
    client = get_woocommerce_client()
    return client.get_orders(**params)

def create_new_order(data):
    """
    יוצר הזמנה חדשה.
    
    Args:
        data: נתוני ההזמנה
    
    Returns:
        ההזמנה שנוצרה
    """
    client = get_woocommerce_client()
    return client.create_order(data)

def update_existing_order(order_id, data):
    """
    מעדכן הזמנה קיימת.
    
    Args:
        order_id: מזהה ההזמנה
        data: נתוני ההזמנה לעדכון
    
    Returns:
        ההזמנה המעודכנת
    """
    client = get_woocommerce_client()
    return client.update_order(order_id, data)

def delete_existing_order(order_id, force=True):
    """
    מוחק הזמנה קיימת.
    
    Args:
        order_id: מזהה ההזמנה
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.delete_order(order_id, force)

def update_order_status(order_id, status):
    """
    מעדכן את הסטטוס של הזמנה.
    
    Args:
        order_id: מזהה ההזמנה
        status: הסטטוס החדש
    
    Returns:
        ההזמנה המעודכנת
    """
    client = get_woocommerce_client()
    return client.update_order(order_id, {"status": status})

def get_order_notes(order_id):
    """
    מחזיר את ההערות של הזמנה.
    
    Args:
        order_id: מזהה ההזמנה
    
    Returns:
        ההערות של ההזמנה
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"orders/{order_id}/notes").json()

def add_order_note(order_id, note, customer_note=False):
    """
    מוסיף הערה להזמנה.
    
    Args:
        order_id: מזהה ההזמנה
        note: תוכן ההערה
        customer_note: האם ההערה גלויה ללקוח (ברירת מחדל: False)
    
    Returns:
        ההערה שנוצרה
    """
    client = get_woocommerce_client()
    data = {
        "note": note,
        "customer_note": customer_note
    }
    return client.wcapi.post(f"orders/{order_id}/notes", data).json()

def get_order_refunds(order_id):
    """
    מחזיר את ההחזרים של הזמנה.
    
    Args:
        order_id: מזהה ההזמנה
    
    Returns:
        ההחזרים של ההזמנה
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"orders/{order_id}/refunds").json()

def create_order_refund(order_id, data):
    """
    יוצר החזר להזמנה.
    
    Args:
        order_id: מזהה ההזמנה
        data: נתוני ההחזר
    
    Returns:
        ההחזר שנוצר
    """
    client = get_woocommerce_client()
    return client.wcapi.post(f"orders/{order_id}/refunds", data).json()
