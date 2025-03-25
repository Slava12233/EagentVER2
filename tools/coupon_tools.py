#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול קופונים בחנות WooCommerce
------------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent לקופונים יכול להשתמש בהם
כדי לבצע פעולות על קופונים בחנות WooCommerce.
"""

from api.coupon_api import (
    get_coupon_by_id,
    get_coupons_by_search,
    get_all_coupons,
    create_new_coupon,
    update_existing_coupon,
    delete_existing_coupon,
    get_coupon_by_code,
    create_percentage_discount_coupon,
    create_fixed_discount_coupon
)

def get_coupon(coupon_id: str = None, code: str = None, search: str = None):
    """
    מחזיר מידע על קופון לפי מזהה, קוד או חיפוש.
    
    Args:
        coupon_id: מזהה הקופון (אופציונלי)
        code: קוד הקופון (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על הקופון או הקופונים שנמצאו
    """
    if coupon_id:
        return get_coupon_by_id(coupon_id)
    elif code:
        return get_coupon_by_code(code)
    elif search:
        return get_coupons_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה קופון, קוד קופון או מונח חיפוש"}

def list_coupons(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    code: str = None,
    **kwargs
):
    """
    מחזיר רשימת קופונים עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        code: קוד הקופון (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        רשימת הקופונים שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page,
        **kwargs
    }
    
    if search:
        params["search"] = search
    
    if code:
        params["code"] = code
    
    return get_all_coupons(**params)

def create_coupon(
    code: str,
    discount_type: str,
    amount: str,
    description: str = "",
    **kwargs
):
    """
    יוצר קופון חדש.
    
    Args:
        code: קוד הקופון
        discount_type: סוג ההנחה (percent, fixed_cart, fixed_product)
        amount: סכום ההנחה
        description: תיאור הקופון (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקופון שנוצר
    """
    data = {
        "code": code,
        "discount_type": discount_type,
        "amount": amount,
        "description": description,
        **kwargs
    }
    
    return create_new_coupon(data)

def create_percentage_coupon(
    code: str,
    amount: str,
    description: str = "",
    expiry_date: str = None,
    **kwargs
):
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
    return create_percentage_discount_coupon(code, amount, description, expiry_date, **kwargs)

def create_fixed_coupon(
    code: str,
    amount: str,
    description: str = "",
    expiry_date: str = None,
    **kwargs
):
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
    return create_fixed_discount_coupon(code, amount, description, expiry_date, **kwargs)

def update_coupon(
    coupon_id: str,
    **kwargs
):
    """
    מעדכן קופון קיים.
    
    Args:
        coupon_id: מזהה הקופון
        **kwargs: פרמטרים לעדכון
    
    Returns:
        הקופון המעודכן
    """
    return update_existing_coupon(coupon_id, kwargs)

def delete_coupon(coupon_id: str, force: bool = True):
    """
    מוחק קופון מהחנות.
    
    Args:
        coupon_id: מזהה הקופון
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_coupon(coupon_id, force)

def set_coupon_usage_limit(coupon_id: str, usage_limit: int):
    """
    מגדיר מגבלת שימוש לקופון.
    
    Args:
        coupon_id: מזהה הקופון
        usage_limit: מגבלת השימוש
    
    Returns:
        הקופון המעודכן
    """
    return update_existing_coupon(coupon_id, {"usage_limit": usage_limit})

def set_coupon_expiry_date(coupon_id: str, expiry_date: str):
    """
    מגדיר תאריך תפוגה לקופון.
    
    Args:
        coupon_id: מזהה הקופון
        expiry_date: תאריך תפוגה בפורמט YYYY-MM-DD
    
    Returns:
        הקופון המעודכן
    """
    date_expires = f"{expiry_date}T23:59:59"
    return update_existing_coupon(coupon_id, {"date_expires": date_expires})

def set_coupon_product_restrictions(coupon_id: str, product_ids: list, exclude: bool = False):
    """
    מגדיר הגבלות מוצרים לקופון.
    
    Args:
        coupon_id: מזהה הקופון
        product_ids: רשימת מזהי מוצרים
        exclude: האם להחריג את המוצרים (ברירת מחדל: False)
    
    Returns:
        הקופון המעודכן
    """
    if exclude:
        return update_existing_coupon(coupon_id, {"excluded_product_ids": product_ids})
    else:
        return update_existing_coupon(coupon_id, {"product_ids": product_ids})

def set_coupon_category_restrictions(coupon_id: str, category_ids: list, exclude: bool = False):
    """
    מגדיר הגבלות קטגוריות לקופון.
    
    Args:
        coupon_id: מזהה הקופון
        category_ids: רשימת מזהי קטגוריות
        exclude: האם להחריג את הקטגוריות (ברירת מחדל: False)
    
    Returns:
        הקופון המעודכן
    """
    if exclude:
        return update_existing_coupon(coupon_id, {"excluded_product_categories": category_ids})
    else:
        return update_existing_coupon(coupon_id, {"product_categories": category_ids})
