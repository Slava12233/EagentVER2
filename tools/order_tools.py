#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול הזמנות בחנות WooCommerce
------------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent להזמנות יכול להשתמש בהם
כדי לבצע פעולות על הזמנות בחנות WooCommerce.
"""

from api.order_api import (
    get_order_by_id,
    get_orders_by_search,
    get_all_orders,
    create_new_order,
    update_existing_order,
    delete_existing_order,
    update_order_status,
    get_order_notes,
    add_order_note,
    get_order_refunds,
    create_order_refund
)

def get_order(order_id: str = None, search: str = None):
    """
    מחזיר מידע על הזמנה לפי מזהה או חיפוש.
    
    Args:
        order_id: מזהה ההזמנה (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על ההזמנה או ההזמנות שנמצאו
    """
    if order_id:
        return get_order_by_id(order_id)
    elif search:
        return get_orders_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה הזמנה או מונח חיפוש"}

def list_orders(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    status: str = None,
    customer: str = None,
    after: str = None,
    before: str = None,
    **kwargs
):
    """
    מחזיר רשימת הזמנות עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        status: סטטוס ההזמנה (אופציונלי)
        customer: מזהה הלקוח (אופציונלי)
        after: תאריך התחלה בפורמט ISO (אופציונלי)
        before: תאריך סיום בפורמט ISO (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        רשימת ההזמנות שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page,
        **kwargs
    }
    
    if search:
        params["search"] = search
    
    if status:
        params["status"] = status
    
    if customer:
        params["customer"] = customer
    
    if after:
        params["after"] = after
    
    if before:
        params["before"] = before
    
    return get_all_orders(**params)

def create_order(
    payment_method: str,
    payment_method_title: str,
    customer_id: int = 0,
    line_items: list = None,
    shipping_lines: list = None,
    billing: dict = None,
    shipping: dict = None,
    **kwargs
):
    """
    יוצר הזמנה חדשה.
    
    Args:
        payment_method: שיטת התשלום
        payment_method_title: כותרת שיטת התשלום
        customer_id: מזהה הלקוח (ברירת מחדל: 0 - אורח)
        line_items: פריטי ההזמנה (אופציונלי)
        shipping_lines: פריטי המשלוח (אופציונלי)
        billing: פרטי חיוב (אופציונלי)
        shipping: פרטי משלוח (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        ההזמנה שנוצרה
    """
    data = {
        "payment_method": payment_method,
        "payment_method_title": payment_method_title,
        "customer_id": customer_id,
        **kwargs
    }
    
    if line_items:
        data["line_items"] = line_items
    
    if shipping_lines:
        data["shipping_lines"] = shipping_lines
    
    if billing:
        data["billing"] = billing
    
    if shipping:
        data["shipping"] = shipping
    
    return create_new_order(data)

def update_order(
    order_id: str,
    **kwargs
):
    """
    מעדכן הזמנה קיימת.
    
    Args:
        order_id: מזהה ההזמנה
        **kwargs: פרמטרים לעדכון
    
    Returns:
        ההזמנה המעודכנת
    """
    return update_existing_order(order_id, kwargs)

def delete_order(order_id: str, force: bool = True):
    """
    מוחק הזמנה מהחנות.
    
    Args:
        order_id: מזהה ההזמנה
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_order(order_id, force)

def update_status(order_id: str, status: str):
    """
    מעדכן את הסטטוס של הזמנה.
    
    Args:
        order_id: מזהה ההזמנה
        status: הסטטוס החדש
    
    Returns:
        ההזמנה המעודכנת
    """
    return update_order_status(order_id, status)

def get_notes(order_id: str):
    """
    מחזיר את ההערות של הזמנה.
    
    Args:
        order_id: מזהה ההזמנה
    
    Returns:
        ההערות של ההזמנה
    """
    return get_order_notes(order_id)

def add_note(order_id: str, note: str, customer_note: bool = False):
    """
    מוסיף הערה להזמנה.
    
    Args:
        order_id: מזהה ההזמנה
        note: תוכן ההערה
        customer_note: האם ההערה גלויה ללקוח (ברירת מחדל: False)
    
    Returns:
        ההערה שנוצרה
    """
    return add_order_note(order_id, note, customer_note)

def get_refunds(order_id: str):
    """
    מחזיר את ההחזרים של הזמנה.
    
    Args:
        order_id: מזהה ההזמנה
    
    Returns:
        ההחזרים של ההזמנה
    """
    return get_order_refunds(order_id)

def create_refund(
    order_id: str,
    amount: float = None,
    reason: str = "",
    line_items: list = None,
    api_refund: bool = True
):
    """
    יוצר החזר להזמנה.
    
    Args:
        order_id: מזהה ההזמנה
        amount: סכום ההחזר (אופציונלי)
        reason: סיבת ההחזר (אופציונלי)
        line_items: פריטים להחזר (אופציונלי)
        api_refund: האם לבצע החזר דרך ה-API של שער התשלום (ברירת מחדל: True)
    
    Returns:
        ההחזר שנוצר
    """
    data = {
        "reason": reason,
        "api_refund": api_refund
    }
    
    if amount is not None:
        data["amount"] = str(amount)
    
    if line_items:
        data["line_items"] = line_items
    
    return create_order_refund(order_id, data)
