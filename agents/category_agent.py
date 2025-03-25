#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent קטגוריות למערכת AI Agents לניהול חנות WooCommerce
--------------------------------------------------------

קובץ זה מגדיר את ה-Agent המתמחה בקטגוריות, שאחראי על:
- יצירת קטגוריות חדשות
- עריכת קטגוריות קיימות
- מחיקת קטגוריות
- ניהול היררכית קטגוריות
"""

from .base import Agent, Tool, function_tool
import json

def get_category(woo_client, category_id=None, slug=None):
    """מחזיר מידע על קטגוריה לפי מזהה או סלאג"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
        
    try:
        if category_id:
            result = woo_client.get_category(category_id)
        elif slug:
            categories = woo_client.get_categories(slug=slug)
            if not categories:
                return f"לא נמצאה קטגוריה עם ה-slug: {slug}"
            result = categories[0]
        else:
            return "נדרש מזהה קטגוריה או slug"
            
        if not result or "id" not in result:
            return f"לא נמצאה קטגוריה מתאימה"
            
        # יצירת טקסט מתאים לתצוגה
        response = f"פרטי הקטגוריה #{result['id']}:\n"
        response += f"שם: '{result['name']}'\n"
        response += f"סלאג: {result.get('slug', '')}\n"
        response += f"הורה: {result.get('parent', 0)}\n"
        response += f"תיאור: {result.get('description', '')}\n"
        response += f"מספר מוצרים: {result.get('count', 0)}\n"
        
        return response
    except Exception as e:
        return f"שגיאה בקבלת פרטי הקטגוריה: {str(e)}"

def list_categories(woo_client, parent=None, limit=10, orderby="name", order="asc"):
    """מחזיר רשימת קטגוריות עם אפשרויות סינון"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
        
    try:
        params = {
            "per_page": limit,
            "orderby": orderby,
            "order": order
        }
        
        if parent is not None:
            params["parent"] = parent
            
        categories = woo_client.get_categories(**params)
        
        if not categories:
            return "לא נמצאו קטגוריות"
            
        # יצירת טקסט מתאים לתצוגה
        response = "רשימת הקטגוריות הזמינות:\n"
        for category in categories:
            response += f"#{category['id']}: שם '{category['name']}', "
            response += f"סלאג: {category.get('slug', '')}, "
            response += f"הורה: {category.get('parent', 0)}, "
            response += f"מספר מוצרים: {category.get('count', 0)}\n"
            
        return response
    except Exception as e:
        return f"שגיאה בקבלת רשימת הקטגוריות: {str(e)}"

def create_category(woo_client, name, slug=None, parent=None, description=None, image=None, display=None, **kwargs):
    """יוצר קטגוריה חדשה בחנות"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
        
    try:
        # בניית נתוני הקטגוריה
        data = {
            "name": name
        }
        
        if slug:
            data["slug"] = slug
        if parent:
            data["parent"] = parent
        if description:
            data["description"] = description
        if image:
            data["image"] = {"src": image}
        if display:
            data["display"] = display
            
        # הוספת פרמטרים נוספים
        for key, value in kwargs.items():
            data[key] = value
            
        # יצירת הקטגוריה
        result = woo_client.create_category(data)
        
        if not result or "id" not in result:
            return f"אירעה שגיאה ביצירת הקטגוריה"
            
        # יצירת טקסט מתאים לתצוגה
        response = f"הקטגוריה נוצרה בהצלחה!\n"
        response += f"מזהה: #{result['id']}\n"
        response += f"שם: '{result['name']}'\n"
        response += f"סלאג: {result.get('slug', '')}\n"
        response += f"הורה: {result.get('parent', 0)}\n"
        response += f"תיאור: {result.get('description', '')}\n"
        
        return response
    except Exception as e:
        return f"שגיאה ביצירת הקטגוריה: {str(e)}"

def update_category(woo_client, category_id, **data):
    """מעדכן קטגוריה קיימת בחנות"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
        
    try:
        # וידוא שיש מזהה קטגוריה
        if not category_id:
            return "נדרש מזהה קטגוריה לעדכון"
            
        # עדכון הקטגוריה
        result = woo_client.update_category(category_id, data)
        
        if not result or "id" not in result:
            return f"אירעה שגיאה בעדכון הקטגוריה עם המזהה {category_id}"
            
        # בניית רשימת שדות שעודכנו
        updated_fields = []
        if data.get("name"):
            updated_fields.append(f"שם: '{result['name']}'")
        if data.get("slug"):
            updated_fields.append(f"סלאג: {result.get('slug', '')}")
        if data.get("parent") is not None:
            updated_fields.append(f"הורה: {result.get('parent', 0)}")
        if data.get("description"):
            updated_fields.append("תיאור")
        if data.get("image"):
            updated_fields.append("תמונה")
        if data.get("display"):
            updated_fields.append(f"תצוגה: {result.get('display', '')}")
            
        updated_str = ", ".join(updated_fields) if updated_fields else "ללא שינויים"
        
        return f"הקטגוריה (מזהה: {category_id}) עודכנה בהצלחה!\nשדות שעודכנו: {updated_str}"
    except Exception as e:
        return f"שגיאה בעדכון הקטגוריה: {str(e)}"

def delete_category(woo_client, category_id, force=False):
    """מוחק קטגוריה"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
        
    try:
        # וידוא שיש מזהה קטגוריה
        if not category_id:
            return "נדרש מזהה קטגוריה למחיקה"
            
        # מחיקת הקטגוריה
        result = woo_client.delete_category(category_id, force)
        
        if not result:
            return f"אירעה שגיאה במחיקת הקטגוריה עם המזהה {category_id}"
            
        return f"הקטגוריה עם המזהה {category_id} נמחקה בהצלחה"
    except Exception as e:
        return f"שגיאה במחיקת הקטגוריה: {str(e)}"

def get_category_products(woo_client, category_id, limit=10, orderby="date", order="desc"):
    """מחזיר רשימת מוצרים בקטגוריה מסוימת"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
        
    try:
        # וידוא שיש מזהה קטגוריה
        if not category_id:
            return "נדרש מזהה קטגוריה"
            
        # קבלת המוצרים בקטגוריה
        products = woo_client.get_products(
            category=category_id,
            per_page=limit,
            orderby=orderby,
            order=order
        )
        
        if not products:
            return f"לא נמצאו מוצרים בקטגוריה עם המזהה {category_id}"
            
        # יצירת טקסט מתאים לתצוגה
        response = f"מוצרים בקטגוריה (מזהה: {category_id}):\n"
        for product in products:
            response += f"#{product['id']}: {product['name']}, "
            response += f"מחיר: ₪{product.get('price', '')} | "
            response += f"מלאי: {product.get('stock_quantity', 'לא מנוהל')}\n"
            
        return response
    except Exception as e:
        return f"שגיאה בקבלת מוצרי הקטגוריה: {str(e)}"

def create_category_agent(client, model="gpt-4o", woo_client=None):
    """
    יוצר agent מתמחה לקטגוריות.
    
    Args:
        client: לקוח OpenAI
        model: מודל השפה לשימוש (ברירת מחדל: gpt-4o)
        woo_client: לקוח WooCommerce (אופציונלי)
    
    Returns:
        Agent מתמחה לקטגוריות
    """
    
    # יצירת ה-agent
    category_agent = Agent(
        client=client,
        model=model
    )
    
    # הגדרת תיאור הסוכן
    category_agent.description = """
    אני סוכן AI מתמחה בניהול קטגוריות בחנות WooCommerce. אני יכול לעזור לך ב:
    - הצגת מידע על קטגוריות
    - יצירת קטגוריות חדשות
    - עריכת קטגוריות קיימות
    - מחיקת קטגוריות
    - ניהול היררכיות של קטגוריות
    - הצגת מוצרים בקטגוריה

    אשמח לסייע בכל שאלה או בקשה הקשורה לסיווג וארגון המוצרים בקטגוריות בחנות!
    
    כשתשאל אותי "איזה סוכן אתה?", אדע להגיד לך שאני סוכן הקטגוריות של המערכת.
    """
    
    # הוספת כלים כאשר יש חיבור לחנות
    if woo_client:
        @function_tool(name="get_category", description="מחזיר פרטי קטגוריה לפי מזהה או סלאג")
        def get_category_tool(category_id: int = None, slug: str = None):
            """
            מחזיר מידע על קטגוריה לפי מזהה או סלאג.
            
            Args:
                category_id: מזהה הקטגוריה (אופציונלי אם סופק סלאג)
                slug: סלאג הקטגוריה (אופציונלי אם סופק מזהה)
            
            Returns:
                פרטי הקטגוריה או הודעת שגיאה
            """
            return get_category(woo_client, category_id, slug)
        
        @function_tool(name="list_categories", description="מחזיר רשימת קטגוריות")
        def list_categories_tool(parent: int = None, limit: int = 10, orderby: str = "name", order: str = "asc"):
            """
            מחזיר רשימה של קטגוריות עם אפשרויות סינון.
            
            Args:
                parent: מזהה קטגוריית אב לסינון (אופציונלי)
                limit: מספר הקטגוריות המקסימלי להצגה (אופציונלי, ברירת מחדל: 10)
                orderby: שדה המיון (name, id, count וכד') (אופציונלי, ברירת מחדל: name)
                order: סדר המיון (asc, desc) (אופציונלי, ברירת מחדל: asc)
            
            Returns:
                רשימת הקטגוריות או הודעת שגיאה
            """
            return list_categories(woo_client, parent, limit, orderby, order)
        
        @function_tool(name="create_category", description="יוצר קטגוריה חדשה")
        def create_category_tool(name: str, slug: str = None, parent: int = None, description: str = None, 
                             image: str = None, display: str = None):
            """
            יוצר קטגוריה חדשה.
            
            Args:
                name: שם הקטגוריה
                slug: סלאג הקטגוריה (אופציונלי)
                parent: מזהה קטגוריית האב (אופציונלי)
                description: תיאור הקטגוריה (אופציונלי)
                image: קישור לתמונת הקטגוריה (אופציונלי)
                display: אופן תצוגת הקטגוריה (אופציונלי)
            
            Returns:
                פרטי הקטגוריה שנוצרה או הודעת שגיאה
            """
            return create_category(woo_client, name, slug, parent, description, image, display)
        
        @function_tool(name="update_category", description="מעדכן קטגוריה קיימת")
        def update_category_tool(category_id: int, name: str = None, slug: str = None, parent: int = None, 
                             description: str = None, image: str = None, display: str = None):
            """
            מעדכן קטגוריה קיימת.
            
            Args:
                category_id: מזהה הקטגוריה לעדכון
                name: שם הקטגוריה (אופציונלי)
                slug: סלאג הקטגוריה (אופציונלי)
                parent: מזהה קטגוריית האב (אופציונלי)
                description: תיאור הקטגוריה (אופציונלי)
                image: קישור לתמונת הקטגוריה (אופציונלי)
                display: אופן תצוגת הקטגוריה (אופציונלי)
            
            Returns:
                פרטי הקטגוריה המעודכנת או הודעת שגיאה
            """
            data = {}
            if name is not None: data["name"] = name
            if slug is not None: data["slug"] = slug
            if parent is not None: data["parent"] = parent
            if description is not None: data["description"] = description
            if image is not None: data["image"] = {"src": image}
            if display is not None: data["display"] = display
            
            return update_category(woo_client, category_id, **data)
        
        @function_tool(name="delete_category", description="מוחק קטגוריה")
        def delete_category_tool(category_id: int, force: bool = False):
            """
            מוחק קטגוריה מהחנות.
            
            Args:
                category_id: מזהה הקטגוריה למחיקה
                force: האם למחוק גם תת-קטגוריות (אופציונלי, ברירת מחדל: False)
            
            Returns:
                הודעת הצלחה או שגיאה
            """
            return delete_category(woo_client, category_id, force)
        
        @function_tool(name="get_category_products", description="מחזיר רשימת מוצרים בקטגוריה")
        def get_category_products_tool(category_id: int, limit: int = 10, orderby: str = "date", order: str = "desc"):
            """
            מחזיר רשימת מוצרים בקטגוריה מסוימת.
            
            Args:
                category_id: מזהה הקטגוריה
                limit: מספר המוצרים המקסימלי להצגה (אופציונלי, ברירת מחדל: 10)
                orderby: שדה המיון (date, price, title וכד') (אופציונלי, ברירת מחדל: date)
                order: סדר המיון (asc, desc) (אופציונלי, ברירת מחדל: desc)
            
            Returns:
                רשימת המוצרים או הודעת שגיאה
            """
            return get_category_products(woo_client, category_id, limit, orderby, order)
        
        # הוספת כל הכלים לסוכן
        category_agent.add_tool(get_category_tool)
        category_agent.add_tool(list_categories_tool)
        category_agent.add_tool(create_category_tool)
        category_agent.add_tool(update_category_tool)
        category_agent.add_tool(delete_category_tool)
        category_agent.add_tool(get_category_products_tool)
    
    return category_agent
