#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent הזמנות למערכת AI Agents לניהול חנות WooCommerce
------------------------------------------------------

קובץ זה מגדיר את ה-Agent המתמחה בהזמנות, שאחראי על:
- צפייה בהזמנות
- עדכון סטטוס הזמנות
- ביטול הזמנות
- עדכון פרטי הזמנה
- חיפוש הזמנות
"""

from .base import Agent, Tool, function_tool

# Dummy tool functions for demonstration
def get_order(woo_client, order_id=None, search_term=None):
    """מקבל פרטי הזמנה לפי מזהה או לפי ערך חיפוש"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
    
    if order_id:
        # מדמה קבלת הזמנה מהשרת
        result = {
            "id": order_id,
            "number": f"#{order_id}",
            "status": "processing",
            "date_created": "2023-06-15T10:30:15",
            "total": "299.99",
            "customer_id": 1,
            "billing": {
                "first_name": "ישראל",
                "last_name": "ישראלי",
                "email": "customer@example.com"
            },
            "line_items": [
                {"product_id": 12, "name": "מוצר לדוגמה", "quantity": 2, "subtotal": "199.99"}
            ]
        }
        
        order_details = f"הזמנה {result['number']} ({result['status']}):\n"
        order_details += f"תאריך: {result['date_created']}\n"
        order_details += f"סכום כולל: ₪{result['total']}\n"
        order_details += f"לקוח: {result['billing']['first_name']} {result['billing']['last_name']} ({result['billing']['email']})\n\n"
        
        order_details += "פריטים בהזמנה:\n"
        for item in result['line_items']:
            order_details += f"- {item['name']}, כמות: {item['quantity']}, סכום: ₪{item['subtotal']}\n"
        
        return order_details
    elif search_term:
        # מדמה חיפוש הזמנה
        return f"נמצאה הזמנה שתואמת לחיפוש '{search_term}': הזמנה #123, סטטוס: processing, סכום: ₪299.99"
    else:
        return "נדרש מזהה הזמנה או ערך חיפוש"

def list_orders(woo_client, status=None, customer_id=None, limit=10):
    """מחזיר רשימת הזמנות עם אפשרות לסינון"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
    
    # מדמה קבלת רשימת הזמנות
    orders = []
    for i in range(1, limit+1):
        status_value = status or (["processing", "completed", "on-hold"][i % 3])
        customer = customer_id or (i % 5 + 1)
        orders.append({
            "id": i + 100,
            "number": f"#{i + 100}",
            "status": status_value,
            "date_created": "2023-06-15",
            "total": f"{i*100 + 99.99}",
            "customer_id": customer
        })
    
    # בניית מחרוזת התשובה
    status_filter = f" בסטטוס {status}" if status else ""
    customer_filter = f" ללקוח {customer_id}" if customer_id else ""
    result = f"רשימת {len(orders)} הזמנות אחרונות{status_filter}{customer_filter}:\n\n"
    
    for order in orders:
        result += f"הזמנה {order['number']} ({order['status']})\n"
        result += f"תאריך: {order['date_created']}, סכום: ₪{order['total']}, לקוח: {order['customer_id']}\n\n"
    
    return result

def create_order(woo_client, customer_id, products, billing=None, shipping=None, payment_method="cod"):
    """יוצר הזמנה חדשה"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
    
    # מדמה יצירת הזמנה
    products_str = ", ".join([f"מוצר {p['product_id']} (כמות: {p.get('quantity', 1)})" for p in products])
    
    return f"הזמנה חדשה נוצרה בהצלחה!\n" \
           f"מספר הזמנה: #1001\n" \
           f"לקוח: #{customer_id}\n" \
           f"מוצרים: {products_str}\n" \
           f"שיטת תשלום: {payment_method}\n" \
           f"סטטוס: pending\n" \
           f"סכום כולל: ₪{sum([p.get('quantity', 1) * 100 for p in products])}.00"

def update_order_status(woo_client, order_id, status):
    """עדכון סטטוס של הזמנה"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
    
    return f"סטטוס ההזמנה #{order_id} עודכן בהצלחה ל-{status}"

def delete_order(woo_client, order_id):
    """מחיקת הזמנה"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
    
    return f"ההזמנה #{order_id} נמחקה בהצלחה"

def add_order_note(woo_client, order_id, note, is_customer_note=False):
    """הוספת הערה להזמנה"""
    if woo_client is None:
        return "אין חיבור לחנות WooCommerce"
    
    note_type = "ללקוח" if is_customer_note else "פנימית"
    return f"הערה {note_type} נוספה בהצלחה להזמנה #{order_id}: \"{note}\""

def create_order_agent(client, model="gpt-4o", woo_client=None):
    """
    יוצר agent מתמחה להזמנות.
    
    Args:
        client: לקוח OpenAI
        model: מודל השפה לשימוש (ברירת מחדל: gpt-4o)
        woo_client: לקוח WooCommerce (אופציונלי)
    
    Returns:
        Agent מתמחה להזמנות
    """
    
    # יצירת ה-agent
    order_agent = Agent(
        client=client,
        model=model
    )
    
    # הגדרת תיאור הסוכן
    order_agent.description = """
    אני סוכן AI מתמחה בניהול הזמנות בחנות WooCommerce. אני יכול לעזור לך ב:
    - הצגת מידע על הזמנות
    - יצירת הזמנות חדשות
    - עדכון סטטוס הזמנות
    - ביטול או מחיקת הזמנות
    - הוספת הערות להזמנות
    - חיפוש הזמנות לפי קריטריונים שונים

    אשמח לסייע בכל שאלה או בקשה הקשורה להזמנות בחנות!
    
    כשתשאל אותי "איזה סוכן אתה?", אדע להגיד לך שאני סוכן ההזמנות של המערכת.
    """
    
    # הוספת כלים כאשר יש חיבור לחנות
    if woo_client:
        @function_tool(name="get_order", description="מחזיר מידע על הזמנה לפי מזהה")
        def get_order_tool(order_id: int):
            """
            מחזיר מידע על הזמנה לפי מזהה.
            
            Args:
                order_id: מזהה ההזמנה
            
            Returns:
                פרטי ההזמנה או הודעת שגיאה
            """
            return get_order(woo_client, order_id)
        
        @function_tool(name="list_orders", description="מחזיר רשימת הזמנות")
        def list_orders_tool(limit: int = 10, status: str = None, customer_id: int = None):
            """
            מחזיר רשימת הזמנות.
            
            Args:
                limit: מספר התוצאות המקסימלי (ברירת מחדל: 10)
                status: סטטוס ההזמנות לסינון (אופציונלי)
                customer_id: מזהה הלקוח לסינון (אופציונלי)
            
            Returns:
                רשימת הזמנות או הודעת שגיאה
            """
            return list_orders(woo_client, status, customer_id, limit)
        
        @function_tool(name="create_order", description="יוצר הזמנה חדשה")
        def create_order_tool(customer_id: int, products: list, billing: dict = None, shipping: dict = None, payment_method: str = "cod"):
            """
            יוצר הזמנה חדשה.
            
            Args:
                customer_id: מזהה הלקוח
                products: רשימת מוצרים להזמנה (כל מוצר חייב לכלול product_id וכמות)
                billing: פרטי חיוב (אופציונלי)
                shipping: פרטי משלוח (אופציונלי)
                payment_method: שיטת תשלום (ברירת מחדל: cod)
            
            Returns:
                פרטי ההזמנה שנוצרה או הודעת שגיאה
            """
            return create_order(woo_client, customer_id, products, billing, shipping, payment_method)
        
        @function_tool(name="update_order_status", description="מעדכן סטטוס של הזמנה")
        def update_order_status_tool(order_id: int, status: str):
            """
            מעדכן סטטוס של הזמנה.
            
            Args:
                order_id: מזהה ההזמנה
                status: הסטטוס החדש
            
            Returns:
                פרטי ההזמנה המעודכנת או הודעת שגיאה
            """
            return update_order_status(woo_client, order_id, status)
        
        @function_tool(name="delete_order", description="מוחק הזמנה")
        def delete_order_tool(order_id: int):
            """
            מוחק הזמנה.
            
            Args:
                order_id: מזהה ההזמנה
            
            Returns:
                תוצאת המחיקה או הודעת שגיאה
            """
            return delete_order(woo_client, order_id)
        
        @function_tool(name="add_order_note", description="מוסיף הערה להזמנה")
        def add_order_note_tool(order_id: int, note: str, is_customer_note: bool = False):
            """
            מוסיף הערה להזמנה.
            
            Args:
                order_id: מזהה ההזמנה
                note: תוכן ההערה
                is_customer_note: האם ההערה מיועדת ללקוח (ברירת מחדל: False)
            
            Returns:
                תוצאת הוספת ההערה או הודעת שגיאה
            """
            return add_order_note(woo_client, order_id, note, is_customer_note)
        
        # הוספת כל הכלים לסוכן
        order_agent.add_tool(get_order_tool)
        order_agent.add_tool(list_orders_tool)
        order_agent.add_tool(create_order_tool)
        order_agent.add_tool(update_order_status_tool)
        order_agent.add_tool(delete_order_tool)
        order_agent.add_tool(add_order_note_tool)
    
    return order_agent
