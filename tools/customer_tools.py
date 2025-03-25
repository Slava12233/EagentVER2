#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול לקוחות בחנות WooCommerce
------------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent ללקוחות יכול להשתמש בהם
כדי לבצע פעולות על לקוחות בחנות WooCommerce.
"""

from api.customer_api import (
    get_customer_by_id,
    get_customers_by_search,
    get_all_customers,
    create_new_customer,
    update_existing_customer,
    delete_existing_customer,
    get_customer_by_email,
    get_customer_orders,
    get_customer_downloads
)

def get_customer(customer_id: str = None, email: str = None, search: str = None):
    """
    מחזיר מידע על לקוח לפי מזהה, אימייל או חיפוש.
    
    Args:
        customer_id: מזהה הלקוח (אופציונלי)
        email: כתובת האימייל של הלקוח (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על הלקוח או הלקוחות שנמצאו
    """
    if customer_id:
        return get_customer_by_id(customer_id)
    elif email:
        return get_customer_by_email(email)
    elif search:
        return get_customers_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה לקוח, כתובת אימייל או מונח חיפוש"}

def list_customers(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    email: str = None,
    role: str = None,
    **kwargs
):
    """
    מחזיר רשימת לקוחות עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        email: כתובת אימייל (אופציונלי)
        role: תפקיד הלקוח (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        רשימת הלקוחות שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page,
        **kwargs
    }
    
    if search:
        params["search"] = search
    
    if email:
        params["email"] = email
    
    if role:
        params["role"] = role
    
    return get_all_customers(**params)

def create_customer(
    email: str,
    first_name: str = "",
    last_name: str = "",
    username: str = None,
    password: str = None,
    **kwargs
):
    """
    יוצר לקוח חדש.
    
    Args:
        email: כתובת האימייל של הלקוח
        first_name: שם פרטי (אופציונלי)
        last_name: שם משפחה (אופציונלי)
        username: שם משתמש (אופציונלי)
        password: סיסמה (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הלקוח שנוצר
    """
    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        **kwargs
    }
    
    if username:
        data["username"] = username
    
    if password:
        data["password"] = password
    
    return create_new_customer(data)

def update_customer(
    customer_id: str,
    **kwargs
):
    """
    מעדכן לקוח קיים.
    
    Args:
        customer_id: מזהה הלקוח
        **kwargs: פרמטרים לעדכון
    
    Returns:
        הלקוח המעודכן
    """
    return update_existing_customer(customer_id, kwargs)

def delete_customer(customer_id: str, force: bool = True):
    """
    מוחק לקוח מהחנות.
    
    Args:
        customer_id: מזהה הלקוח
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_customer(customer_id, force)

def get_orders(
    customer_id: str,
    page: int = 1,
    per_page: int = 10,
    status: str = None,
    **kwargs
):
    """
    מחזיר את ההזמנות של לקוח.
    
    Args:
        customer_id: מזהה הלקוח
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        status: סטטוס ההזמנה (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        ההזמנות של הלקוח
    """
    params = {
        "page": page,
        "per_page": per_page,
        **kwargs
    }
    
    if status:
        params["status"] = status
    
    return get_customer_orders(customer_id, **params)

def get_downloads(customer_id: str):
    """
    מחזיר את ההורדות של לקוח.
    
    Args:
        customer_id: מזהה הלקוח
    
    Returns:
        ההורדות של הלקוח
    """
    return get_customer_downloads(customer_id)

def update_billing_address(
    customer_id: str,
    first_name: str = None,
    last_name: str = None,
    company: str = None,
    address_1: str = None,
    address_2: str = None,
    city: str = None,
    state: str = None,
    postcode: str = None,
    country: str = None,
    email: str = None,
    phone: str = None
):
    """
    מעדכן את כתובת החיוב של לקוח.
    
    Args:
        customer_id: מזהה הלקוח
        first_name: שם פרטי (אופציונלי)
        last_name: שם משפחה (אופציונלי)
        company: חברה (אופציונלי)
        address_1: כתובת 1 (אופציונלי)
        address_2: כתובת 2 (אופציונלי)
        city: עיר (אופציונלי)
        state: מדינה/מחוז (אופציונלי)
        postcode: מיקוד (אופציונלי)
        country: מדינה (אופציונלי)
        email: אימייל (אופציונלי)
        phone: טלפון (אופציונלי)
    
    Returns:
        הלקוח המעודכן
    """
    billing = {}
    
    if first_name:
        billing["first_name"] = first_name
    
    if last_name:
        billing["last_name"] = last_name
    
    if company:
        billing["company"] = company
    
    if address_1:
        billing["address_1"] = address_1
    
    if address_2:
        billing["address_2"] = address_2
    
    if city:
        billing["city"] = city
    
    if state:
        billing["state"] = state
    
    if postcode:
        billing["postcode"] = postcode
    
    if country:
        billing["country"] = country
    
    if email:
        billing["email"] = email
    
    if phone:
        billing["phone"] = phone
    
    return update_existing_customer(customer_id, {"billing": billing})

def update_shipping_address(
    customer_id: str,
    first_name: str = None,
    last_name: str = None,
    company: str = None,
    address_1: str = None,
    address_2: str = None,
    city: str = None,
    state: str = None,
    postcode: str = None,
    country: str = None
):
    """
    מעדכן את כתובת המשלוח של לקוח.
    
    Args:
        customer_id: מזהה הלקוח
        first_name: שם פרטי (אופציונלי)
        last_name: שם משפחה (אופציונלי)
        company: חברה (אופציונלי)
        address_1: כתובת 1 (אופציונלי)
        address_2: כתובת 2 (אופציונלי)
        city: עיר (אופציונלי)
        state: מדינה/מחוז (אופציונלי)
        postcode: מיקוד (אופציונלי)
        country: מדינה (אופציונלי)
    
    Returns:
        הלקוח המעודכן
    """
    shipping = {}
    
    if first_name:
        shipping["first_name"] = first_name
    
    if last_name:
        shipping["last_name"] = last_name
    
    if company:
        shipping["company"] = company
    
    if address_1:
        shipping["address_1"] = address_1
    
    if address_2:
        shipping["address_2"] = address_2
    
    if city:
        shipping["city"] = city
    
    if state:
        shipping["state"] = state
    
    if postcode:
        shipping["postcode"] = postcode
    
    if country:
        shipping["country"] = country
    
    return update_existing_customer(customer_id, {"shipping": shipping})
