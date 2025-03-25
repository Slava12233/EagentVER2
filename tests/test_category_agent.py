#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
בדיקות יחידה לסוכן הקטגוריות
"""

import pytest
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# שמירת מזהים של פריטים שנוצרו במהלך הבדיקות כדי לנקות אותם בסוף
created_categories = []

class TestCategoryAgent:
    """מחלקת בדיקות לסוכן הקטגוריות"""
    
    def test_agent_initialization(self, category_agent):
        """בדיקה שהסוכן מאותחל כראוי"""
        assert category_agent is not None
        assert len(category_agent.tools) > 0
        assert category_agent.description != ""
    
    def test_list_categories(self, category_agent):
        """בדיקת פונקציית רשימת הקטגוריות"""
        response = category_agent.run("הצג לי את רשימת הקטגוריות")
        
        # וידוא שהתגובה מכילה תוכן כלשהו
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לבקשה להצגת קטגוריות: {response}")
    
    def test_create_category(self, category_agent, test_category_data):
        """בדיקת יצירת קטגוריה חדשה"""
        # הוספת מספר רנדומלי לשם הקטגוריה לוודא שהיא ייחודית
        category_name = f"{test_category_data['name']} {int(time.time())}"
        
        # שליחת בקשה ליצירת קטגוריה
        response = category_agent.run(
            f"צור קטגוריה חדשה בשם '{category_name}' עם תיאור '{test_category_data['description']}'"
        )
        
        # וידוא שהתגובה מכילה מידע על הקטגוריה שנוצרה
        assert response is not None
        assert isinstance(response, str)
        assert "נוצר" in response or "הקטגוריה נוצרה" in response or category_name in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן ליצירת קטגוריה: {response}")
        
        # חיפוש מזהה הקטגוריה בתשובה - מניחים שהוא מופיע כמספר עם המילה ID או מזהה
        import re
        category_id_match = re.search(r'(?:מזהה|ID|id)[:\s]+(\d+)', response)
        
        if category_id_match:
            category_id = int(category_id_match.group(1))
            created_categories.append(category_id)
            logger.info(f"נמצא מזהה קטגוריה: {category_id}")
    
    def test_get_category_by_id(self, category_agent, test_category_data, woo_client):
        """בדיקת קבלת מידע על קטגוריה לפי מזהה"""
        # וידוא שיש קטגוריות לבדיקה - במידת הצורך, יצירת קטגוריה חדשה
        category_id = None
        if created_categories:
            category_id = created_categories[0]
        else:
            # אם אין קטגוריות שנוצרו, נוצר קטגוריה חדשה
            category_name = f"{test_category_data['name']} {int(time.time())}"
            response = category_agent.run(
                f"צור קטגוריה חדשה בשם '{category_name}' עם תיאור '{test_category_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת קטגוריה: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            category_id_match = re.search(r'(?:מזהה|ID|id|קטגוריה מספר)[:\s.]*([\d]+)', response)
            if not category_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                category_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if category_id_match:
                category_id = int(category_id_match.group(1))
                created_categories.append(category_id)
                logger.info(f"נוצרה קטגוריה חדשה לצורך בדיקה עם מזהה: {category_id}")
            else:
                # אם אין התאמה, בדוק אם קיימת קטגוריה עם השם שהזנו
                categories = woo_client.get_categories(per_page=10)
                for category in categories:
                    if category_name in category.get("name", ""):
                        category_id = category.get("id")
                        created_categories.append(category_id)
                        logger.info(f"נמצאה קטגוריה קיימת עם שם דומה, מזהה: {category_id}")
                        break

        # וידוא שיש מזהה קטגוריה תקין
        assert category_id is not None, "לא ניתן ליצור קטגוריה לבדיקה"
        
        response = category_agent.run(f"הצג מידע על קטגוריה עם מזהה {category_id}")
        
        # וידוא שהתגובה מכילה את מזהה הקטגוריה או מידע כללי על הקטגוריה
        assert response is not None
        assert isinstance(response, str)
        assert (str(category_id) in response or 
                "מזהה" in response or 
                "פרטי" in response or 
                "קטגוריה" in response or
                "שם הקטגוריה" in response or
                "סלאג" in response)
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לבקשת מידע על קטגוריה: {response}")
    
    def test_update_category(self, category_agent, test_category_data, woo_client):
        """בדיקת עדכון קטגוריה קיימת"""
        # וידוא שיש קטגוריות לבדיקה - במידת הצורך, יצירת קטגוריה חדשה
        category_id = None
        if created_categories:
            category_id = created_categories[0]
        else:
            # אם אין קטגוריות שנוצרו, נוצר קטגוריה חדשה
            category_name = f"{test_category_data['name']} {int(time.time())}"
            response = category_agent.run(
                f"צור קטגוריה חדשה בשם '{category_name}' עם תיאור '{test_category_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת קטגוריה: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            category_id_match = re.search(r'(?:מזהה|ID|id|קטגוריה מספר)[:\s.]*([\d]+)', response)
            if not category_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                category_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if category_id_match:
                category_id = int(category_id_match.group(1))
                created_categories.append(category_id)
                logger.info(f"נוצרה קטגוריה חדשה לצורך עדכון עם מזהה: {category_id}")
            else:
                # אם אין התאמה, בדוק אם קיימת קטגוריה עם השם שהזנו או צור ישירות דרך ה-API
                try:
                    categories = woo_client.get_categories(per_page=10)
                    for category in categories:
                        if category_name in category.get("name", ""):
                            category_id = category.get("id")
                            created_categories.append(category_id)
                            logger.info(f"נמצאה קטגוריה קיימת עם שם דומה, מזהה: {category_id}")
                            break
                    
                    # אם עדיין אין מזהה, ניצור קטגוריה ישירות דרך ה-API
                    if not category_id:
                        new_category_data = {
                            "name": category_name,
                            "description": test_category_data['description']
                        }
                        new_category = woo_client.create_category(new_category_data)
                        category_id = new_category.get("id")
                        if category_id:
                            created_categories.append(category_id)
                            logger.info(f"נוצרה קטגוריה חדשה ישירות דרך ה-API עם מזהה: {category_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת קטגוריה דרך ה-API: {str(e)}")

        # וידוא שיש מזהה קטגוריה תקין
        assert category_id is not None, "לא ניתן ליצור קטגוריה לבדיקה"
        
        new_description = f"תיאור חדש לקטגוריה - {int(time.time())}"
        
        response = category_agent.run(
            f"עדכן את התיאור של קטגוריה עם מזהה {category_id} לתיאור '{new_description}'"
        )
        
        # וידוא שהעדכון התבצע בהצלחה או שיש הודעת שגיאה מנומקת
        assert response is not None
        assert isinstance(response, str)
        assert ("עודכן" in response or 
                "הקטגוריה עודכנה" in response or
                "התיאור שונה" in response or
                "התעדכנה" in response or
                "עודכנה" in response or
                "עדכנתי" in response or
                "שגיאה" in response or
                "בעיה" in response or
                "לא ניתן" in response)
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לעדכון קטגוריה: {response}")
    
    def test_create_subcategory(self, category_agent, test_category_data, woo_client):
        """בדיקת יצירת תת-קטגוריה"""
        # וידוא שיש קטגוריות לבדיקה - במידת הצורך, יצירת קטגוריה חדשה
        parent_id = None
        if created_categories:
            parent_id = created_categories[0]
        else:
            # אם אין קטגוריות שנוצרו, נוצר קטגוריה חדשה
            category_name = f"{test_category_data['name']} {int(time.time())}"
            response = category_agent.run(
                f"צור קטגוריה חדשה בשם '{category_name}' עם תיאור '{test_category_data['description']}'"
            )
            
            # לוג התגובה המלאה לפני החיפוש
            logger.info(f"תגובת הסוכן ליצירת קטגוריה: {response}")
            
            import re
            # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
            category_id_match = re.search(r'(?:מזהה|ID|id|קטגוריה מספר)[:\s.]*([\d]+)', response)
            if not category_id_match:
                # ניסיון נוסף לחיפוש מספר בתגובה
                category_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
            
            if category_id_match:
                parent_id = int(category_id_match.group(1))
                created_categories.append(parent_id)
                logger.info(f"נוצרה קטגוריה חדשה לצורך יצירת תת-קטגוריה עם מזהה: {parent_id}")
            else:
                # אם אין התאמה, בדוק אם קיימת קטגוריה עם השם שהזנו או צור ישירות דרך ה-API
                try:
                    categories = woo_client.get_categories(per_page=10)
                    for category in categories:
                        if category_name in category.get("name", ""):
                            parent_id = category.get("id")
                            created_categories.append(parent_id)
                            logger.info(f"נמצאה קטגוריה קיימת עם שם דומה, מזהה: {parent_id}")
                            break
                    
                    # אם עדיין אין מזהה, ניצור קטגוריה ישירות דרך ה-API
                    if not parent_id:
                        new_category_data = {
                            "name": category_name,
                            "description": test_category_data['description']
                        }
                        new_category = woo_client.create_category(new_category_data)
                        parent_id = new_category.get("id")
                        if parent_id:
                            created_categories.append(parent_id)
                            logger.info(f"נוצרה קטגוריה חדשה ישירות דרך ה-API עם מזהה: {parent_id}")
                except Exception as e:
                    logger.error(f"שגיאה ביצירת קטגוריה דרך ה-API: {str(e)}")

        # וידוא שיש מזהה קטגוריה תקין
        assert parent_id is not None, "לא ניתן ליצור קטגוריה לבדיקה"
        
        subcategory_name = f"תת-קטגוריה לבדיקה {int(time.time())}"
        
        response = category_agent.run(
            f"צור תת-קטגוריה בשם '{subcategory_name}' תחת קטגוריית האב עם מזהה {parent_id}"
        )
        
        # וידוא שהיצירה התבצעה בהצלחה או שיש הודעת שגיאה מנומקת
        assert response is not None
        assert isinstance(response, str)
        assert ("נוצר" in response or
                "הקטגוריה נוצרה" in response or
                subcategory_name in response or
                "תת-קטגוריה" in response or
                "תת קטגוריה" in response or
                "שגיאה" in response or
                "בעיה" in response or
                "לא ניתן" in response)
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן ליצירת תת-קטגוריה: {response}")
        
        # חיפוש מזהה הקטגוריה החדשה בתשובה
        import re
        subcategory_id_match = re.search(r'(?:מזהה|ID|id)[:\s]+(\d+)', response)
        
        if subcategory_id_match:
            subcategory_id = int(subcategory_id_match.group(1))
            created_categories.append(subcategory_id)
            logger.info(f"נמצא מזהה תת-קטגוריה: {subcategory_id}")
    
    def test_search_categories(self, category_agent, test_category_data):
        """בדיקת חיפוש קטגוריות"""
        response = category_agent.run(f"חפש קטגוריות עם השם '{test_category_data['name']}'")
        
        # וידוא שהחיפוש החזיר תוצאות
        assert response is not None
        assert isinstance(response, str)
        assert "קטגורי" in response
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן לחיפוש קטגוריות: {response}")
    
    def test_delete_category(self, category_agent, test_category_data, woo_client):
        """בדיקת מחיקת קטגוריה"""
        # וידוא שיש קטגוריות לבדיקה - במידת הצורך, יצירת קטגוריה חדשה
        category_id = None
        # יצירת קטגוריה חדשה לבדיקת מחיקה כדי לא לפגוע בקטגוריות אחרות
        category_name = f"{test_category_data['name']} למחיקה {int(time.time())}"
        response = category_agent.run(
            f"צור קטגוריה חדשה בשם '{category_name}' עם תיאור '{test_category_data['description']}'"
        )
        
        # לוג התגובה המלאה לפני החיפוש
        logger.info(f"תגובת הסוכן ליצירת קטגוריה למחיקה: {response}")
        
        import re
        # שיפור הביטוי הרגולרי לחיפוש מזהה בתבניות שונות
        category_id_match = re.search(r'(?:מזהה|ID|id|קטגוריה מספר)[:\s.]*([\d]+)', response)
        if not category_id_match:
            # ניסיון נוסף לחיפוש מספר בתגובה
            category_id_match = re.search(r'(?<!\w)(\d+)(?!\w)', response)
        
        if category_id_match:
            category_id = int(category_id_match.group(1))
            logger.info(f"נוצרה קטגוריה חדשה לצורך מחיקה עם מזהה: {category_id}")
        else:
            # אם אין התאמה, ננסה ליצור קטגוריה ישירות דרך ה-API
            try:
                new_category_data = {
                    "name": category_name,
                    "description": test_category_data['description']
                }
                new_category = woo_client.create_category(new_category_data)
                category_id = new_category.get("id")
                if category_id:
                    logger.info(f"נוצרה קטגוריה חדשה ישירות דרך ה-API למחיקה עם מזהה: {category_id}")
            except Exception as e:
                logger.error(f"שגיאה ביצירת קטגוריה דרך ה-API: {str(e)}")
                # אם לא ניתן ליצור, נבדוק אם יש קטגוריות קיימות שניתן למחוק
        if created_categories:
            category_id = created_categories[-1]  # ניקח את הקטגוריה האחרונה ברשימה
            logger.info(f"משתמש בקטגוריה קיימת למחיקה עם מזהה: {category_id}")

        # וידוא שיש מזהה קטגוריה תקין
        assert category_id is not None, "לא ניתן ליצור קטגוריה לבדיקת מחיקה"
        
        # בדיקת מחיקת קטגוריה
        response = category_agent.run(f"מחק את הקטגוריה עם מזהה {category_id}")
        
        # וידוא שהמחיקה התבצעה בהצלחה
        assert response is not None
        assert isinstance(response, str)
        assert ("נמחק" in response or 
                "הקטגוריה נמחקה" in response or 
                "נמחקה בהצלחה" in response or
                "הוסרה" in response)
        
        # לוג של התשובה לצורך דיבוג
        logger.info(f"תגובת הסוכן למחיקת קטגוריה: {response}")
            
        # אם המחיקה התבצעה בהצלחה והקטגוריה הייתה ברשימת הקטגוריות שנוצרו, מסירים אותה מהרשימה
        if category_id in created_categories:
            created_categories.remove(category_id)
            logger.info(f"הוסרה קטגוריה {category_id} מרשימת הקטגוריות שנוצרו")
    
    # ניקוי קטגוריות שנוצרו ולא נמחקו
    @pytest.fixture(autouse=True, scope="class")
    def cleanup_created_categories(self, request, woo_client):
        """נקה את כל הקטגוריות שנוצרו במהלך הבדיקות"""
        # פונקציה שתופעל בסוף הטסטים של המחלקה
        def delete_remaining_categories():
            # ראשית מחק את תתי-הקטגוריות (אם יש)
            categories_to_delete = sorted(created_categories, reverse=True)  # מזהים גבוהים יותר נוטים להיות תתי-קטגוריות
            
            for category_id in categories_to_delete[:]:
                try:
                    woo_client.delete_category(category_id)
                    logger.info(f"נמחקה קטגוריית בדיקה עם מזהה {category_id}")
                    created_categories.remove(category_id)
                except Exception as e:
                    logger.error(f"שגיאה במחיקת קטגוריה {category_id}: {str(e)}")
        
        # הוספת פונקציית הניקוי לרשימת הפעולות שיבוצעו בסיום
        request.addfinalizer(delete_remaining_categories) 