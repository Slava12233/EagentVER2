#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול קטגוריות בחנות WooCommerce
--------------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent לקטגוריות יכול להשתמש בהם
כדי לבצע פעולות על קטגוריות בחנות WooCommerce.
"""

from api.category_api import (
    get_category_by_id,
    get_categories_by_search,
    get_all_categories,
    create_new_category,
    update_existing_category,
    delete_existing_category,
    get_category_by_slug,
    get_category_by_name,
    get_subcategories,
    create_category_with_parent,
    get_products_by_category
)

def get_category(category_id: str = None, slug: str = None, name: str = None, search: str = None):
    """
    מחזיר מידע על קטגוריה לפי מזהה, slug, שם או חיפוש.
    
    Args:
        category_id: מזהה הקטגוריה (אופציונלי)
        slug: ה-slug של הקטגוריה (אופציונלי)
        name: שם הקטגוריה (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על הקטגוריה או הקטגוריות שנמצאו
    """
    if category_id:
        return get_category_by_id(category_id)
    elif slug:
        return get_category_by_slug(slug)
    elif name:
        return get_category_by_name(name)
    elif search:
        return get_categories_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה קטגוריה, slug, שם או מונח חיפוש"}

def list_categories(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    parent: int = None,
    **kwargs
):
    """
    מחזיר רשימת קטגוריות עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        parent: מזהה קטגוריית האב (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        רשימת הקטגוריות שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page,
        **kwargs
    }
    
    if search:
        params["search"] = search
    
    if parent is not None:
        params["parent"] = parent
    
    return get_all_categories(**params)

def create_category(
    name: str,
    description: str = "",
    slug: str = None,
    parent: int = 0,
    **kwargs
):
    """
    יוצר קטגוריה חדשה.
    
    Args:
        name: שם הקטגוריה
        description: תיאור הקטגוריה (אופציונלי)
        slug: ה-slug של הקטגוריה (אופציונלי)
        parent: מזהה קטגוריית האב (ברירת מחדל: 0 - קטגוריה ראשית)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקטגוריה שנוצרה
    """
    data = {
        "name": name,
        "description": description,
        "parent": parent,
        **kwargs
    }
    
    if slug:
        data["slug"] = slug
    
    return create_new_category(data)

def create_subcategory(
    name: str,
    parent_id: int,
    description: str = "",
    **kwargs
):
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
    return create_category_with_parent(name, parent_id, description, **kwargs)

def update_category(
    category_id: str,
    **kwargs
):
    """
    מעדכן קטגוריה קיימת.
    
    Args:
        category_id: מזהה הקטגוריה
        **kwargs: פרמטרים לעדכון
    
    Returns:
        הקטגוריה המעודכנת
    """
    return update_existing_category(category_id, kwargs)

def delete_category(category_id: str, force: bool = True):
    """
    מוחק קטגוריה מהחנות.
    
    Args:
        category_id: מזהה הקטגוריה
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_category(category_id, force)

def get_subcategories_of(parent_id: int):
    """
    מחזיר את כל קטגוריות המשנה של קטגוריה.
    
    Args:
        parent_id: מזהה הקטגוריה האב
    
    Returns:
        קטגוריות המשנה
    """
    return get_subcategories(parent_id)

def get_products_in_category(
    category_id: int,
    page: int = 1,
    per_page: int = 10,
    **kwargs
):
    """
    מחזיר את כל המוצרים בקטגוריה.
    
    Args:
        category_id: מזהה הקטגוריה
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        **kwargs: פרמטרים נוספים
    
    Returns:
        המוצרים בקטגוריה
    """
    params = {
        "page": page,
        "per_page": per_page,
        **kwargs
    }
    
    return get_products_by_category(category_id, **params)

def move_category(category_id: str, new_parent_id: int):
    """
    מעביר קטגוריה לקטגוריית אב אחרת.
    
    Args:
        category_id: מזהה הקטגוריה
        new_parent_id: מזהה קטגוריית האב החדשה
    
    Returns:
        הקטגוריה המעודכנת
    """
    return update_existing_category(category_id, {"parent": new_parent_id})

def set_category_image(category_id: str, image_id: int):
    """
    מגדיר תמונה לקטגוריה.
    
    Args:
        category_id: מזהה הקטגוריה
        image_id: מזהה התמונה
    
    Returns:
        הקטגוריה המעודכנת
    """
    return update_existing_category(category_id, {"image": {"id": image_id}})

def get_category_hierarchy():
    """
    מחזיר את היררכיית הקטגוריות המלאה.
    
    Returns:
        היררכיית הקטגוריות
    """
    # קבלת כל הקטגוריות
    all_categories = get_all_categories(per_page=100)
    
    # בניית מילון של קטגוריות לפי מזהה
    categories_by_id = {category["id"]: category for category in all_categories}
    
    # בניית היררכיה
    hierarchy = []
    
    # הוספת קטגוריות ראשיות
    for category in all_categories:
        if category["parent"] == 0:
            category_copy = category.copy()
            category_copy["children"] = []
            hierarchy.append(category_copy)
    
    # הוספת קטגוריות משנה
    for category in all_categories:
        if category["parent"] != 0 and category["parent"] in categories_by_id:
            parent_id = category["parent"]
            
            # חיפוש הקטגוריה האב בהיררכיה
            for root_category in hierarchy:
                if root_category["id"] == parent_id:
                    category_copy = category.copy()
                    category_copy["children"] = []
                    root_category["children"].append(category_copy)
                    break
    
    return hierarchy
