#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API לקטגוריות בחנות WooCommerce
------------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על קטגוריות בחנות.
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

def get_category_by_id(category_id):
    """
    מחזיר קטגוריה לפי מזהה.
    
    Args:
        category_id: מזהה הקטגוריה
    
    Returns:
        הקטגוריה שנמצאה
    """
    client = get_woocommerce_client()
    return client.get_category(category_id)

def get_categories_by_search(search_term, **params):
    """
    מחזיר קטגוריות לפי חיפוש.
    
    Args:
        search_term: מונח חיפוש
        **params: פרמטרים נוספים
    
    Returns:
        הקטגוריות שנמצאו
    """
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_categories(**params)

def get_all_categories(**params):
    """
    מחזיר את כל הקטגוריות.
    
    Args:
        **params: פרמטרים לסינון
    
    Returns:
        כל הקטגוריות שנמצאו
    """
    client = get_woocommerce_client()
    return client.get_categories(**params)

def create_new_category(data):
    """
    יוצר קטגוריה חדשה.
    
    Args:
        data: נתוני הקטגוריה
    
    Returns:
        הקטגוריה שנוצרה
    """
    client = get_woocommerce_client()
    return client.create_category(data)

def update_existing_category(category_id, data):
    """
    מעדכן קטגוריה קיימת.
    
    Args:
        category_id: מזהה הקטגוריה
        data: נתוני הקטגוריה לעדכון
    
    Returns:
        הקטגוריה המעודכנת
    """
    client = get_woocommerce_client()
    return client.update_category(category_id, data)

def delete_existing_category(category_id, force=True):
    """
    מוחק קטגוריה קיימת.
    
    Args:
        category_id: מזהה הקטגוריה
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.delete_category(category_id, force)

def get_category_by_slug(slug):
    """
    מחזיר קטגוריה לפי slug.
    
    Args:
        slug: ה-slug של הקטגוריה
    
    Returns:
        הקטגוריה שנמצאה, או None אם לא נמצאה
    """
    client = get_woocommerce_client()
    categories = client.get_categories(slug=slug)
    
    if not categories:
        return None
    
    return categories[0]

def get_category_by_name(name):
    """
    מחזיר קטגוריה לפי שם.
    
    Args:
        name: שם הקטגוריה
    
    Returns:
        הקטגוריה שנמצאה, או None אם לא נמצאה
    """
    client = get_woocommerce_client()
    categories = client.get_categories()
    
    for category in categories:
        if category.get("name") == name:
            return category
    
    return None

def get_subcategories(parent_id):
    """
    מחזיר את כל קטגוריות המשנה של קטגוריה.
    
    Args:
        parent_id: מזהה הקטגוריה האב
    
    Returns:
        קטגוריות המשנה
    """
    client = get_woocommerce_client()
    return client.get_categories(parent=parent_id)

def create_category_with_parent(name, parent_id, description="", **kwargs):
    """
    יוצר קטגוריית משנה.
    
    Args:
        name: שם הקטגוריה
        parent_id: מזהה קטגוריית האב
        description: תיאור הקטגוריה (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקטגוריה שנוצרה
    """
    data = {
        "name": name,
        "parent": parent_id,
        "description": description,
        **kwargs
    }
    
    return create_new_category(data)

def get_products_by_category(category_id, **params):
    """
    מחזיר את כל המוצרים בקטגוריה.
    
    Args:
        category_id: מזהה הקטגוריה
        **params: פרמטרים נוספים
    
    Returns:
        המוצרים בקטגוריה
    """
    client = get_woocommerce_client()
    params["category"] = category_id
    return client.get_products(**params)
