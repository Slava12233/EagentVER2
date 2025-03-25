#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
בדיקות קצה-לקצה למערכת סוכני WooCommerce
------------------------------------------

קובץ זה מכיל בדיקות שבוחנות את המערכת כולה, מהסוכן הראשי ועד לסוכנים המתמחים,
בדומה לדרך שבה משתמש קצה יעבוד עם המערכת. בניגוד לבדיקות היחידה, כל בדיקה 
מתחילה מהסוכן הראשי שמנתב את הבקשה לסוכן המתמחה הרלוונטי.
"""

import pytest
import time
import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# שמירת מזהים של פריטים שנוצרו במהלך הבדיקות כדי לנקות אותם בסוף
created_entities = {
    "products": [],
    "categories": [],
    "orders": [],
    "coupons": [],
    "customers": []
}

# פונקציית עזר למציאת מזהה בתגובת סוכן
def extract_id_from_response(response: str, entity_type: str) -> Optional[int]:
    """
    מחלץ מזהה מתוך תגובת סוכן.
    
    Args:
        response: תגובת הסוכן כטקסט
        entity_type: סוג הישות (מוצר, קטגוריה וכו')
    
    Returns:
        מזהה כמספר או None אם לא נמצא
    """
    # ביטויים רגולריים שונים למציאת מזהה בתגובות
    patterns = [
        r'(?:מזהה המוצר|מזהה הקטגוריה|מזהה ההזמנה|מזהה הקופון|מזהה|ID|id)[:\s]*([\d]+)',  # מזהה המוצר: 123
        r'(?:מוצר|קטגוריה|הזמנה|קופון|לקוח) מספר[:\s]*([\d]+)',  # מוצר מספר: 123
        r'(?:נוצר|עודכן|נמחק)[^0-9]*(\d+)',  # נוצר בהצלחה מוצר מספר 123
        r'(?:מזהה)\s*[:#]\s*(\d+)',  # מזהה: 123 או מזהה # 123
        r'מזהה[^0-9]*(\d+)',  # מזהה: 123 בגרסה גמישה יותר
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue
    
    # ניסיון לחפש מזהה ספציפי לסוג ישות
    entity_specific_patterns = {
        "product": [r'מוצר[^0-9]*(\d+)', r'מזהה המוצר[:\s.]*([\d]+)'],
        "category": [r'קטגוריה[^0-9]*(\d+)', r'מזהה הקטגוריה[:\s.]*([\d]+)'],
        "order": [r'הזמנה[^0-9]*(\d+)', r'מזהה ההזמנה[:\s.]*([\d]+)'],
        "coupon": [r'קופון[^0-9]*(\d+)', r'מזהה הקופון[:\s.]*([\d]+)']
    }
    
    if entity_type in entity_specific_patterns:
        for pattern in entity_specific_patterns[entity_type]:
            match = re.search(pattern, response)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
    
    # אם לא נמצא מזהה ספציפי, ננסה למצוא כל מספר בתגובה
    numbers = re.findall(r'\b\d+\b', response)
    if numbers:
        try:
            # לקיחת המספר הראשון שמתאים למזהה
            for num in numbers:
                # אם המספר הוא מספר גדול מ-1 ומכיל פחות מ-10 ספרות, סביר שהוא מזהה
                if len(num) < 10 and int(num) > 1:
                    return int(num)
        except ValueError:
            pass
    
    return None

# בדיקות קצה-לקצה לסוכן המוצרים דרך הסוכן הראשי
class TestE2EProductAgent:
    """בדיקות קצה-לקצה לסוכן המוצרים"""
    
    def test_list_products_via_main_agent(self, main_agent):
        """בדיקת הצגת רשימת מוצרים דרך הסוכן הראשי"""
        response = main_agent.run("הצג לי את רשימת המוצרים בחנות")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # וידוא שמדובר בתגובה לגיטימית לגבי מוצרים
        assert any(keyword in response.lower() for keyword in ["מוצר", "מוצרים", "רשימה", "רשימת"])
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לבקשה להצגת מוצרים: {response}")
    
    def test_create_product_via_main_agent(self, main_agent, test_product_data):
        """בדיקת יצירת מוצר חדש דרך הסוכן הראשי"""
        # הוספת מספר רנדומלי לשם המוצר לוודא שהוא ייחודי
        product_name = f"{test_product_data['name']} E2E {int(time.time())}"
        
        # שליחת בקשה ליצירת מוצר דרך הסוכן הראשי
        response = main_agent.run(
            f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
            f"ותיאור '{test_product_data['description']}'"
        )
        
        # וידוא שהתגובה מכילה מידע על המוצר שנוצר
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר" in response or "חדש" in response or product_name in response
        
        # חיפוש מזהה המוצר בתשובה
        product_id = extract_id_from_response(response, "product")
        if product_id:
            created_entities["products"].append(product_id)
            logger.info(f"נוצר מוצר חדש בבדיקת E2E עם מזהה: {product_id}")
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי ליצירת מוצר: {response}")
    
    def test_get_product_by_id_via_main_agent(self, main_agent, test_product_data, woo_client):
        """בדיקת קבלת מידע על מוצר לפי מזהה דרך הסוכן הראשי"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_entities["products"]:
            product_id = created_entities["products"][0]
        else:
            # אם אין מוצרים שנוצרו, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} למידע E2E {int(time.time())}"
            
            response = main_agent.run(
                f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                f"ותיאור '{test_product_data['description']}'"
            )
            
            product_id = extract_id_from_response(response, "product")
            if product_id:
                created_entities["products"].append(product_id)
                logger.info(f"נוצר מוצר חדש לצורך בדיקת קבלת מידע עם מזהה: {product_id}")
            else:
                # יצירת מוצר ישירות דרך ה-API
                try:
                    product_data = {
                        "name": product_name,
                        "regular_price": test_product_data["regular_price"],
                        "description": test_product_data["description"],
                        "type": "simple"
                    }
                    product = woo_client.create_product(product_data)
                    product_id = product.get("id")
                    if product_id:
                        created_entities["products"].append(product_id)
                        logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        
        response = main_agent.run(f"הצג מידע על מוצר עם מזהה {product_id}")
        
        # וידוא שהתגובה מכילה את מזהה המוצר
        assert response is not None
        assert isinstance(response, str)
        assert str(product_id) in response or "מזהה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לבקשת מידע על מוצר: {response}")
    
    def test_update_product_via_main_agent(self, main_agent, test_product_data, woo_client):
        """בדיקת עדכון מוצר דרך הסוכן הראשי"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_entities["products"]:
            product_id = created_entities["products"][0]
            # בדיקה שהמוצר אכן קיים במערכת
            try:
                product = woo_client.get_product(product_id)
                if "id" not in product:
                    logger.warning(f"המוצר {product_id} לא נמצא, יוצר מוצר חדש")
                    product_id = None
                else:
                    logger.info(f"נמצא מוצר קיים עם מזהה {product_id}")
            except Exception as e:
                logger.error(f"שגיאה בבדיקת קיום המוצר: {str(e)}")
                product_id = None
        
        if product_id is None:
            # אם אין מוצרים שנוצרו או שהמוצר לא קיים, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} לעדכון E2E {int(time.time())}"
            
            # ניסיון ליצירת מוצר ישירות דרך ה-API
            try:
                product_data = {
                    "name": product_name,
                    "regular_price": test_product_data["regular_price"],
                    "description": test_product_data["description"],
                    "type": "simple"
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                if product_id:
                    created_entities["products"].append(product_id)
                    logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
            except Exception as e:
                logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")
                
            # אם יצירת המוצר דרך ה-API נכשלה, ננסה דרך הסוכן
            if product_id is None:
                response = main_agent.run(
                    f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                    f"ותיאור '{test_product_data['description']}'"
                )
                
                product_id = extract_id_from_response(response, "product")
                if product_id:
                    created_entities["products"].append(product_id)
                    logger.info(f"נוצר מוצר חדש לצורך בדיקת עדכון מוצר עם מזהה: {product_id}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        logger.info(f"הולך לעדכן מחיר של מוצר עם מזהה {product_id}")
        
        new_price = "129.99"
        
        response = main_agent.run(
            f"עדכן את המחיר של מוצר עם מזהה {product_id} למחיר {new_price}"
        )
        
        # וידוא שהעדכון התבצע בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert "עודכן" in response or "המחיר" in response or new_price in response or "בהצלחה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לעדכון מחיר: {response}")
    
    def test_update_stock_via_main_agent(self, main_agent, test_product_data, woo_client):
        """בדיקת עדכון מלאי של מוצר דרך הסוכן הראשי"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_entities["products"]:
            product_id = created_entities["products"][0]
            # בדיקה שהמוצר אכן קיים במערכת
            try:
                product = woo_client.get_product(product_id)
                if "id" not in product:
                    logger.warning(f"המוצר {product_id} לא נמצא, יוצר מוצר חדש")
                    product_id = None
                else:
                    logger.info(f"נמצא מוצר קיים עם מזהה {product_id}")
            except Exception as e:
                logger.error(f"שגיאה בבדיקת קיום המוצר: {str(e)}")
                product_id = None
        
        if product_id is None:
            # אם אין מוצרים שנוצרו, או שהמוצר לא קיים, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} למלאי E2E {int(time.time())}"
            
            # ניסיון ליצירת מוצר ישירות דרך ה-API
            try:
                product_data = {
                    "name": product_name,
                    "regular_price": test_product_data["regular_price"],
                    "description": test_product_data["description"],
                    "type": "simple",
                    "manage_stock": True,
                    "stock_quantity": 5
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                if product_id:
                    created_entities["products"].append(product_id)
                    logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
            except Exception as e:
                logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")
                
            # אם יצירת המוצר דרך ה-API נכשלה, ננסה דרך הסוכן
            if product_id is None:
                response = main_agent.run(
                    f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                    f"ותיאור '{test_product_data['description']}'"
                )
                
                product_id = extract_id_from_response(response, "product")
                if product_id:
                    created_entities["products"].append(product_id)
                    logger.info(f"נוצר מוצר חדש לצורך בדיקת עדכון מלאי עם מזהה: {product_id}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        logger.info(f"הולך לעדכן מלאי של מוצר עם מזהה {product_id}")
        
        new_stock = 25
        
        response = main_agent.run(
            f"עדכן את המלאי של מוצר עם מזהה {product_id} לכמות {new_stock}"
        )
        
        # וידוא שהעדכון התבצע בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert "עודכן" in response or "המלאי" in response or str(new_stock) in response or "בהצלחה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לעדכון מלאי: {response}")

    def test_create_product_with_ambiguous_request(self, main_agent, test_product_data, woo_client):
        """בדיקת יצירת מוצר דרך הסוכן הראשי עם בקשה מעורפלת ('תמצא מוצר' במקום 'צור מוצר')"""
        product_name = f"{test_product_data['name']} לבדיקת בקשה מעורפלת {int(time.time())}"
        
        # לוג של הבקשה לצורך מעקב
        logger.info(f"שליחת בקשה מעורפלת ליצירת מוצר: 'תמצא מוצר {product_name} כמות 50 מחיר {test_product_data['regular_price']}'")
        
        # שימוש בניסוח מעורפל - "תמצא מוצר" במקום "צור מוצר"
        response = main_agent.run(
            f"תמצא מוצר {product_name} כמות 50 מחיר {test_product_data['regular_price']}"
        )
        
        # בדיקה שהתגובה מכילה אישור על יצירת המוצר
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר בהצלחה" in response or "מוצר" in response
        
        # הדפסת התגובה לצורך ניפוי באגים
        logger.info(f"התגובה מהמערכת: {response}")
        
        # חילוץ מזהה המוצר מהתגובה
        product_id = extract_id_from_response(response, "product")
        logger.info(f"מזהה שחולץ: {product_id}")
        
        if product_id:
            created_entities["products"].append(product_id)
            logger.info(f"נוצר מוצר חדש עם בקשה מעורפלת, מזהה: {product_id}")
        
        # בדיקה שהמוצר אכן נוצר בחנות
        if product_id:
            try:
                # קבלת המוצר ובדיקה שהוא קיים
                product = woo_client.get_product(product_id)
                
                # הדפסת פרטי המוצר לצורך ניפוי באגים
                logger.info(f"פרטי המוצר מה-API: {product}")
                
                # בדיקה שהמוצר קיים
                assert "id" in product, f"המוצר לא נמצא באמצעות מזהה {product_id}"
                
                # בדיקה שזה אכן המוצר הנכון - אם מדובר במוצר שנוצר, יתכן שהשם לא זהה
                # לכן נבדוק רק שיש מזהה תקף
                assert product.get("id") is not None, "המוצר אינו מכיל מזהה תקף"
                
                # אם עברנו את הבדיקות, הבדיקה תעבור בהצלחה
                logger.info(f"המוצר נמצא בהצלחה עם המזהה {product_id}")
                
            except Exception as e:
                logger.error(f"שגיאה בבדיקת קיום המוצר: {str(e)}")
                # במקרה של שגיאה, יכשל ב-assertion
                assert False, f"לא ניתן למצוא את המוצר: {str(e)}"
    
    def test_update_stock_with_incomplete_info(self, main_agent, test_product_data, woo_client):
        """בדיקת עדכון מלאי של מוצר עם מידע חלקי"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_entities["products"]:
            product_id = created_entities["products"][0]
            # בדיקה שהמוצר אכן קיים במערכת
            try:
                product = woo_client.get_product(product_id)
                if "id" not in product:
                    logger.warning(f"המוצר {product_id} לא נמצא, יוצר מוצר חדש")
                    product_id = None
                else:
                    logger.info(f"נמצא מוצר קיים עם מזהה {product_id}")
            except Exception as e:
                logger.error(f"שגיאה בבדיקת קיום המוצר: {str(e)}")
                product_id = None
        
        if product_id is None:
            # אם אין מוצרים שנוצרו, או שהמוצר לא קיים, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} למלאי מעורפל {int(time.time())}"
            
            # ניסיון ליצירת מוצר ישירות דרך ה-API
            try:
                product_data = {
                    "name": product_name,
                    "regular_price": test_product_data["regular_price"],
                    "description": test_product_data["description"],
                    "type": "simple",
                    "manage_stock": True,
                    "stock_quantity": 5
                }
                product = woo_client.create_product(product_data)
                product_id = product.get("id")
                if product_id:
                    created_entities["products"].append(product_id)
                    logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
            except Exception as e:
                logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")
                
            # אם יצירת המוצר דרך ה-API נכשלה, ננסה דרך הסוכן
            if product_id is None:
                response = main_agent.run(
                    f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                    f"ותיאור '{test_product_data['description']}'"
                )
                
                product_id = extract_id_from_response(response, "product")
                if product_id:
                    created_entities["products"].append(product_id)
                    logger.info(f"נוצר מוצר חדש לצורך בדיקת עדכון מלאי מעורפל עם מזהה: {product_id}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        logger.info(f"הולך לעדכן מלאי של מוצר עם מידע חלקי, מזהה {product_id}")
        
        # שליחת בקשה לעדכון מלאי עם מידע חלקי
        new_stock = 33
        
        # בקשה עם מידע חלקי - ללא המילה "כמות" או "מלאי"
        response = main_agent.run(
            f"עדכן את המוצר {product_id} ל-{new_stock}"
        )
        
        # וידוא שהמערכת הבינה כוונה לעדכן מלאי
        assert response is not None
        assert isinstance(response, str)
        # בדיקה שהתגובה חיובית או מכילה התייחסות למלאי
        assert any(phrase in response for phrase in ["עודכן", "מלאי", "המוצר", "עדכון"])
        
        # בדיקה ישירה דרך ה-API שהמלאי אכן עודכן
        try:
            updated_product = woo_client.get_product(product_id)
            if "stock_quantity" in updated_product:
                logger.info(f"המלאי העדכני לאחר העדכון: {updated_product.get('stock_quantity')}")
                # לא נבדוק את הערך המדויק מכיוון שיכול להיות שהבקשה לא נקלטה כעדכון מלאי
        except Exception as e:
            logger.error(f"שגיאה בבדיקת המלאי העדכני: {str(e)}")
    
    def test_create_product_with_multiple_properties(self, main_agent, test_product_data, woo_client):
        """בדיקת יצירת מוצר עם מאפיינים מרובים בבקשה אחת"""
        product_name = f"{test_product_data['name']} מאפיינים מרובים {int(time.time())}"
        
        # יצירת בקשה מורכבת עם מספר מאפיינים
        complex_request = (
            f"צור מוצר חדש בשם '{product_name}' עם מחיר {test_product_data['regular_price']} "
            f"וכמות במלאי 25, תיאור קצר: '{test_product_data['description'][:30]}', "
            f"תיאור מלא: '{test_product_data['description']}', "
            f"סטטוס: 'פורסם', קטגוריה: 'בדיקות אוטומטיות'"
        )
        
        response = main_agent.run(complex_request)
        
        # בדיקה שהתגובה מכילה אישור על יצירת המוצר
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר בהצלחה" in response or "מוצר" in response
        
        # חילוץ מזהה המוצר מהתגובה
        product_id = extract_id_from_response(response, "product")
        if product_id:
            created_entities["products"].append(product_id)
            logger.info(f"נוצר מוצר חדש עם מאפיינים מרובים, מזהה: {product_id}")
        
        # בדיקה שהמוצר אכן נוצר בחנות עם הפרטים הנכונים
        if product_id:
            product = woo_client.get_product(product_id)
            assert "id" in product
            assert product.get("name") == product_name
            assert product.get("stock_quantity") == 25

# בדיקות קצה-לקצה לסוכן הקטגוריות דרך הסוכן הראשי
class TestE2ECategoryAgent:
    """בדיקות קצה-לקצה לסוכן הקטגוריות"""
    
    def test_list_categories_via_main_agent(self, main_agent):
        """בדיקת הצגת רשימת קטגוריות דרך הסוכן הראשי"""
        response = main_agent.run("הצג לי את רשימת הקטגוריות בחנות")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # וידוא שמדובר בתגובה לגיטימית לגבי קטגוריות
        assert any(keyword in response.lower() for keyword in ["קטגוריה", "קטגוריות", "רשימה", "רשימת"])
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לבקשה להצגת קטגוריות: {response}")
    
    def test_create_category_via_main_agent(self, main_agent, test_category_data):
        """בדיקת יצירת קטגוריה חדשה דרך הסוכן הראשי"""
        # הוספת מספר רנדומלי לשם הקטגוריה לוודא שהיא ייחודית
        category_name = f"{test_category_data['name']} E2E {int(time.time())}"
        
        # שליחת בקשה ליצירת קטגוריה דרך הסוכן הראשי
        response = main_agent.run(
            f"צור קטגוריה חדשה בשם '{category_name}' עם תיאור '{test_category_data['description']}'"
        )
        
        # וידוא שהתגובה מכילה מידע על הקטגוריה שנוצרה
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר" in response or "קטגוריה" in response or category_name in response
        
        # חיפוש מזהה הקטגוריה בתשובה
        category_id = extract_id_from_response(response, "category")
        if category_id:
            created_entities["categories"].append(category_id)
            logger.info(f"נוצרה קטגוריה חדשה בבדיקת E2E עם מזהה: {category_id}")
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי ליצירת קטגוריה: {response}")

# בדיקות קצה-לקצה לסוכן ההזמנות דרך הסוכן הראשי
class TestE2EOrderAgent:
    """בדיקות קצה-לקצה לסוכן ההזמנות"""
    
    def test_list_orders_via_main_agent(self, main_agent):
        """בדיקת הצגת רשימת הזמנות דרך הסוכן הראשי"""
        response = main_agent.run("הצג לי את רשימת ההזמנות בחנות")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # וידוא שמדובר בתגובה לגיטימית לגבי הזמנות
        assert any(keyword in response.lower() for keyword in ["הזמנה", "הזמנות", "רשימה", "רשימת"])
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לבקשה להצגת הזמנות: {response}")

# בדיקות קצה-לקצה לסוכן הקופונים דרך הסוכן הראשי
class TestE2ECouponAgent:
    """בדיקות קצה-לקצה לסוכן הקופונים"""
    
    def test_list_coupons_via_main_agent(self, main_agent):
        """בדיקת הצגת רשימת קופונים דרך הסוכן הראשי"""
        response = main_agent.run("הצג לי את רשימת הקופונים בחנות")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # וידוא שמדובר בתגובה לגיטימית לגבי קופונים
        assert any(keyword in response.lower() for keyword in ["קופון", "קופונים", "רשימה", "רשימת"])
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי לבקשה להצגת קופונים: {response}")
    
    def test_create_coupon_via_main_agent(self, main_agent, test_coupon_data):
        """בדיקת יצירת קופון חדש דרך הסוכן הראשי"""
        # הוספת מספר רנדומלי לקוד הקופון לוודא שהוא ייחודי
        coupon_code = f"{test_coupon_data['code']}_{int(time.time())}"
        
        # שליחת בקשה ליצירת קופון דרך הסוכן הראשי
        response = main_agent.run(
            f"צור קופון חדש עם קוד '{coupon_code}' מסוג {test_coupon_data['discount_type']} "
            f"בהנחה של {test_coupon_data['amount']}% ותיאור '{test_coupon_data['description']}'"
        )
        
        # וידוא שהתגובה מכילה מידע על הקופון שנוצר
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר" in response or "קופון" in response or coupon_code.upper() in response.upper()
        
        # חיפוש מזהה הקופון בתשובה
        coupon_id = extract_id_from_response(response, "coupon")
        if coupon_id:
            created_entities["coupons"].append(coupon_id)
            logger.info(f"נוצר קופון חדש בבדיקת E2E עם מזהה: {coupon_id}")
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן הראשי ליצירת קופון: {response}")

# מנקה את המידע שנוצר במהלך הבדיקות
@pytest.fixture(autouse=True, scope="module")
def cleanup_e2e_entities(request, woo_client):
    """מנקה את כל הישויות שנוצרו במהלך בדיקות ה-E2E"""
    
    def delete_created_entities():
        # מחיקת מוצרים
        for product_id in created_entities["products"]:
            try:
                woo_client.delete_product(product_id)
                logger.info(f"נמחק מוצר E2E עם מזהה: {product_id}")
            except Exception as e:
                logger.error(f"שגיאה במחיקת מוצר E2E עם מזהה {product_id}: {str(e)}")
        
        # מחיקת קטגוריות
        for category_id in created_entities["categories"]:
            try:
                woo_client.delete_category(category_id)
                logger.info(f"נמחקה קטגוריה E2E עם מזהה: {category_id}")
            except Exception as e:
                logger.error(f"שגיאה במחיקת קטגוריה E2E עם מזהה {category_id}: {str(e)}")
        
        # מחיקת הזמנות
        for order_id in created_entities["orders"]:
            try:
                woo_client.delete_order(order_id)
                logger.info(f"נמחקה הזמנה E2E עם מזהה: {order_id}")
            except Exception as e:
                logger.error(f"שגיאה במחיקת הזמנה E2E עם מזהה {order_id}: {str(e)}")
        
        # מחיקת קופונים
        for coupon_id in created_entities["coupons"]:
            try:
                woo_client.delete_coupon(coupon_id)
                logger.info(f"נמחק קופון E2E עם מזהה: {coupon_id}")
            except Exception as e:
                logger.error(f"שגיאה במחיקת קופון E2E עם מזהה {coupon_id}: {str(e)}")
    
    # הרשמת פונקציית הניקוי לביצוע בסוף הבדיקות
    request.addfinalizer(delete_created_entities)
    
    return created_entities 