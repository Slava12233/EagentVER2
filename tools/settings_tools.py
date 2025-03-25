#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
כלים לניהול הגדרות בחנות WooCommerce
------------------------------------

קובץ זה מגדיר את הכלים (tools) שה-Agent להגדרות יכול להשתמש בהם
כדי לבצע פעולות על הגדרות בחנות WooCommerce.
"""

from api.settings_api import (
    get_store_settings,
    get_setting_group,
    get_setting_option,
    update_setting_option,
    get_payment_gateways,
    get_payment_gateway,
    update_payment_gateway,
    get_shipping_methods,
    get_shipping_method,
    get_shipping_zones,
    get_shipping_zone,
    create_shipping_zone,
    update_shipping_zone,
    delete_shipping_zone,
    get_shipping_zone_locations,
    update_shipping_zone_locations,
    get_shipping_zone_methods,
    create_shipping_zone_method,
    get_tax_classes,
    create_tax_class,
    delete_tax_class,
    get_webhooks,
    create_webhook,
    get_webhook,
    update_webhook,
    delete_webhook
)

def get_settings():
    """
    מחזיר את כל הגדרות החנות.
    
    Returns:
        הגדרות החנות
    """
    return get_store_settings()

def get_settings_group(group: str):
    """
    מחזיר קבוצת הגדרות.
    
    Args:
        group: שם קבוצת ההגדרות
    
    Returns:
        קבוצת ההגדרות
    """
    return get_setting_group(group)

def get_settings_option(group: str, option_id: str):
    """
    מחזיר אפשרות הגדרה ספציפית.
    
    Args:
        group: שם קבוצת ההגדרות
        option_id: מזהה האפשרות
    
    Returns:
        אפשרות ההגדרה
    """
    return get_setting_option(group, option_id)

def update_settings_option(group: str, option_id: str, value: str):
    """
    מעדכן אפשרות הגדרה ספציפית.
    
    Args:
        group: שם קבוצת ההגדרות
        option_id: מזהה האפשרות
        value: הערך החדש
    
    Returns:
        אפשרות ההגדרה המעודכנת
    """
    return update_setting_option(group, option_id, value)

def get_store_name():
    """
    מחזיר את שם החנות.
    
    Returns:
        שם החנות
    """
    return get_setting_option("general", "woocommerce_store_name")

def update_store_name(name: str):
    """
    מעדכן את שם החנות.
    
    Args:
        name: שם החנות החדש
    
    Returns:
        הגדרת שם החנות המעודכנת
    """
    return update_setting_option("general", "woocommerce_store_name", name)

def get_store_address():
    """
    מחזיר את כתובת החנות.
    
    Returns:
        כתובת החנות
    """
    address = {}
    address["address_1"] = get_setting_option("general", "woocommerce_store_address")["value"]
    address["address_2"] = get_setting_option("general", "woocommerce_store_address_2")["value"]
    address["city"] = get_setting_option("general", "woocommerce_store_city")["value"]
    address["postcode"] = get_setting_option("general", "woocommerce_store_postcode")["value"]
    address["country"] = get_setting_option("general", "woocommerce_default_country")["value"]
    
    return address

def update_store_address(address_1: str = None, address_2: str = None, city: str = None, postcode: str = None, country: str = None):
    """
    מעדכן את כתובת החנות.
    
    Args:
        address_1: כתובת 1 (אופציונלי)
        address_2: כתובת 2 (אופציונלי)
        city: עיר (אופציונלי)
        postcode: מיקוד (אופציונלי)
        country: מדינה (אופציונלי)
    
    Returns:
        כתובת החנות המעודכנת
    """
    result = {}
    
    if address_1 is not None:
        result["address_1"] = update_setting_option("general", "woocommerce_store_address", address_1)
    
    if address_2 is not None:
        result["address_2"] = update_setting_option("general", "woocommerce_store_address_2", address_2)
    
    if city is not None:
        result["city"] = update_setting_option("general", "woocommerce_store_city", city)
    
    if postcode is not None:
        result["postcode"] = update_setting_option("general", "woocommerce_store_postcode", postcode)
    
    if country is not None:
        result["country"] = update_setting_option("general", "woocommerce_default_country", country)
    
    return result

def get_currency_settings():
    """
    מחזיר את הגדרות המטבע.
    
    Returns:
        הגדרות המטבע
    """
    currency = {}
    currency["currency"] = get_setting_option("general", "woocommerce_currency")["value"]
    currency["currency_position"] = get_setting_option("general", "woocommerce_currency_pos")["value"]
    currency["thousand_separator"] = get_setting_option("general", "woocommerce_price_thousand_sep")["value"]
    currency["decimal_separator"] = get_setting_option("general", "woocommerce_price_decimal_sep")["value"]
    currency["number_of_decimals"] = get_setting_option("general", "woocommerce_price_num_decimals")["value"]
    
    return currency

def update_currency_settings(currency: str = None, position: str = None, thousand_separator: str = None, decimal_separator: str = None, decimals: str = None):
    """
    מעדכן את הגדרות המטבע.
    
    Args:
        currency: קוד המטבע (אופציונלי)
        position: מיקום סימן המטבע (אופציונלי)
        thousand_separator: מפריד אלפים (אופציונלי)
        decimal_separator: מפריד עשרוני (אופציונלי)
        decimals: מספר ספרות אחרי הנקודה העשרונית (אופציונלי)
    
    Returns:
        הגדרות המטבע המעודכנות
    """
    result = {}
    
    if currency is not None:
        result["currency"] = update_setting_option("general", "woocommerce_currency", currency)
    
    if position is not None:
        result["currency_position"] = update_setting_option("general", "woocommerce_currency_pos", position)
    
    if thousand_separator is not None:
        result["thousand_separator"] = update_setting_option("general", "woocommerce_price_thousand_sep", thousand_separator)
    
    if decimal_separator is not None:
        result["decimal_separator"] = update_setting_option("general", "woocommerce_price_decimal_sep", decimal_separator)
    
    if decimals is not None:
        result["number_of_decimals"] = update_setting_option("general", "woocommerce_price_num_decimals", decimals)
    
    return result

def list_payment_gateways():
    """
    מחזיר רשימת שערי תשלום.
    
    Returns:
        רשימת שערי התשלום
    """
    return get_payment_gateways()

def get_payment_gateway_details(gateway_id: str):
    """
    מחזיר פרטים על שער תשלום.
    
    Args:
        gateway_id: מזהה שער התשלום
    
    Returns:
        פרטי שער התשלום
    """
    return get_payment_gateway(gateway_id)

def enable_payment_gateway(gateway_id: str):
    """
    מפעיל שער תשלום.
    
    Args:
        gateway_id: מזהה שער התשלום
    
    Returns:
        שער התשלום המעודכן
    """
    return update_payment_gateway(gateway_id, {"enabled": True})

def disable_payment_gateway(gateway_id: str):
    """
    מבטל שער תשלום.
    
    Args:
        gateway_id: מזהה שער התשלום
    
    Returns:
        שער התשלום המעודכן
    """
    return update_payment_gateway(gateway_id, {"enabled": False})

def update_payment_gateway_settings(gateway_id: str, **settings):
    """
    מעדכן הגדרות של שער תשלום.
    
    Args:
        gateway_id: מזהה שער התשלום
        **settings: הגדרות לעדכון
    
    Returns:
        שער התשלום המעודכן
    """
    return update_payment_gateway(gateway_id, settings)

def list_shipping_methods():
    """
    מחזיר רשימת שיטות משלוח.
    
    Returns:
        רשימת שיטות המשלוח
    """
    return get_shipping_methods()

def get_shipping_method_details(method_id: str):
    """
    מחזיר פרטים על שיטת משלוח.
    
    Args:
        method_id: מזהה שיטת המשלוח
    
    Returns:
        פרטי שיטת המשלוח
    """
    return get_shipping_method(method_id)

def list_shipping_zones():
    """
    מחזיר רשימת אזורי משלוח.
    
    Returns:
        רשימת אזורי המשלוח
    """
    return get_shipping_zones()

def get_shipping_zone_details(zone_id: int):
    """
    מחזיר פרטים על אזור משלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
    
    Returns:
        פרטי אזור המשלוח
    """
    return get_shipping_zone(zone_id)

def create_new_shipping_zone(name: str, order: int = 0):
    """
    יוצר אזור משלוח חדש.
    
    Args:
        name: שם אזור המשלוח
        order: סדר אזור המשלוח (ברירת מחדל: 0)
    
    Returns:
        אזור המשלוח שנוצר
    """
    data = {
        "name": name,
        "order": order
    }
    
    return create_shipping_zone(data)

def update_shipping_zone_name(zone_id: int, name: str):
    """
    מעדכן את שם אזור המשלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
        name: שם אזור המשלוח החדש
    
    Returns:
        אזור המשלוח המעודכן
    """
    data = {"name": name}
    return update_shipping_zone(zone_id, data)

def remove_shipping_zone(zone_id: int):
    """
    מוחק אזור משלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
    
    Returns:
        תוצאת המחיקה
    """
    return delete_shipping_zone(zone_id)

def get_zone_locations(zone_id: int):
    """
    מחזיר את מיקומי אזור המשלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
    
    Returns:
        מיקומי אזור המשלוח
    """
    return get_shipping_zone_locations(zone_id)

def set_zone_locations(zone_id: int, locations: list):
    """
    מגדיר את מיקומי אזור המשלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
        locations: רשימת מיקומים
    
    Returns:
        מיקומי אזור המשלוח המעודכנים
    """
    return update_shipping_zone_locations(zone_id, locations)

def get_zone_shipping_methods(zone_id: int):
    """
    מחזיר את שיטות המשלוח של אזור משלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
    
    Returns:
        שיטות המשלוח של אזור המשלוח
    """
    return get_shipping_zone_methods(zone_id)

def add_shipping_method_to_zone(zone_id: int, method_id: str, **settings):
    """
    מוסיף שיטת משלוח לאזור משלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
        method_id: מזהה שיטת המשלוח
        **settings: הגדרות נוספות
    
    Returns:
        שיטת המשלוח שנוספה
    """
    data = {
        "method_id": method_id,
        **settings
    }
    
    return create_shipping_zone_method(zone_id, data)

def list_tax_classes():
    """
    מחזיר רשימת מחלקות מס.
    
    Returns:
        רשימת מחלקות המס
    """
    return get_tax_classes()

def add_tax_class(name: str):
    """
    מוסיף מחלקת מס חדשה.
    
    Args:
        name: שם מחלקת המס
    
    Returns:
        מחלקת המס שנוספה
    """
    return create_tax_class(name)

def remove_tax_class(slug: str):
    """
    מוחק מחלקת מס.
    
    Args:
        slug: ה-slug של מחלקת המס
    
    Returns:
        תוצאת המחיקה
    """
    return delete_tax_class(slug)

def list_webhooks():
    """
    מחזיר רשימת webhooks.
    
    Returns:
        רשימת ה-webhooks
    """
    return get_webhooks()

def get_webhook_details(webhook_id: int):
    """
    מחזיר פרטים על webhook.
    
    Args:
        webhook_id: מזהה ה-webhook
    
    Returns:
        פרטי ה-webhook
    """
    return get_webhook(webhook_id)

def create_new_webhook(name: str, topic: str, delivery_url: str, secret: str = None, status: str = "active"):
    """
    יוצר webhook חדש.
    
    Args:
        name: שם ה-webhook
        topic: נושא ה-webhook
        delivery_url: כתובת ה-URL לשליחה
        secret: סוד ה-webhook (אופציונלי)
        status: סטטוס ה-webhook (ברירת מחדל: active)
    
    Returns:
        ה-webhook שנוצר
    """
    data = {
        "name": name,
        "topic": topic,
        "delivery_url": delivery_url,
        "status": status
    }
    
    if secret:
        data["secret"] = secret
    
    return create_webhook(data)

def update_webhook_status(webhook_id: int, status: str):
    """
    מעדכן את סטטוס ה-webhook.
    
    Args:
        webhook_id: מזהה ה-webhook
        status: הסטטוס החדש (active או paused)
    
    Returns:
        ה-webhook המעודכן
    """
    data = {"status": status}
    return update_webhook(webhook_id, data)

def remove_webhook(webhook_id: int):
    """
    מוחק webhook.
    
    Args:
        webhook_id: מזהה ה-webhook
    
    Returns:
        תוצאת המחיקה
    """
    return delete_webhook(webhook_id)
