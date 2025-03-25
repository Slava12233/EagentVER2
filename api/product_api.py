#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API למוצרים בחנות WooCommerce
-----------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על מוצרים בחנות.
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

def get_product_by_id(product_id):
    """
    מחזיר מוצר לפי מזהה.
    
    Args:
        product_id: מזהה המוצר
    
    Returns:
        המוצר שנמצא
    """
    client = get_woocommerce_client()
    return client.get_product(product_id)

def get_products_by_search(search_term, **params):
    """
    מחזיר מוצרים לפי חיפוש.
    
    Args:
        search_term: מונח חיפוש
        **params: פרמטרים נוספים
    
    Returns:
        המוצרים שנמצאו
    """
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_products(**params)

def get_all_products(**params):
    """
    מחזיר את כל המוצרים.
    
    Args:
        **params: פרמטרים לסינון
    
    Returns:
        כל המוצרים שנמצאו
    """
    client = get_woocommerce_client()
    return client.get_products(**params)

def create_new_product(data):
    """
    יוצר מוצר חדש.
    
    Args:
        data: נתוני המוצר
    
    Returns:
        המוצר שנוצר
    """
    client = get_woocommerce_client()
    return client.create_product(data)

def update_existing_product(product_id, data):
    """
    מעדכן מוצר קיים.
    
    Args:
        product_id: מזהה המוצר
        data: נתוני המוצר לעדכון
    
    Returns:
        המוצר המעודכן
    """
    client = get_woocommerce_client()
    return client.update_product(product_id, data)

def delete_existing_product(product_id, force=True):
    """
    מוחק מוצר קיים.
    
    Args:
        product_id: מזהה המוצר
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.delete_product(product_id, force)

def update_product_stock(product_id, data):
    """
    מעדכן את המלאי של מוצר.
    
    Args:
        product_id: מזהה המוצר
        data: נתוני המלאי לעדכון
    
    Returns:
        המוצר המעודכן
    """
    client = get_woocommerce_client()
    return client.update_product(product_id, data)

def update_product_price(product_id, data):
    """
    מעדכן את המחיר של מוצר.
    
    Args:
        product_id: מזהה המוצר
        data: נתוני המחיר לעדכון
    
    Returns:
        המוצר המעודכן
    """
    client = get_woocommerce_client()
    return client.update_product(product_id, data)

def update_product_images(product_id, data):
    """
    מעדכן את התמונות של מוצר.
    
    Args:
        product_id: מזהה המוצר
        data: נתוני התמונות לעדכון
    
    Returns:
        המוצר המעודכן
    """
    client = get_woocommerce_client()
    return client.update_product(product_id, data)

def update_product_variations(product_id, data):
    """
    מעדכן את הוריאציות של מוצר.
    
    Args:
        product_id: מזהה המוצר
        data: נתוני הוריאציות לעדכון
    
    Returns:
        המוצר המעודכן
    """
    client = get_woocommerce_client()
    return client.update_product(product_id, data)
