#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
מחלקת לקוח WooCommerce
----------------------

קובץ זה מגדיר את המחלקה WooCommerceClient שמספקת ממשק נוח
לעבודה עם WooCommerce API.
"""

try:
    from woocommerce import API
except ImportError:
    # מחלקה מדומה למקרה שהחבילה לא מותקנת
    class API:
        def __init__(self, **kwargs):
            self.url = kwargs.get('url')
            self.consumer_key = kwargs.get('consumer_key')
            self.consumer_secret = kwargs.get('consumer_secret')
            self.version = kwargs.get('version')
        
        def get(self, endpoint, **kwargs):
            class Response:
                def json(self):
                    return []
            return Response()
            
        def post(self, endpoint, data=None, **kwargs):
            class Response:
                def json(self):
                    return {"id": 1, **data} if data else {"id": 1}
            return Response()
            
        def put(self, endpoint, data=None, **kwargs):
            class Response:
                def json(self):
                    return {"id": int(endpoint.split('/')[-1]), **data} if data else {"id": int(endpoint.split('/')[-1])}
            return Response()
            
        def delete(self, endpoint, **kwargs):
            class Response:
                def json(self):
                    return {"id": int(endpoint.split('/')[-1]), "deleted": True}
            return Response()

class WooCommerceClient:
    """
    מחלקה שמספקת ממשק נוח לעבודה עם WooCommerce API.
    """
    
    def __init__(self, url, consumer_key, consumer_secret, version="wc/v3"):
        """
        אתחול הלקוח.
        
        Args:
            url: כתובת האתר
            consumer_key: מפתח צרכן
            consumer_secret: סוד צרכן
            version: גרסת ה-API (ברירת מחדל: wc/v3)
        """
        self.wcapi = API(
            url=url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version=version
        )
    
    # מוצרים
    
    def get_products(self, **params):
        """
        מחזיר רשימת מוצרים.
        
        Args:
            **params: פרמטרים לסינון
        
        Returns:
            רשימת המוצרים
        """
        return self.wcapi.get("products", params=params).json()
    
    def get_product(self, product_id):
        """
        מחזיר מוצר לפי מזהה.
        
        Args:
            product_id: מזהה המוצר
        
        Returns:
            המוצר שנמצא
        """
        return self.wcapi.get(f"products/{product_id}").json()
    
    def create_product(self, data):
        """
        יוצר מוצר חדש.
        
        Args:
            data: נתוני המוצר
        
        Returns:
            המוצר שנוצר
        """
        return self.wcapi.post("products", data).json()
    
    def update_product(self, product_id, data):
        """
        מעדכן מוצר קיים.
        
        Args:
            product_id: מזהה המוצר
            data: נתוני המוצר לעדכון
        
        Returns:
            המוצר המעודכן
        """
        return self.wcapi.put(f"products/{product_id}", data).json()
    
    def delete_product(self, product_id, force=True):
        """
        מוחק מוצר קיים.
        
        Args:
            product_id: מזהה המוצר
            force: האם למחוק לצמיתות (ברירת מחדל: True)
        
        Returns:
            תוצאת המחיקה
        """
        return self.wcapi.delete(f"products/{product_id}", params={"force": force}).json()
    
    def search_products(self, search_term, **params):
        """
        מחפש מוצרים לפי מונח חיפוש.
        
        Args:
            search_term: מונח החיפוש
            **params: פרמטרים נוספים לסינון
        
        Returns:
            רשימת המוצרים שנמצאו
        """
        params["search"] = search_term
        return self.get_products(**params)
    
    # הזמנות
    
    def get_orders(self, **params):
        """
        מחזיר רשימת הזמנות.
        
        Args:
            **params: פרמטרים לסינון
        
        Returns:
            רשימת ההזמנות
        """
        return self.wcapi.get("orders", params=params).json()
    
    def get_order(self, order_id):
        """
        מחזיר הזמנה לפי מזהה.
        
        Args:
            order_id: מזהה ההזמנה
        
        Returns:
            ההזמנה שנמצאה
        """
        return self.wcapi.get(f"orders/{order_id}").json()
    
    def create_order(self, data):
        """
        יוצר הזמנה חדשה.
        
        Args:
            data: נתוני ההזמנה
        
        Returns:
            ההזמנה שנוצרה
        """
        return self.wcapi.post("orders", data).json()
    
    def update_order(self, order_id, data):
        """
        מעדכן הזמנה קיימת.
        
        Args:
            order_id: מזהה ההזמנה
            data: נתוני ההזמנה לעדכון
        
        Returns:
            ההזמנה המעודכנת
        """
        return self.wcapi.put(f"orders/{order_id}", data).json()
    
    def delete_order(self, order_id, force=True):
        """
        מוחק הזמנה קיימת.
        
        Args:
            order_id: מזהה ההזמנה
            force: האם למחוק לצמיתות (ברירת מחדל: True)
        
        Returns:
            תוצאת המחיקה
        """
        return self.wcapi.delete(f"orders/{order_id}", params={"force": force}).json()
    
    def search_orders(self, search_term, **params):
        """
        מחפש הזמנות לפי מונח חיפוש.
        
        Args:
            search_term: מונח החיפוש
            **params: פרמטרים נוספים לסינון
        
        Returns:
            רשימת ההזמנות שנמצאו
        """
        params["search"] = search_term
        return self.get_orders(**params)
    
    # קופונים
    
    def get_coupons(self, **params):
        """
        מחזיר רשימת קופונים.
        
        Args:
            **params: פרמטרים לסינון
        
        Returns:
            רשימת הקופונים
        """
        return self.wcapi.get("coupons", params=params).json()
    
    def get_coupon(self, coupon_id):
        """
        מחזיר קופון לפי מזהה.
        
        Args:
            coupon_id: מזהה הקופון
        
        Returns:
            הקופון שנמצא
        """
        return self.wcapi.get(f"coupons/{coupon_id}").json()
    
    def create_coupon(self, data):
        """
        יוצר קופון חדש.
        
        Args:
            data: נתוני הקופון
        
        Returns:
            הקופון שנוצר
        """
        return self.wcapi.post("coupons", data).json()
    
    def update_coupon(self, coupon_id, data):
        """
        מעדכן קופון קיים.
        
        Args:
            coupon_id: מזהה הקופון
            data: נתוני הקופון לעדכון
        
        Returns:
            הקופון המעודכן
        """
        return self.wcapi.put(f"coupons/{coupon_id}", data).json()
    
    def delete_coupon(self, coupon_id, force=True):
        """
        מוחק קופון קיים.
        
        Args:
            coupon_id: מזהה הקופון
            force: האם למחוק לצמיתות (ברירת מחדל: True)
        
        Returns:
            תוצאת המחיקה
        """
        return self.wcapi.delete(f"coupons/{coupon_id}", params={"force": force}).json()
    
    def search_coupons(self, search_term, **params):
        """
        מחפש קופונים לפי מונח חיפוש.
        
        Args:
            search_term: מונח החיפוש
            **params: פרמטרים נוספים לסינון
        
        Returns:
            רשימת הקופונים שנמצאו
        """
        params["search"] = search_term
        return self.get_coupons(**params)
    
    # לקוחות
    
    def get_customers(self, **params):
        """
        מחזיר רשימת לקוחות.
        
        Args:
            **params: פרמטרים לסינון
        
        Returns:
            רשימת הלקוחות
        """
        return self.wcapi.get("customers", params=params).json()
    
    def get_customer(self, customer_id):
        """
        מחזיר לקוח לפי מזהה.
        
        Args:
            customer_id: מזהה הלקוח
        
        Returns:
            הלקוח שנמצא
        """
        return self.wcapi.get(f"customers/{customer_id}").json()
    
    def create_customer(self, data):
        """
        יוצר לקוח חדש.
        
        Args:
            data: נתוני הלקוח
        
        Returns:
            הלקוח שנוצר
        """
        return self.wcapi.post("customers", data).json()
    
    def update_customer(self, customer_id, data):
        """
        מעדכן לקוח קיים.
        
        Args:
            customer_id: מזהה הלקוח
            data: נתוני הלקוח לעדכון
        
        Returns:
            הלקוח המעודכן
        """
        return self.wcapi.put(f"customers/{customer_id}", data).json()
    
    def delete_customer(self, customer_id, force=True):
        """
        מוחק לקוח קיים.
        
        Args:
            customer_id: מזהה הלקוח
            force: האם למחוק לצמיתות (ברירת מחדל: True)
        
        Returns:
            תוצאת המחיקה
        """
        return self.wcapi.delete(f"customers/{customer_id}", params={"force": force}).json()
    
    def search_customers(self, search_term, **params):
        """
        מחפש לקוחות לפי מונח חיפוש.
        
        Args:
            search_term: מונח החיפוש
            **params: פרמטרים נוספים לסינון
        
        Returns:
            רשימת הלקוחות שנמצאו
        """
        params["search"] = search_term
        return self.get_customers(**params)
    
    def get_customer_orders(self, customer_id, **params):
        """
        מחזיר רשימת הזמנות של לקוח מסוים.
        
        Args:
            customer_id: מזהה הלקוח
            **params: פרמטרים נוספים לסינון
        
        Returns:
            רשימת ההזמנות של הלקוח
        """
        params["customer"] = customer_id
        return self.get_orders(**params)
    
    # קטגוריות
    
    def get_categories(self, **params):
        """
        מחזיר רשימת קטגוריות.
        
        Args:
            **params: פרמטרים לסינון
        
        Returns:
            רשימת הקטגוריות
        """
        return self.wcapi.get("products/categories", params=params).json()
    
    def get_category(self, category_id):
        """
        מחזיר קטגוריה לפי מזהה.
        
        Args:
            category_id: מזהה הקטגוריה
        
        Returns:
            הקטגוריה שנמצאה
        """
        return self.wcapi.get(f"products/categories/{category_id}").json()
    
    def create_category(self, data):
        """
        יוצר קטגוריה חדשה.
        
        Args:
            data: נתוני הקטגוריה
        
        Returns:
            הקטגוריה שנוצרה
        """
        return self.wcapi.post("products/categories", data).json()
    
    def update_category(self, category_id, data):
        """
        מעדכן קטגוריה קיימת.
        
        Args:
            category_id: מזהה הקטגוריה
            data: נתוני הקטגוריה לעדכון
        
        Returns:
            הקטגוריה המעודכנת
        """
        return self.wcapi.put(f"products/categories/{category_id}", data).json()
    
    def delete_category(self, category_id, force=True):
        """
        מוחק קטגוריה קיימת.
        
        Args:
            category_id: מזהה הקטגוריה
            force: האם למחוק לצמיתות (ברירת מחדל: True)
        
        Returns:
            תוצאת המחיקה
        """
        return self.wcapi.delete(f"products/categories/{category_id}", params={"force": force}).json()
    
    def search_categories(self, search_term, **params):
        """
        מחפש קטגוריות לפי מונח חיפוש.
        
        Args:
            search_term: מונח החיפוש
            **params: פרמטרים נוספים לסינון
        
        Returns:
            רשימת הקטגוריות שנמצאו
        """
        params["search"] = search_term
        return self.get_categories(**params)
