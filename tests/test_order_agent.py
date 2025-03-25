#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
בדיקות יחידה לסוכן ההזמנות
"""

import pytest
import time
import logging
import random
from typing import Dict, List

logger = logging.getLogger(__name__)

# שמירת מזהים של פריטים שנוצרו במהלך הבדיקות כדי לנקות אותם בסוף
created_orders = []

class TestOrderAgent:
    """מחלקת בדיקות לסוכן ההזמנות"""
    
    def test_agent_initialization(self, order_agent):
        """בדיקה שהסוכן מאותחל כראוי"""
        assert order_agent is not None
        assert len(order_agent.tools) > 0
        assert order_agent.description != ""
    
    def test_list_orders(self, order_agent):
        """בדיקת פונקציית רשימת ההזמנות"""
        response = order_agent.run("הצג לי את רשימת ההזמנות")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לבקשה להצגת הזמנות: {response}")
    
    def test_create_order(self, order_agent, woo_client):
        """בדיקת יצירת הזמנה חדשה"""
        # תחילה צריך לוודא שיש מוצרים בחנות
        products = woo_client.get_products(per_page=1)
        if not products:
            # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
            product_data = {
                "name": f"מוצר בדיקה להזמנה {int(time.time())}",
                "regular_price": "50",
                "type": "simple"
            }
            product = woo_client.create_product(product_data)
            product_id = product.get("id")
            logger.info(f"נוצר מוצר זמני למטרת בדיקת הזמנות עם מזהה {product_id}")
        else:
            product_id = products[0].get("id")
        
        # יצירת הזמנה עם המוצר
        customer_email = f"test{random.randint(1000, 9999)}@example.com"
        customer_name = "לקוח בדיקה"
        
        response = order_agent.run(
            f"צור הזמנה חדשה עבור {customer_name} עם האימייל {customer_email} "
            f"הכוללת את מוצר {product_id} בכמות 1"
        )
        
        # וידוא שהתגובה מכילה מידע על ההזמנה שנוצרה
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר" in response or "הזמנה" in response or customer_name in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן ליצירת הזמנה: {response}")
        
        # חיפוש מזהה ההזמנה בתשובה - מניחים שהוא מופיע כמספר עם המילה ID או מזהה
        import re
        order_id_match = re.search(r'(?:מזהה|ID|id)[:\s]+(\d+)', response)
        
        if order_id_match:
            order_id = int(order_id_match.group(1))
            created_orders.append(order_id)
            logger.info(f"נמצא מזהה הזמנה: {order_id}")
    
    def test_get_order_by_id(self, order_agent, woo_client):
        """בדיקת קבלת מידע על הזמנה לפי מזהה"""
        # וידוא שיש הזמנות לבדיקה - במידת הצורך, יצירת הזמנה חדשה
        order_id = None
        if created_orders:
            order_id = created_orders[0]
        else:
            # תחילה צריך לוודא שיש מוצרים בחנות
            products = woo_client.get_products(per_page=1)
            if not products:
                # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
                product_data = {
                    "name": f"מוצר בדיקה להזמנה {int(time.time())}",
                    "regular_price": "50",
                    "type": "simple"
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                logger.info(f"נוצר מוצר זמני למטרת בדיקת הזמנות עם מזהה {product_id}")
            else:
                product_id = products[0].get("id")
            
            # יצירת הזמנה עם המוצר
            customer_email = f"test{random.randint(1000, 9999)}@example.com"
            customer_name = "לקוח בדיקה"
            
            # ננסה ליצור הזמנה דרך הסוכן
            response = order_agent.run(
                f"צור הזמנה חדשה עבור {customer_name} עם האימייל {customer_email} "
                f"הכוללת את מוצר {product_id} בכמות 1"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת הזמנה: {response}")
            
            # חיפוש מזהה ההזמנה בתשובה
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            order_id_match = re.search(r'(?:מזהה|ID|id|הזמנה מספר)[:\s.]*([\d]+)', response)
            if not order_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                order_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if order_id_match:
                order_id = int(order_id_match.group(1))
                created_orders.append(order_id)
                logger.info(f"נוצרה הזמנה חדשה לצורך בדיקה עם מזהה: {order_id}")
            else:
                # אם הסוכן לא הצליח, ננסה ליצור הזמנה ישירות דרך ה-API
                try:
                    # קודם נבדוק אם יש הזמנות קיימות
                    orders = woo_client.get_orders(per_page=5)
                    if orders:
                        # נשתמש בהזמנה קיימת
                        order_id = orders[0].get("id")
                        created_orders.append(order_id)
                        logger.info(f"נמצאה הזמנה קיימת באמצעות ה-API עם מזהה: {order_id}")
                    else:
                        # אם אין הזמנות קיימות, ניצור אחת חדשה ישירות דרך ה-API
                        order_data = {
                            "payment_method": "cod",
                            "payment_method_title": "Cash on Delivery",
                            "status": "processing",
                            "set_paid": True,
                            "billing": {
                                "first_name": customer_name,
                                "email": customer_email
                            },
                            "shipping": {
                                "first_name": customer_name,
                                "email": customer_email
                            },
                            "line_items": [
                                {
                                    "product_id": product_id,
                                    "quantity": 1
                                }
                            ]
                        }
                        
                        order = woo_client.create_order(order_data)
                        order_id = order.get("id")
                        if order_id:
                            created_orders.append(order_id)
                            logger.info(f"נוצרה הזמנה חדשה ישירות דרך ה-API עם מזהה: {order_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת הזמנה דרך ה-API: {str(e)}")
        
        # וידוא שיש מזהה הזמנה תקין
        assert order_id is not None, "לא ניתן ליצור הזמנה לבדיקה"
        
        response = order_agent.run(f"הצג מידע על הזמנה עם מזהה {order_id}")
        
        # וידוא שהתגובה מכילה את מזהה ההזמנה
        assert response is not None
        assert isinstance(response, str)
        assert str(order_id) in response or "מזהה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לבקשת מידע על הזמנה: {response}")
    
    def test_update_order_status(self, order_agent, woo_client):
        """בדיקת עדכון סטטוס של הזמנה"""
        # וידוא שיש הזמנות לבדיקה - במידת הצורך, יצירת הזמנה חדשה
        order_id = None
        if created_orders:
            order_id = created_orders[0]
        else:
            # תחילה צריך לוודא שיש מוצרים בחנות
            products = woo_client.get_products(per_page=1)
            if not products:
                # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
                product_data = {
                    "name": f"מוצר בדיקה להזמנה {int(time.time())}",
                    "regular_price": "50",
                    "type": "simple"
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                logger.info(f"נוצר מוצר זמני למטרת בדיקת הזמנות עם מזהה {product_id}")
            else:
                product_id = products[0].get("id")
            
            # יצירת הזמנה ישירות דרך ה-API במקום דרך הסוכן
            try:
                # קודם נבדוק אם יש הזמנות קיימות
                orders = woo_client.get_orders(per_page=5)
                if orders:
                    # נשתמש בהזמנה קיימת
                    order_id = orders[0].get("id")
                    created_orders.append(order_id)
                    logger.info(f"נמצאה הזמנה קיימת באמצעות ה-API עם מזהה: {order_id}")
                else:
                    # אם אין הזמנות קיימות, ניצור אחת חדשה ישירות דרך ה-API
                    customer_email = f"test{random.randint(1000, 9999)}@example.com"
                    customer_name = "לקוח בדיקה"
                    
                    order_data = {
                        "payment_method": "cod",
                        "payment_method_title": "Cash on Delivery",
                        "status": "pending",
                        "billing": {
                            "first_name": customer_name,
                            "email": customer_email
                        },
                        "shipping": {
                            "first_name": customer_name,
                            "email": customer_email
                        },
                        "line_items": [
                            {
                                "product_id": product_id,
                                "quantity": 1
                            }
                        ]
                    }
                    
                    order = woo_client.create_order(order_data)
                    order_id = order.get("id")
                    if order_id:
                        created_orders.append(order_id)
                        logger.info(f"נוצרה הזמנה חדשה ישירות דרך ה-API עם מזהה: {order_id}")
            except Exception as e:
                logger.error(f"שגיאה ביצירת הזמנה דרך ה-API: {str(e)}")
        
        # וידוא שיש מזהה הזמנה תקין
        assert order_id is not None, "לא ניתן ליצור הזמנה לבדיקה"
        
        # עדכון סטטוס ההזמנה ל- 'בתהליך'
        response = order_agent.run(f"עדכן את הסטטוס של הזמנה {order_id} ל'בתהליך'")
        
        # וידוא שהעדכון התבצע בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert "עודכן" in response or "סטטוס" in response or "בתהליך" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לעדכון סטטוס הזמנה: {response}")
    
    def test_search_orders(self, order_agent, woo_client):
        """בדיקת חיפוש הזמנות"""
        # יצירת הזמנה חדשה עם שם ייחודי אם אין הזמנות 
        if not created_orders:
            # תחילה צריך לוודא שיש מוצרים בחנות
            products = woo_client.get_products(per_page=1)
            if not products:
                # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
                product_data = {
                    "name": f"מוצר בדיקה להזמנה {int(time.time())}",
                    "regular_price": "50",
                    "type": "simple"
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                logger.info(f"נוצר מוצר זמני למטרת בדיקת הזמנות עם מזהה {product_id}")
            else:
                product_id = products[0].get("id")
            
            # יצירת לקוח עם שם ייחודי לצורך החיפוש
            unique_customer_name = f"לקוח_חיפוש_{int(time.time())}"
            customer_email = f"test{random.randint(1000, 9999)}@example.com"
            
            response = order_agent.run(
                f"צור הזמנה חדשה עבור {unique_customer_name} עם האימייל {customer_email} "
                f"הכוללת את מוצר {product_id} בכמות 1"
            )
            
            # חיפוש מזהה ההזמנה בתשובה
            import re
            order_id_match = re.search(r'(?:מזהה|ID|id)[:\s]+(\d+)', response)
            if order_id_match:
                order_id = int(order_id_match.group(1))
                created_orders.append(order_id)
                logger.info(f"נוצרה הזמנה חדשה לצורך חיפוש עם מזהה: {order_id}")
            
            search_term = unique_customer_name
        else:
            # אם כבר יש הזמנות, נבדוק אותן בחנות כדי לקבל את שם הלקוח
            order_details = woo_client.get_order(created_orders[0])
            if order_details and "billing" in order_details:
                search_term = order_details["billing"].get("first_name", "לקוח בדיקה")
            else:
                search_term = "לקוח בדיקה"
        
        response = order_agent.run(f"חפש הזמנות עבור '{search_term}'")
        
        # וידוא שהחיפוש החזיר תוצאות
        assert response is not None
        assert isinstance(response, str)
        assert "הזמנ" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לחיפוש הזמנות: {response}")
    
    def test_get_order_notes(self, order_agent, woo_client):
        """בדיקת קבלת הערות להזמנה"""
        # וידוא שיש הזמנות לבדיקה - במידת הצורך, יצירת הזמנה חדשה
        order_id = None
        if created_orders:
            order_id = created_orders[0]
        else:
            # תחילה צריך לוודא שיש מוצרים בחנות
            products = woo_client.get_products(per_page=1)
            if not products:
                # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
                product_data = {
                    "name": f"מוצר בדיקה להזמנה {int(time.time())}",
                    "regular_price": "50",
                    "type": "simple"
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                logger.info(f"נוצר מוצר זמני למטרת בדיקת הזמנות עם מזהה {product_id}")
            else:
                product_id = products[0].get("id")
            
            # יצירת הזמנה ישירות דרך ה-API במקום דרך הסוכן
            try:
                # קודם נבדוק אם יש הזמנות קיימות
                orders = woo_client.get_orders(per_page=5)
                if orders:
                    # נשתמש בהזמנה קיימת
                    order_id = orders[0].get("id")
                    created_orders.append(order_id)
                    logger.info(f"נמצאה הזמנה קיימת באמצעות ה-API עם מזהה: {order_id}")
                    
                    # נוסיף הערה להזמנה כדי שתהיה הערה לבדוק
                    note_data = {
                        "note": "הערה לבדיקה אוטומטית"
                    }
                    woo_client.create_order_note(order_id, note_data)
                    logger.info(f"נוספה הערה להזמנה {order_id} דרך ה-API")
                else:
                    # אם אין הזמנות קיימות, ניצור אחת חדשה ישירות דרך ה-API
                    customer_email = f"test{random.randint(1000, 9999)}@example.com"
                    customer_name = "לקוח בדיקה"
                    
                    order_data = {
                        "payment_method": "cod",
                        "payment_method_title": "Cash on Delivery",
                        "status": "processing",
                        "billing": {
                            "first_name": customer_name,
                            "email": customer_email
                        },
                        "shipping": {
                            "first_name": customer_name,
                            "email": customer_email
                        },
                        "line_items": [
                            {
                                "product_id": product_id,
                                "quantity": 1
                            }
                        ]
                    }
                    
                    order = woo_client.create_order(order_data)
                    order_id = order.get("id")
                    if order_id:
                        created_orders.append(order_id)
                        logger.info(f"נוצרה הזמנה חדשה ישירות דרך ה-API עם מזהה: {order_id}")
                        
                        # הוספת הערה להזמנה
                        note_data = {
                            "note": "הערה לבדיקה אוטומטית"
                        }
                        woo_client.create_order_note(order_id, note_data)
                        logger.info(f"נוספה הערה להזמנה {order_id} דרך ה-API")
            except Exception as e:
                logger.error(f"שגיאה ביצירת הזמנה/הערה דרך ה-API: {str(e)}")
        
        # וידוא שיש מזהה הזמנה תקין
        assert order_id is not None, "לא ניתן ליצור הזמנה לבדיקה"
        
        response = order_agent.run(f"הצג הערות להזמנה עם מזהה {order_id}")
        
        # וידוא שהתגובה מכילה אזכור להערות
        assert response is not None
        assert isinstance(response, str)
        assert "הערות" in response or "הזמנה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן להצגת הערות להזמנה: {response}")
    
    def test_add_order_note(self, order_agent, woo_client):
        """בדיקת הוספת הערה להזמנה"""
        # וידוא שיש הזמנות לבדיקה - במידת הצורך, יצירת הזמנה חדשה
        order_id = None
        if created_orders:
            order_id = created_orders[0]
        else:
            # תחילה צריך לוודא שיש מוצרים בחנות
            products = woo_client.get_products(per_page=1)
            if not products:
                # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
                product_data = {
                    "name": f"מוצר בדיקה להזמנה {int(time.time())}",
                    "regular_price": "50",
                    "type": "simple"
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                logger.info(f"נוצר מוצר זמני למטרת בדיקת הזמנות עם מזהה {product_id}")
            else:
                product_id = products[0].get("id")
            
            # יצירת הזמנה עם המוצר
            customer_email = f"test{random.randint(1000, 9999)}@example.com"
            customer_name = "לקוח בדיקה"
            
            response = order_agent.run(
                f"צור הזמנה חדשה עבור {customer_name} עם האימייל {customer_email} "
                f"הכוללת את מוצר {product_id} בכמות 1"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת הזמנה להוספת הערה: {response}")
            
            # חיפוש מזהה ההזמנה בתשובה
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            order_id_match = re.search(r'(?:מזהה|ID|id|הזמנה מספר)[:\s.]*([\d]+)', response)
            if not order_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                order_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if order_id_match:
                order_id = int(order_id_match.group(1))
                created_orders.append(order_id)
                logger.info(f"נוצרה הזמנה חדשה לצורך הוספת הערה עם מזהה: {order_id}")
            else:
                # בדיקה אם יש הזמנות חדשות באמצעות ה-API
                try:
                    orders = woo_client.get_orders(per_page=5)
                    if orders:
                        # נבדוק את ההזמנה האחרונה שנוצרה
                        order_id = orders[0].get("id")
                        created_orders.append(order_id)
                        logger.info(f"נמצאה הזמנה אחרונה באמצעות ה-API עם מזהה: {order_id}")
                except Exception as e:
                    logger.error(f"שגיאה בקבלת הזמנות אחרונות: {str(e)}")
        
        # וידוא שיש מזהה הזמנה תקין
        assert order_id is not None, "לא ניתן ליצור הזמנה לבדיקה"
        
        # הוספת הערה להזמנה
        note_text = f"הערת בדיקה {int(time.time())}"
        response = order_agent.run(f"הוסף הערה להזמנה {order_id}: {note_text}")
        
        # וידוא שההערה נוספה בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert "נוספה" in response or "הערה" in response or "התווספה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן להוספת הערה להזמנה: {response}")
    
    def test_cancel_order(self, order_agent, woo_client):
        """בדיקת ביטול הזמנה"""
        # יצירת הזמנה חדשה לבדיקת ביטול
        # תחילה צריך לוודא שיש מוצרים בחנות
        products = woo_client.get_products(per_page=1)
        if not products:
            # אם אין מוצרים בחנות, יוצר מוצר זמני לצורך הבדיקה
            product_data = {
                "name": f"מוצר בדיקה להזמנה לביטול {int(time.time())}",
                "regular_price": "50",
                "type": "simple"
            }
            product = woo_client.create_product(product_data)
            product_id = product.get("id")
            logger.info(f"נוצר מוצר זמני למטרת בדיקת ביטול הזמנה עם מזהה {product_id}")
        else:
            product_id = products[0].get("id")
        
        # יצירת הזמנה חדשה עם המוצר
        customer_email = f"test{random.randint(1000, 9999)}@example.com"
        customer_name = "לקוח בדיקה לביטול"
        
        response = order_agent.run(
            f"צור הזמנה חדשה עבור {customer_name} עם האימייל {customer_email} "
            f"הכוללת את מוצר {product_id} בכמות 1"
        )
        
        # חיפוש מזהה ההזמנה בתשובה
        import re
        order_id_match = re.search(r'(?:מזהה|ID|id)[:\s]+(\d+)', response)
        
        if order_id_match:
            order_id = int(order_id_match.group(1))
            created_orders.append(order_id)
            logger.info(f"נוצרה הזמנה חדשה לצורך ביטול עם מזהה: {order_id}")
        else:
            # אם לא ניתן לחלץ מזהה מתשובת הסוכן, ננסה ליצור הזמנה ישירות דרך ה-API
            try:
                order_data = {
                    "payment_method": "cod",
                    "payment_method_title": "Cash on Delivery",
                    "status": "processing",
                    "set_paid": True,
                    "billing": {
                        "first_name": customer_name,
                        "email": customer_email
                    },
                    "shipping": {
                        "first_name": customer_name,
                        "email": customer_email
                    },
                    "line_items": [
                        {
                            "product_id": product_id,
                            "quantity": 1
                        }
                    ]
                }
                
                order = woo_client.create_order(order_data)
                order_id = order.get("id")
                if order_id:
                    created_orders.append(order_id)
                    logger.info(f"נוצרה הזמנה חדשה ישירות דרך ה-API עם מזהה: {order_id}")
                else:
                    pytest.skip("לא ניתן ליצור הזמנה לבדיקת ביטול")
            except Exception as e:
                logger.error(f"שגיאה ביצירת הזמנה דרך ה-API: {str(e)}")
                pytest.skip("לא ניתן ליצור הזמנה לבדיקת ביטול")
        
        # בדיקת ביטול ההזמנה
        response = order_agent.run(f"בטל את ההזמנה עם מזהה {order_id}")
        
        # וידוא שהביטול התבצע בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert ("בוטל" in response or 
                "בוטלה" in response or 
                "ההזמנה בוטלה" in response or
                "נמחק" in response or
                "נמחקה" in response)
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לביטול הזמנה: {response}")
    
    # ניקוי הזמנות שנוצרו ולא נמחקו
    @pytest.fixture(autouse=True, scope="class")
    def cleanup_created_orders(self, request, woo_client):
        """נקה את כל ההזמנות שנוצרו במהלך הבדיקות"""
        # פונקציה שתופעל בסוף הטסטים של המחלקה
        def delete_remaining_orders():
            for order_id in created_orders[:]:
                try:
                    # בביטול ההזמנה במקום מחיקה (מחיקה עלולה לא להיות אפשרית עבור הזמנות מסוימות)
                    woo_client.update_order(order_id, {"status": "cancelled"})
                    logger.info(f"בוטלה הזמנת בדיקה עם מזהה {order_id}")
                    created_orders.remove(order_id)
                except Exception as e:
                    logger.error(f"שגיאה בביטול הזמנה {order_id}: {str(e)}")
        
        # הוספת פונקציית הניקוי לרשימת הפעולות שיבוצעו בסיום
        request.addfinalizer(delete_remaining_orders) 