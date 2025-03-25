#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול מוצרים בחנות WooCommerce
--------------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent למוצרים יכול להשתמש בהם
כדי לבצע פעולות על מוצרים בחנות WooCommerce.
"""

from api.product_api import (
    get_product_by_id,
    get_products_by_search,
    get_all_products,
    create_new_product,
    update_existing_product,
    delete_existing_product,
    update_product_stock,
    update_product_price,
    update_product_images,
    update_product_variations
)

def get_product(product_id: str = None, search: str = None):
    """
    מחזיר מידע על מוצר לפי מזהה או חיפוש.
    
    Args:
        product_id: מזהה המוצר (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על המוצר או המוצרים שנמצאו
    """
    if product_id:
        return get_product_by_id(product_id)
    elif search:
        return get_products_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה מוצר או מונח חיפוש"}

def list_products(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    category: str = None,
    tag: str = None,
    status: str = None,
    stock_status: str = None,
    on_sale: bool = None
):
    """
    מחזיר רשימת מוצרים עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        category: קטגוריה (אופציונלי)
        tag: תגית (אופציונלי)
        status: סטטוס המוצר (אופציונלי)
        stock_status: סטטוס המלאי (אופציונלי)
        on_sale: האם המוצר במבצע (אופציונלי)
    
    Returns:
        רשימת המוצרים שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if search:
        params["search"] = search
    
    if category:
        params["category"] = category
    
    if tag:
        params["tag"] = tag
    
    if status:
        params["status"] = status
    
    if stock_status:
        params["stock_status"] = stock_status
    
    if on_sale is not None:
        params["on_sale"] = on_sale
    
    return get_all_products(**params)

def create_product(
    name: str,
    regular_price: str,
    description: str = "",
    short_description: str = "",
    categories: list = None,
    tags: list = None,
    images: list = None,
    attributes: list = None,
    **kwargs
):
    """
    יוצר מוצר חדש בחנות.
    
    Args:
        name: שם המוצר
        regular_price: מחיר רגיל
        description: תיאור מלא (אופציונלי)
        short_description: תיאור קצר (אופציונלי)
        categories: רשימת קטגוריות (אופציונלי)
        tags: רשימת תגיות (אופציונלי)
        images: רשימת תמונות (אופציונלי)
        attributes: רשימת מאפיינים (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        המוצר שנוצר
    """
    data = {
        "name": name,
        "regular_price": regular_price,
        "description": description,
        "short_description": short_description,
        **kwargs
    }
    
    if categories:
        data["categories"] = categories
    
    if tags:
        data["tags"] = tags
    
    if images:
        data["images"] = images
    
    if attributes:
        data["attributes"] = attributes
    
    return create_new_product(data)

def update_product(
    product_id: str,
    **kwargs
):
    """
    מעדכן מוצר קיים בחנות.
    
    Args:
        product_id: מזהה המוצר
        **kwargs: פרמטרים לעדכון
    
    Returns:
        המוצר המעודכן
    """
    return update_existing_product(product_id, kwargs)

def delete_product(product_id: str, force: bool = True):
    """
    מוחק מוצר מהחנות.
    
    Args:
        product_id: מזהה המוצר
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_product(product_id, force)

def update_stock(
    product_id: str,
    stock_quantity: int,
    stock_status: str = None
):
    """
    מעדכן את המלאי של מוצר.
    
    Args:
        product_id: מזהה המוצר
        stock_quantity: כמות המלאי
        stock_status: סטטוס המלאי (אופציונלי)
    
    Returns:
        המוצר המעודכן
    """
    data = {
        "stock_quantity": stock_quantity
    }
    
    if stock_status:
        data["stock_status"] = stock_status
    
    return update_product_stock(product_id, data)

def update_price(
    product_id: str,
    regular_price: str = None,
    sale_price: str = None
):
    """
    מעדכן את המחיר של מוצר.
    
    Args:
        product_id: מזהה המוצר
        regular_price: מחיר רגיל (אופציונלי)
        sale_price: מחיר מבצע (אופציונלי)
    
    Returns:
        המוצר המעודכן
    """
    data = {}
    
    if regular_price:
        data["regular_price"] = regular_price
    
    if sale_price:
        data["sale_price"] = sale_price
    
    return update_product_price(product_id, data)

def manage_images(
    product_id: str,
    images: list
):
    """
    מנהל את התמונות של מוצר.
    
    Args:
        product_id: מזהה המוצר
        images: רשימת תמונות
    
    Returns:
        המוצר המעודכן
    """
    return update_product_images(product_id, {"images": images})

def manage_variations(
    product_id: str,
    variations: list
):
    """
    מנהל את הוריאציות של מוצר.
    
    Args:
        product_id: מזהה המוצר
        variations: רשימת וריאציות
    
    Returns:
        המוצר המעודכן
    """
    return update_product_variations(product_id, {"variations": variations})
