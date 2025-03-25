#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
פיקסטורות משותפות לבדיקת כל הסוכנים
"""

import os
import pytest
from dotenv import load_dotenv
from openai import OpenAI
from api.woocommerce_client import WooCommerceClient
from agents.main_agent import MainAgent
from agents.product_agent import create_product_agent
from agents.order_agent import create_order_agent
from agents.category_agent import create_category_agent
from agents.coupon_agent import create_coupon_agent
from agents.customer_agent import create_customer_agent
from agents.report_agent import create_report_agent
from agents.settings_agent import create_settings_agent
from config import get_openai_config, get_woocommerce_config
import logging

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# טעינת משתני הסביבה
load_dotenv()

# פיקסטורה ללקוח OpenAI
@pytest.fixture(scope="session")
def openai_client():
    """יצירת לקוח OpenAI לבדיקות"""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            config = get_openai_config()
            api_key = config.get("api_key")
        
        if not api_key:
            pytest.skip("חסר מפתח API של OpenAI")
        
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"שגיאה ביצירת לקוח OpenAI: {str(e)}")
        pytest.skip(f"שגיאה ביצירת לקוח OpenAI: {str(e)}")

# פיקסטורה ללקוח WooCommerce
@pytest.fixture(scope="session")
def woo_client():
    """יצירת לקוח WooCommerce לבדיקות"""
    try:
        woo_config = get_woocommerce_config()
        
        url = woo_config.get("url")
        consumer_key = woo_config.get("consumer_key")
        consumer_secret = woo_config.get("consumer_secret")
        
        if not all([url, consumer_key, consumer_secret]):
            pytest.skip("חסרות הגדרות WooCommerce")
        
        client = WooCommerceClient(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret
        )
        return client
    except Exception as e:
        logger.error(f"שגיאה ביצירת לקוח WooCommerce: {str(e)}")
        pytest.skip(f"שגיאה ביצירת לקוח WooCommerce: {str(e)}")

# פיקסטורות לסוכנים השונים
@pytest.fixture
def product_agent(openai_client, woo_client):
    """יצירת סוכן מוצרים לבדיקות"""
    agent = create_product_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def order_agent(openai_client, woo_client):
    """יצירת סוכן הזמנות לבדיקות"""
    agent = create_order_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def category_agent(openai_client, woo_client):
    """יצירת סוכן קטגוריות לבדיקות"""
    agent = create_category_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def coupon_agent(openai_client, woo_client):
    """יצירת סוכן קופונים לבדיקות"""
    agent = create_coupon_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def customer_agent(openai_client, woo_client):
    """יצירת סוכן לקוחות לבדיקות"""
    agent = create_customer_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def report_agent(openai_client, woo_client):
    """יצירת סוכן דוחות לבדיקות"""
    agent = create_report_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def settings_agent(openai_client, woo_client):
    """יצירת סוכן הגדרות לבדיקות"""
    agent = create_settings_agent(openai_client, woo_client=woo_client)
    return agent

@pytest.fixture
def main_agent(openai_client, woo_client):
    """יצירת סוכן ראשי לבדיקות"""
    from agents.main_agent import create_agent
    agent = create_agent(openai_client, woo_client=woo_client)
    return agent

# פיקסטורות לנתוני בדיקה
@pytest.fixture
def test_product_data():
    """נתוני מוצר לבדיקות"""
    return {
        "name": "מוצר בדיקה",
        "description": "תיאור מפורט למוצר בדיקה",
        "short_description": "תיאור קצר",
        "regular_price": "99.99",
        "categories": [{"name": "קטגוריית בדיקה"}],
        "stock_quantity": 10
    }

@pytest.fixture
def test_category_data():
    """נתוני קטגוריה לבדיקות"""
    return {
        "name": "קטגוריית בדיקה",
        "description": "תיאור לקטגוריית בדיקה"
    }

@pytest.fixture
def test_coupon_data():
    """נתוני קופון לבדיקות"""
    return {
        "code": "TESTCOUPON",
        "discount_type": "percent",
        "amount": "10",
        "description": "קופון בדיקה"
    }

@pytest.fixture
def test_customer_data():
    """נתוני לקוח לבדיקות"""
    return {
        "email": "test@example.com",
        "first_name": "לקוח",
        "last_name": "בדיקה",
        "username": "testcustomer",
        "password": "password123"
    }

# מחיקת נתוני בדיקה לאחר הטסטים
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data(request, woo_client):
    """מוחק נתוני בדיקה שנוצרו במהלך הריצה"""
    # מה שיקרה אחרי הטסטים
    def cleanup():
        if not woo_client:
            return
            
        try:
            # מחיקת מוצרי בדיקה
            products = woo_client.get_products(search="מוצר בדיקה")
            for product in products:
                if "מוצר בדיקה" in product.get("name", ""):
                    woo_client.delete_product(product["id"])
            
            # מחיקת קטגוריות בדיקה
            categories = woo_client.get_categories(search="קטגוריית בדיקה")
            for category in categories:
                if "קטגוריית בדיקה" in category.get("name", ""):
                    woo_client.delete_category(category["id"])
                    
            # מחיקת קופוני בדיקה
            coupons = woo_client.get_coupons()
            for coupon in coupons:
                if coupon.get("code", "").startswith("TEST"):
                    woo_client.delete_coupon(coupon["id"])
                    
            # מחיקת לקוחות בדיקה
            customers = woo_client.get_customers(email="test@example.com")
            for customer in customers:
                woo_client.delete_customer(customer["id"])
                
        except Exception as e:
            logger.error(f"שגיאה בניקוי נתוני בדיקה: {str(e)}")
    
    # רשום את פונקציית הניקוי להפעלה בסיום
    request.addfinalizer(cleanup) 