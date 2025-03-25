#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API להגדרות בחנות WooCommerce
----------------------------

קובץ זה מגדיר את הפונקציות שמתממשקות עם WooCommerce API
לביצוע פעולות על הגדרות בחנות.
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

def get_store_settings():
    """
    מחזיר את הגדרות החנות.
    
    Returns:
        הגדרות החנות
    """
    client = get_woocommerce_client()
    return client.wcapi.get("settings").json()

def get_setting_group(group):
    """
    מחזיר קבוצת הגדרות.
    
    Args:
        group: שם קבוצת ההגדרות
    
    Returns:
        קבוצת ההגדרות
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"settings/{group}").json()

def get_setting_option(group, id):
    """
    מחזיר אפשרות הגדרה ספציפית.
    
    Args:
        group: שם קבוצת ההגדרות
        id: מזהה האפשרות
    
    Returns:
        אפשרות ההגדרה
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"settings/{group}/{id}").json()

def update_setting_option(group, id, value):
    """
    מעדכן אפשרות הגדרה ספציפית.
    
    Args:
        group: שם קבוצת ההגדרות
        id: מזהה האפשרות
        value: הערך החדש
    
    Returns:
        אפשרות ההגדרה המעודכנת
    """
    client = get_woocommerce_client()
    data = {"value": value}
    return client.wcapi.put(f"settings/{group}/{id}", data).json()

def get_payment_gateways():
    """
    מחזיר את שערי התשלום.
    
    Returns:
        שערי התשלום
    """
    client = get_woocommerce_client()
    return client.wcapi.get("payment_gateways").json()

def get_payment_gateway(id):
    """
    מחזיר שער תשלום ספציפי.
    
    Args:
        id: מזהה שער התשלום
    
    Returns:
        שער התשלום
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"payment_gateways/{id}").json()

def update_payment_gateway(id, data):
    """
    מעדכן שער תשלום ספציפי.
    
    Args:
        id: מזהה שער התשלום
        data: נתוני העדכון
    
    Returns:
        שער התשלום המעודכן
    """
    client = get_woocommerce_client()
    return client.wcapi.put(f"payment_gateways/{id}", data).json()

def get_shipping_methods():
    """
    מחזיר את שיטות המשלוח.
    
    Returns:
        שיטות המשלוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get("shipping_methods").json()

def get_shipping_method(id):
    """
    מחזיר שיטת משלוח ספציפית.
    
    Args:
        id: מזהה שיטת המשלוח
    
    Returns:
        שיטת המשלוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"shipping_methods/{id}").json()

def get_shipping_zones():
    """
    מחזיר את אזורי המשלוח.
    
    Returns:
        אזורי המשלוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get("shipping/zones").json()

def get_shipping_zone(id):
    """
    מחזיר אזור משלוח ספציפי.
    
    Args:
        id: מזהה אזור המשלוח
    
    Returns:
        אזור המשלוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"shipping/zones/{id}").json()

def create_shipping_zone(data):
    """
    יוצר אזור משלוח חדש.
    
    Args:
        data: נתוני אזור המשלוח
    
    Returns:
        אזור המשלוח שנוצר
    """
    client = get_woocommerce_client()
    return client.wcapi.post("shipping/zones", data).json()

def update_shipping_zone(id, data):
    """
    מעדכן אזור משלוח קיים.
    
    Args:
        id: מזהה אזור המשלוח
        data: נתוני העדכון
    
    Returns:
        אזור המשלוח המעודכן
    """
    client = get_woocommerce_client()
    return client.wcapi.put(f"shipping/zones/{id}", data).json()

def delete_shipping_zone(id):
    """
    מוחק אזור משלוח.
    
    Args:
        id: מזהה אזור המשלוח
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.wcapi.delete(f"shipping/zones/{id}", params={"force": True}).json()

def get_shipping_zone_locations(zone_id):
    """
    מחזיר את מיקומי אזור המשלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
    
    Returns:
        מיקומי אזור המשלוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"shipping/zones/{zone_id}/locations").json()

def update_shipping_zone_locations(zone_id, locations):
    """
    מעדכן את מיקומי אזור המשלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
        locations: מיקומים חדשים
    
    Returns:
        מיקומי אזור המשלוח המעודכנים
    """
    client = get_woocommerce_client()
    return client.wcapi.put(f"shipping/zones/{zone_id}/locations", locations).json()

def get_shipping_zone_methods(zone_id):
    """
    מחזיר את שיטות המשלוח של אזור משלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
    
    Returns:
        שיטות המשלוח של אזור המשלוח
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"shipping/zones/{zone_id}/methods").json()

def create_shipping_zone_method(zone_id, data):
    """
    יוצר שיטת משלוח חדשה לאזור משלוח.
    
    Args:
        zone_id: מזהה אזור המשלוח
        data: נתוני שיטת המשלוח
    
    Returns:
        שיטת המשלוח שנוצרה
    """
    client = get_woocommerce_client()
    return client.wcapi.post(f"shipping/zones/{zone_id}/methods", data).json()

def get_tax_classes():
    """
    מחזיר את מחלקות המס.
    
    Returns:
        מחלקות המס
    """
    client = get_woocommerce_client()
    return client.wcapi.get("taxes/classes").json()

def create_tax_class(name):
    """
    יוצר מחלקת מס חדשה.
    
    Args:
        name: שם מחלקת המס
    
    Returns:
        מחלקת המס שנוצרה
    """
    client = get_woocommerce_client()
    data = {"name": name}
    return client.wcapi.post("taxes/classes", data).json()

def delete_tax_class(slug):
    """
    מוחק מחלקת מס.
    
    Args:
        slug: ה-slug של מחלקת המס
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.wcapi.delete(f"taxes/classes/{slug}", params={"force": True}).json()

def get_webhooks():
    """
    מחזיר את ה-webhooks.
    
    Returns:
        ה-webhooks
    """
    client = get_woocommerce_client()
    return client.wcapi.get("webhooks").json()

def create_webhook(data):
    """
    יוצר webhook חדש.
    
    Args:
        data: נתוני ה-webhook
    
    Returns:
        ה-webhook שנוצר
    """
    client = get_woocommerce_client()
    return client.wcapi.post("webhooks", data).json()

def get_webhook(id):
    """
    מחזיר webhook ספציפי.
    
    Args:
        id: מזהה ה-webhook
    
    Returns:
        ה-webhook
    """
    client = get_woocommerce_client()
    return client.wcapi.get(f"webhooks/{id}").json()

def update_webhook(id, data):
    """
    מעדכן webhook קיים.
    
    Args:
        id: מזהה ה-webhook
        data: נתוני העדכון
    
    Returns:
        ה-webhook המעודכן
    """
    client = get_woocommerce_client()
    return client.wcapi.put(f"webhooks/{id}", data).json()

def delete_webhook(id):
    """
    מוחק webhook.
    
    Args:
        id: מזהה ה-webhook
    
    Returns:
        תוצאת המחיקה
    """
    client = get_woocommerce_client()
    return client.wcapi.delete(f"webhooks/{id}", params={"force": True}).json()
