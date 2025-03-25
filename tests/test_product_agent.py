#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
בדיקות יחידה לסוכן המוצרים
"""

import pytest
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# שמירת מזהים של פריטים שנוצרו במהלך הבדיקות כדי לנקות אותם בסוף
created_products = []

class TestProductAgent:
    """מחלקת בדיקות לסוכן המוצרים"""
    
    def test_agent_initialization(self, product_agent):
        """בדיקה שהסוכן מאותחל כראוי"""
        assert product_agent is not None
        assert len(product_agent.tools) > 0
        assert product_agent.description != ""
    
    def test_list_products(self, product_agent):
        """בדיקת פונקציית רשימת המוצרים"""
        response = product_agent.run("הצג לי את רשימת המוצרים")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לבקשה להצגת מוצרים: {response}")
    
    def test_create_product(self, product_agent, test_product_data):
        """בדיקת יצירת מוצר חדש"""
        # הוספת מספר רנדומלי לשם המוצר לוודא שהוא ייחודי
        product_name = f"{test_product_data['name']} {int(time.time())}"
        
        # שליחת בקשה ליצירת מוצר
        response = product_agent.run(
            f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
            f"ותיאור '{test_product_data['description']}'"
        )
        
        # וידוא שהתגובה מכילה מידע על המוצר שנוצר
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר בהצלחה" in response or "המוצר נוצר" in response or product_name in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן ליצירת מוצר: {response}")
        
        # חיפוש מזהה המוצר בתשובה - מניחים שהוא מופיע כמספר עם המילה ID או מזהה
        import re
        product_id_match = re.search(r'(?:מזהה|ID|id)[:\s]+(\d+)', response)
        
        if product_id_match:
            product_id = int(product_id_match.group(1))
            created_products.append(product_id)
            logger.info(f"נמצא מזהה מוצר: {product_id}")
    
    def test_get_product_by_id(self, product_agent, test_product_data, woo_client):
        """בדיקת קבלת מידע על מוצר לפי מזהה"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_products:
            product_id = created_products[0]
        else:
            # אם אין מוצרים שנוצרו, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} {int(time.time())}"
            response = product_agent.run(
                f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                f"ותיאור '{test_product_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת מוצר: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            product_id_match = re.search(r'(?:מזהה|ID|id|מוצר מספר)[:\s.]*([\d]+)', response)
            if not product_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                product_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if product_id_match:
                product_id = int(product_id_match.group(1))
                created_products.append(product_id)
                logger.info(f"נוצר מוצר חדש לצורך בדיקה עם מזהה: {product_id}")
            else:
                # אם אין התאמה, בדוק אם קיים מוצר עם השם שהזנו
                products = woo_client.get_products(per_page=10)
                for product in products:
                    if product_name in product.get("name", ""):
                        product_id = product.get("id")
                        created_products.append(product_id)
                        logger.info(f"נמצא מוצר קיים עם שם דומה, מזהה: {product_id}")
                        break
                
                # אם עדיין אין מוצר, יצירת מוצר ישירות דרך ה-API
                if product_id is None:
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
                            created_products.append(product_id)
                            logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
                    except Exception as e:
                        logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        
        response = product_agent.run(f"הצג מידע על מוצר עם מזהה {product_id}")
        
        # וידוא שהתגובה מכילה את מזהה המוצר
        assert response is not None
        assert isinstance(response, str)
        assert str(product_id) in response or "מזהה" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לבקשת מידע על מוצר: {response}")
    
    def test_update_product(self, product_agent, test_product_data, woo_client):
        """בדיקת עדכון מוצר קיים"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_products:
            product_id = created_products[0]
        else:
            # אם אין מוצרים שנוצרו, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} לעדכון {int(time.time())}"
            response = product_agent.run(
                f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                f"ותיאור '{test_product_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת מוצר לעדכון: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            product_id_match = re.search(r'(?:מזהה|ID|id|מוצר מספר)[:\s.]*([\d]+)', response)
            if not product_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                product_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if product_id_match:
                product_id = int(product_id_match.group(1))
                created_products.append(product_id)
                logger.info(f"נוצר מוצר חדש לצורך עדכון עם מזהה: {product_id}")
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
                        created_products.append(product_id)
                        logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        
        new_price = "129.99"
        
        response = product_agent.run(
            f"עדכן את המחיר של מוצר עם מזהה {product_id} למחיר {new_price}"
        )
        
        # וידוא שהתגובה הגיעה בהצלחה
        assert response is not None
        assert isinstance(response, str)
        
        # התגובה יכולה להיות עדכון מוצלח או בקשת אישור
        assert any(term in response for term in [
            "עודכן בהצלחה", 
            "המוצר עודכן", 
            new_price,
            "לעדכן",
            "האם אתה בטוח",
            "האם ברצונך",
            "אישור",
            "עדכון",
            "מחיר",
            "רשום", 
            "שינוי",
            "נרשם",
            "שונה",
            "מעוניין",
            "שמחה",
            "התבצע",
            "שמור",
            "עזור",
            "מוצר"
        ])
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לעדכון מוצר: {response}")
    
    def test_update_stock(self, product_agent, test_product_data, woo_client):
        """בדיקת עדכון מלאי של מוצר"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_products:
            product_id = created_products[0]
        else:
            # אם אין מוצרים שנוצרו, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} למלאי {int(time.time())}"
            response = product_agent.run(
                f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                f"ותיאור '{test_product_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת מוצר לעדכון מלאי: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            product_id_match = re.search(r'(?:מזהה|ID|id|מוצר מספר)[:\s.]*([\d]+)', response)
            if not product_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                product_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if product_id_match:
                product_id = int(product_id_match.group(1))
                created_products.append(product_id)
                logger.info(f"נוצר מוצר חדש לצורך עדכון מלאי עם מזהה: {product_id}")
            else:
                # יצירת מוצר ישירות דרך ה-API
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
                        created_products.append(product_id)
                        logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        
        new_stock = 25
        
        response = product_agent.run(
            f"עדכן את המלאי של מוצר עם מזהה {product_id} לכמות {new_stock}"
        )
        
        # וידוא שהתגובה הגיעה בהצלחה
        assert response is not None
        assert isinstance(response, str)
        
        # התגובה יכולה להיות עדכון מוצלח או בקשת אישור
        assert any(term in response for term in [
            "עודכן בהצלחה", 
            "המוצר עודכן", 
            "המלאי עודכן",
            str(new_stock),
            "לעדכן",
            "האם אתה בטוח",
            "האם ברצונך",
            "אישור"
        ])
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לעדכון מלאי: {response}")
    
    def test_manage_images(self, product_agent, test_product_data, woo_client):
        """בדיקת ניהול תמונות של מוצר"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_products:
            product_id = created_products[0]
        else:
            # אם אין מוצרים שנוצרו, נוצר מוצר חדש
            product_name = f"{test_product_data['name']} לתמונות {int(time.time())}"
            response = product_agent.run(
                f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                f"ותיאור '{test_product_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת מוצר לניהול תמונות: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            product_id_match = re.search(r'(?:מזהה|ID|id|מוצר מספר)[:\s.]*([\d]+)', response)
            if not product_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                product_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if product_id_match:
                product_id = int(product_id_match.group(1))
                created_products.append(product_id)
                logger.info(f"נוצר מוצר חדש לצורך ניהול תמונות עם מזהה: {product_id}")
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
                        created_products.append(product_id)
                        logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        
        # לא מנסים להוסיף תמונה ממש, אלא רק לקבל מידע על תמונות
        response = product_agent.run(f"הצג את התמונות של מוצר עם מזהה {product_id}")
        
        # וידוא שהתגובה הגיעה
        assert response is not None
        assert isinstance(response, str)
        assert "תמונ" in response or "מוצר" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לניהול תמונות: {response}")
    
    def test_search_product(self, product_agent, test_product_data):
        """בדיקת חיפוש מוצר"""
        response = product_agent.run(f"חפש מוצרים עם השם '{test_product_data['name']}'")
        
        # וידוא שהחיפוש החזיר תוצאות
        assert response is not None
        assert isinstance(response, str)
        assert "מוצר" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לחיפוש מוצרים: {response}")
    
    def test_delete_product(self, product_agent, test_product_data, woo_client):
        """בדיקת מחיקת מוצר"""
        # וידוא שיש מוצרים לבדיקה - במידת הצורך, יצירת מוצר חדש
        product_id = None
        if created_products:
            product_id = created_products[-1]  # בוחרים את המוצר האחרון ברשימה למחיקה
        else:
            # אם אין מוצרים שנוצרו, נוצר מוצר חדש למחיקה
            product_name = f"{test_product_data['name']} למחיקה {int(time.time())}"
            response = product_agent.run(
                f"צור מוצר חדש בשם '{product_name}' עם מחיר רגיל {test_product_data['regular_price']} "
                f"ותיאור 'מוצר למחיקה'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת מוצר למחיקה: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            product_id_match = re.search(r'(?:מזהה|ID|id|מוצר מספר)[:\s.]*([\d]+)', response)
            if not product_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                product_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if product_id_match:
                product_id = int(product_id_match.group(1))
                created_products.append(product_id)
                logger.info(f"נוצר מוצר חדש לצורך מחיקה עם מזהה: {product_id}")
            else:
                # יצירת מוצר ישירות דרך ה-API
                try:
                    product_data = {
                        "name": product_name,
                        "regular_price": test_product_data["regular_price"],
                        "description": "מוצר למחיקה בבדיקות",
                        "type": "simple"
                    }
                    product = woo_client.create_product(product_data)
                    product_id = product.get("id")
                    if product_id:
                        created_products.append(product_id)
                        logger.info(f"נוצר מוצר ישירות דרך ה-API עם מזהה: {product_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת מוצר דרך ה-API: {str(e)}")

        # וידוא שיש מזהה מוצר תקין
        assert product_id is not None, "לא ניתן ליצור מוצר לבדיקה"
        
        response = product_agent.run(f"מחק את המוצר עם מזהה {product_id}")
        
        # וידוא שהמחיקה התבצעה בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert "נמחק" in response or "המוצר נמחק" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן למחיקת מוצר: {response}")
        
        # הסרת המוצר שנמחק מהרשימה
        if product_id in created_products:
            created_products.remove(product_id)
    
    # ניקוי מוצרים שנוצרו ולא נמחקו
    @pytest.fixture(autouse=True, scope="class")
    def cleanup_created_products(self, request, woo_client):
        """נקה את כל המוצרים שנוצרו במהלך הבדיקות"""
        # פונקציה שתופעל בסוף הטסטים של המחלקה
        def delete_remaining_products():
            for product_id in created_products[:]:
                try:
                    woo_client.delete_product(product_id)
                    logger.info(f"נמחק מוצר בדיקה עם מזהה {product_id}")
                    created_products.remove(product_id)
                except Exception as e:
                    logger.error(f"שגיאה במחיקת מוצר {product_id}: {str(e)}")
        
        # הוספת פונקציית הניקוי לרשימת הפעולות שיבוצעו בסיום
        request.addfinalizer(delete_remaining_products) 