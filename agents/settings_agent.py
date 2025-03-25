#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent הגדרות למערכת AI Agents לניהול חנות WooCommerce
------------------------------------------------------

קובץ זה מגדיר את ה-Agent המתמחה בהגדרות החנות, שאחראי על:
- הגדרות כלליות
- הגדרות תשלום
- הגדרות משלוח
- הגדרות מיסים
- הגדרות מדינות
- הגדרות אזורי משלוח
"""

from .base import Agent, Tool, function_tool

# Dummy tool functions for demonstration
def get_store_settings():
    """מחזיר הגדרות כלליות של החנות"""
    result = {
        "store_name": "חנות לדוגמה",
        "store_address": "רחוב ראשי 1, תל אביב",
        "store_email": "store@example.com",
        "store_currency": "ILS",
        "store_language": "he_IL"
    }
    return f"הגדרות כלליות של החנות:\n" \
           f"שם החנות: {result['store_name']}\n" \
           f"כתובת: {result['store_address']}\n" \
           f"אימייל: {result['store_email']}\n" \
           f"מטבע: {result['store_currency']}\n" \
           f"שפה: {result['store_language']}"

def get_general_settings():
    """מחזיר הגדרות כלליות של החנות"""
    return get_store_settings()

def update_general_settings(**data):
    """מעדכן הגדרות כלליות של החנות"""
    updated_fields = ", ".join(data.keys()) if data else "ללא שינויים"
    return f"הגדרות החנות עודכנו בהצלחה. שדות שעודכנו: {updated_fields}"

def get_payment_gateways():
    """מחזיר רשימת שערי תשלום זמינים"""
    result = {
        "payment_methods": [
            {"id": "bacs", "title": "העברה בנקאית", "enabled": True},
            {"id": "cod", "title": "תשלום במזומן", "enabled": True},
            {"id": "credit_card", "title": "כרטיס אשראי", "enabled": True}
        ]
    }
    
    methods_str = "\n".join([f"- {m['title']} (קוד: {m['id']}): {'מופעל' if m['enabled'] else 'מושבת'}" for m in result["payment_methods"]])
    
    return f"שערי תשלום זמינים בחנות:\n{methods_str}"

def get_payment_settings():
    """מחזיר הגדרות תשלום של החנות"""
    return get_payment_gateways()

def update_payment_method(method_id, **data):
    """מעדכן הגדרות אמצעי תשלום"""
    updated_fields = ", ".join(data.keys()) if data else "ללא שינויים"
    return f"אמצעי התשלום {method_id} עודכן בהצלחה. שדות שעודכנו: {updated_fields}"

def get_shipping_methods():
    """מחזיר רשימת שיטות משלוח זמינות"""
    result = {
        "shipping_methods": [
            {"id": "flat_rate", "title": "תעריף קבוע", "enabled": True},
            {"id": "free_shipping", "title": "משלוח חינם", "enabled": True},
            {"id": "local_pickup", "title": "איסוף עצמי", "enabled": False}
        ]
    }
    
    methods_str = "\n".join([f"- {m['title']} (קוד: {m['id']}): {'מופעל' if m['enabled'] else 'מושבת'}" for m in result["shipping_methods"]])
    
    return f"שיטות משלוח זמינות בחנות:\n{methods_str}"

def get_shipping_settings():
    """מחזיר הגדרות משלוח של החנות"""
    result = {
        "shipping_zones": [
            {"id": 1, "name": "ישראל", "methods": ["משלוח רגיל", "משלוח מהיר"]},
            {"id": 2, "name": "בינלאומי", "methods": ["דואר אוויר", "שליח בינלאומי"]}
        ]
    }
    
    zones_str = ""
    for zone in result["shipping_zones"]:
        methods_str = ", ".join(zone["methods"])
        zones_str += f"- אזור {zone['name']} (מזהה: {zone['id']}): {methods_str}\n"
    
    return f"אזורי משלוח מוגדרים בחנות:\n{zones_str}"

def update_shipping_zone(zone_id, **data):
    """מעדכן הגדרות אזור משלוח"""
    updated_fields = ", ".join(data.keys()) if data else "ללא שינויים"
    return f"אזור המשלוח {zone_id} עודכן בהצלחה. שדות שעודכנו: {updated_fields}"

def get_tax_settings():
    """מחזיר הגדרות מס של החנות"""
    result = {
        "tax_classes": [
            {"id": 1, "name": "רגיל", "rate": 17},
            {"id": 2, "name": "מופחת", "rate": 0}
        ]
    }
    
    classes_str = "\n".join([f"- {c['name']} (מזהה: {c['id']}): {c['rate']}%" for c in result["tax_classes"]])
    
    return f"מחלקות מס מוגדרות בחנות:\n{classes_str}"

def update_tax_class(class_id, **data):
    """מעדכן הגדרות מחלקת מס"""
    updated_fields = ", ".join(data.keys()) if data else "ללא שינויים"
    return f"מחלקת המס {class_id} עודכנה בהצלחה. שדות שעודכנו: {updated_fields}"

def update_tax_settings(prices_include_tax=None, tax_based_on=None):
    """מעדכן הגדרות מיסים כלליות"""
    updated_params = []
    if prices_include_tax is not None:
        updated_params.append(f"מחירים כוללים מע\"מ: {'כן' if prices_include_tax else 'לא'}")
    if tax_based_on is not None:
        updated_params.append(f"מיסוי מבוסס על: {tax_based_on}")
    
    updated_str = ", ".join(updated_params) if updated_params else "ללא שינויים"
    return f"הגדרות המיסים הכלליות עודכנו בהצלחה. שדות שעודכנו: {updated_str}"

def update_setting(setting_key, setting_value):
    """מעדכן הגדרה ספציפית של החנות"""
    return f"ההגדרה {setting_key} עודכנה בהצלחה לערך: {setting_value}"

def update_payment_settings(payment_gateway, enabled=True, settings=None):
    """מעדכן הגדרות אמצעי תשלום"""
    status = "הופעל" if enabled else "הושבת"
    settings_str = f", הגדרות נוספות עודכנו" if settings else ""
    return f"אמצעי התשלום {payment_gateway} {status} בהצלחה{settings_str}."

def update_shipping_settings(shipping_zone, methods=None):
    """מעדכן הגדרות משלוח של החנות"""
    if methods:
        methods_list = ", ".join(methods)
        return f"הגדרות המשלוח לאזור '{shipping_zone}' עודכנו בהצלחה. שיטות משלוח: {methods_list}"
    return f"הגדרות המשלוח לאזור '{shipping_zone}' עודכנו בהצלחה."

def get_email_settings():
    """מחזיר הגדרות האימייל של החנות"""
    result = {
        "admin_emails": ["admin@example.com"],
        "customer_emails": {
            "new_order": True,
            "processing_order": True,
            "completed_order": True,
            "refunded_order": True,
            "customer_note": True
        },
        "smtp_settings": {
            "host": "smtp.example.com",
            "port": 587,
            "encryption": "tls",
            "username": "noreply@example.com"
        },
        "from_name": "חנות לדוגמה",
        "from_address": "noreply@example.com"
    }
    
    customer_emails = ", ".join([k for k, v in result["customer_emails"].items() if v])
    
    return f"הגדרות אימייל של החנות:\n\n" \
           f"אימייל מנהל: {', '.join(result['admin_emails'])}\n" \
           f"הודעות ללקוח: {customer_emails}\n" \
           f"שם השולח: {result['from_name']}\n" \
           f"כתובת השולח: {result['from_address']}\n\n" \
           f"הגדרות SMTP:\n" \
           f"שרת: {result['smtp_settings']['host']}\n" \
           f"פורט: {result['smtp_settings']['port']}\n" \
           f"הצפנה: {result['smtp_settings']['encryption']}"

def get_currency_settings():
    """מחזיר הגדרות המטבע של החנות"""
    result = {
        "currency": "ILS",
        "currency_symbol": "₪",
        "thousand_separator": ",",
        "decimal_separator": ".",
        "decimals": 2,
        "price_format": "%s%v"
    }
    
    return f"הגדרות מטבע של החנות:\n\n" \
           f"מטבע: {result['currency']}\n" \
           f"סמל המטבע: {result['currency_symbol']}\n" \
           f"מפריד אלפים: '{result['thousand_separator']}'\n" \
           f"מפריד עשרוני: '{result['decimal_separator']}'\n" \
           f"ספרות אחרי הנקודה: {result['decimals']}\n" \
           f"פורמט מחיר: {result['price_format']}"

def create_settings_agent(client, model="gpt-4o", woo_client=None):
    """
    יוצר agent מתמחה להגדרות.
    
    Args:
        client: לקוח OpenAI
        model: מודל השפה לשימוש (ברירת מחדל: gpt-4o)
        woo_client: לקוח WooCommerce (אופציונלי)
    
    Returns:
        Agent מתמחה להגדרות
    """
    
    # יצירת ה-agent
    settings_agent = Agent(
        client=client,
        model=model,
        woo_client=woo_client
    )
    
    # הגדרת תיאור הסוכן
    settings_agent.description = """
    אני סוכן AI מתמחה בהגדרות החנות WooCommerce. אני יכול לעזור לך ב:
    - הצגת הגדרות החנות הנוכחיות
    - עדכון הגדרות כלליות
    - ניהול אפשרויות תשלום
    - הגדרת אפשרויות משלוח
    - ניהול הגדרות מיסים
    - הגדרות אימייל והתראות
    - ניהול מטבעות ואזורי מסחר

    אשמח לסייע בכל שאלה או בקשה הקשורה להגדרות ותצורת החנות!
    
    כשתשאל אותי "איזה סוכן אתה?", אדע להגיד לך שאני סוכן ההגדרות של המערכת.
    """
    
    # הוספת כלים כאשר יש חיבור לחנות
    if woo_client:
        @function_tool(name="get_general_settings", description="מחזיר את ההגדרות הכלליות של החנות")
        def get_general_settings_tool():
            """
            מחזיר את ההגדרות הכלליות של החנות.
            
            Returns:
                הגדרות החנות הכלליות או הודעת שגיאה
            """
            return get_general_settings()
        
        @function_tool(name="update_general_settings", description="מעדכן את ההגדרות הכלליות של החנות")
        def update_general_settings_tool(store_name: str = None, store_address: str = None, default_country: str = None,
                                      store_email: str = None, timezone: str = None):
            """
            מעדכן את ההגדרות הכלליות של החנות.
            
            Args:
                store_name: שם החנות (אופציונלי)
                store_address: כתובת החנות (אופציונלי)
                default_country: מדינת ברירת מחדל (אופציונלי)
                store_email: אימייל החנות (אופציונלי)
                timezone: אזור זמן (אופציונלי)
            
            Returns:
                הגדרות החנות המעודכנות או הודעת שגיאה
            """
            data = {}
            if store_name is not None: data["store_name"] = store_name
            if store_address is not None: data["store_address"] = store_address 
            if default_country is not None: data["default_country"] = default_country
            if store_email is not None: data["store_email"] = store_email
            if timezone is not None: data["timezone"] = timezone
            
            return update_general_settings(**data)
        
        @function_tool(name="get_payment_settings", description="מחזיר את הגדרות התשלום של החנות")
        def get_payment_settings_tool():
            """
            מחזיר את הגדרות התשלום של החנות.
            
            Returns:
                הגדרות התשלום או הודעת שגיאה
            """
            return get_payment_settings()
        
        @function_tool(name="update_payment_settings", description="מעדכן את הגדרות התשלום של החנות")
        def update_payment_settings_tool(payment_gateway: str, enabled: bool = True, settings: dict = None):
            """
            מעדכן את הגדרות התשלום של החנות.
            
            Args:
                payment_gateway: שער התשלום לעדכון
                enabled: האם לאפשר את שער התשלום (ברירת מחדל: True)
                settings: הגדרות נוספות עבור שער התשלום (אופציונלי)
            
            Returns:
                הגדרות התשלום המעודכנות או הודעת שגיאה
            """
            return update_payment_settings(payment_gateway, enabled, settings)
        
        @function_tool(name="get_shipping_settings", description="מחזיר את הגדרות המשלוח של החנות")
        def get_shipping_settings_tool():
            """
            מחזיר את הגדרות המשלוח של החנות.
            
            Returns:
                הגדרות המשלוח או הודעת שגיאה
            """
            return get_shipping_settings()
        
        @function_tool(name="update_shipping_settings", description="מעדכן את הגדרות המשלוח של החנות")
        def update_shipping_settings_tool(shipping_zone: str, methods: list = None):
            """
            מעדכן את הגדרות המשלוח של החנות.
            
            Args:
                shipping_zone: אזור המשלוח לעדכון
                methods: רשימת שיטות משלוח לאזור זה (אופציונלי)
            
            Returns:
                הגדרות המשלוח המעודכנות או הודעת שגיאה
            """
            return update_shipping_settings(shipping_zone, methods)
        
        @function_tool(name="get_tax_settings", description="מחזיר את הגדרות המיסים של החנות")
        def get_tax_settings_tool():
            """
            מחזיר את הגדרות המיסים של החנות.
            
            Returns:
                הגדרות המיסים או הודעת שגיאה
            """
            return get_tax_settings()
        
        @function_tool(name="update_tax_settings", description="מעדכן את הגדרות המיסים של החנות")
        def update_tax_settings_tool(prices_include_tax: bool = None, tax_based_on: str = None):
            """
            מעדכן את הגדרות המיסים של החנות.
            
            Args:
                prices_include_tax: האם המחירים כוללים מס (אופציונלי)
                tax_based_on: על מה המס מבוסס (אופציונלי)
            
            Returns:
                הגדרות המיסים המעודכנות או הודעת שגיאה
            """
            return update_tax_settings(prices_include_tax, tax_based_on)
            
        @function_tool(name="update_setting", description="מעדכן הגדרה ספציפית של החנות")
        def update_setting_tool(setting_key: str, setting_value: str):
            """
            מעדכן הגדרה ספציפית של החנות.
            
            Args:
                setting_key: מפתח ההגדרה לעדכון
                setting_value: הערך החדש להגדרה
            
            Returns:
                הודעת הצלחה או שגיאה
            """
            return update_setting(setting_key, setting_value)
        
        @function_tool(name="get_store_settings", description="מחזיר את ההגדרות הכלליות של החנות")
        def get_store_settings_tool():
            """
            מחזיר את ההגדרות הכלליות של החנות.
            
            Returns:
                הגדרות החנות הכלליות או הודעת שגיאה
            """
            return get_store_settings()
            
        @function_tool(name="get_payment_gateways", description="מחזיר רשימת שערי תשלום זמינים")
        def get_payment_gateways_tool():
            """
            מחזיר רשימת שערי תשלום זמינים.
            
            Returns:
                רשימת שערי תשלום זמינים או הודעת שגיאה
            """
            return get_payment_gateways()
            
        @function_tool(name="get_shipping_methods", description="מחזיר רשימת שיטות משלוח זמינות")
        def get_shipping_methods_tool():
            """
            מחזיר רשימת שיטות משלוח זמינות.
            
            Returns:
                רשימת שיטות משלוח זמינות או הודעת שגיאה
            """
            return get_shipping_methods()
        
        @function_tool(name="get_email_settings", description="מחזיר את הגדרות האימייל של החנות")
        def get_email_settings_tool():
            """
            מחזיר את הגדרות האימייל של החנות.
            
            Returns:
                הגדרות האימייל הנוכחיות של החנות
            """
            return get_email_settings()
            
        @function_tool(name="get_currency_settings", description="מחזיר את הגדרות המטבע של החנות")
        def get_currency_settings_tool():
            """
            מחזיר את הגדרות המטבע של החנות.
            
            Returns:
                הגדרות המטבע הנוכחיות של החנות
            """
            return get_currency_settings()
        
        # הוספת כל הכלים לסוכן
        settings_agent.add_tool(get_store_settings_tool)
        settings_agent.add_tool(get_general_settings_tool)
        settings_agent.add_tool(update_general_settings_tool)
        settings_agent.add_tool(get_payment_gateways_tool)
        settings_agent.add_tool(get_payment_settings_tool)
        settings_agent.add_tool(update_payment_settings_tool)
        settings_agent.add_tool(get_shipping_methods_tool)
        settings_agent.add_tool(get_shipping_settings_tool)
        settings_agent.add_tool(update_shipping_settings_tool)
        settings_agent.add_tool(get_tax_settings_tool)
        settings_agent.add_tool(update_tax_settings_tool)
        settings_agent.add_tool(update_setting_tool)
        settings_agent.add_tool(get_email_settings_tool)
        settings_agent.add_tool(get_currency_settings_tool)
    
    return settings_agent
