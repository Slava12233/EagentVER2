#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
בדיקות יחידה לסוכן הראשי ולמעברים בין סוכנים
"""

import pytest
import logging
import time
import re

# Disable insecure HTTPS warnings that might appear when testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMainAgent:
    """מחלקת בדיקות לסוכן הראשי ומעברים בין סוכנים"""
    
    def test_agent_initialization(self, main_agent):
        """בדיקה שהסוכן הראשי מאותחל כראוי"""
        assert main_agent is not None
        assert hasattr(main_agent, 'client')
        assert hasattr(main_agent, 'woocommerce')
        assert hasattr(main_agent, 'router')
        assert hasattr(main_agent, 'handoffs')
        assert hasattr(main_agent, 'primary_agent')
        assert hasattr(main_agent, 'agents')
        
        # וידוא שכל הסוכנים המשניים נוצרו
        agent_types = ['product', 'order', 'category', 'coupon', 'customer', 'report', 'settings']
        for agent_type in agent_types:
            assert agent_type in main_agent.agents, f"הסוכן מסוג {agent_type} לא נוצר"
    
    def test_initial_conversation(self, main_agent):
        """בדיקת התחלת שיחה עם הסוכן הראשי"""
        response = main_agent.run("שלום, אני צריך עזרה עם חנות ה-WooCommerce שלי")
        
        # וידוא שהתגובה מכילה תוכן כלשהו ומתייחסת לבקשה
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # התגובה צריכה להיות ידידותית ולהציע עזרה
        assert (
            "שלום" in response or 
            "היי" in response or 
            "ברוך הבא" in response or
            "בכיף" in response or
            (response.strip().startswith("כמובן") and 
             ("אשמח לעזור" in response or "אעזור" in response or "אוכל לעזור" in response or "כדי לעזור" in response or "לסייע" in response))
        )
        assert "עזרה" in response or "לעזור" in response or "לסייע" in response
        
        logger.info(f"תגובת הסוכן הראשי להתחלת שיחה: {response}")
    
    def test_product_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן המוצרים"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        response = main_agent.run("אני רוצה להוסיף מוצר חדש")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן המוצרים
        assert response is not None
        assert isinstance(response, str)
        assert "מוצר" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת הוספת מוצר: {response}")
    
    def test_order_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן ההזמנות"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        response = main_agent.run("אני רוצה לבדוק הזמנות אחרונות")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן ההזמנות
        assert response is not None
        assert isinstance(response, str)
        assert "הזמנ" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת הזמנות אחרונות: {response}")
    
    def test_category_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן הקטגוריות"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")

        response = main_agent.run("אני צריך לנהל את הקטגוריות בחנות")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן הקטגוריות
        assert response is not None
        assert isinstance(response, str)
        assert "קטגורי" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת ניהול קטגוריות: {response}")
    
    def test_coupon_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן הקופונים"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        response = main_agent.run("אני רוצה ליצור קופוני הנחה")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן הקופונים
        assert response is not None
        assert isinstance(response, str)
        assert "קופון" in response or "הנחה" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת יצירת קופונים: {response}")
    
    def test_customer_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן הלקוחות"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        response = main_agent.run("אני רוצה לבדוק את רשימת הלקוחות שלי")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן הלקוחות
        assert response is not None
        assert isinstance(response, str)
        assert "לקוח" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת מידע על לקוחות: {response}")
    
    def test_report_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן הדוחות"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        response = main_agent.run("אני רוצה לראות דוחות מכירות")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן הדוחות
        assert response is not None
        assert isinstance(response, str)
        assert "דוח" in response or "דוחות" in response or "מכירות" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת דוחות: {response}")
    
    def test_settings_agent_handoff(self, main_agent):
        """בדיקת ניתוב לסוכן ההגדרות"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        response = main_agent.run("אני רוצה לשנות את הגדרות החנות")
        
        # וידוא שהתקבלה תשובה רלוונטית מסוכן ההגדרות
        assert response is not None
        assert isinstance(response, str)
        assert "הגדר" in response or "הגדרות" in response
        
        # בארכיטקטורה החדשה, הסוכן הראשי תמיד נשאר primary
        # ומנתב בקשות לסוכנים המתאימים כשירות
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary", "הסוכן הראשי צריך להישאר primary כחלק מהארכיטקטורה החדשה"
        
        logger.info(f"תגובת הסוכן לבקשת שינוי הגדרות: {response}")
    
    def test_return_to_primary_agent(self, main_agent):
        """בדיקת חזרה לסוכן הראשי"""
        # הבדיקה הזו אינה רלוונטית יותר כי הסוכן תמיד נשאר primary,
        # אבל נשאיר אותה כדי לוודא שהפקודה "חזור לסוכן הראשי" עדיין עובדת
        
        # וידוא שהסוכן מתחיל כסוכן ראשי
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # שליחת בקשה לסוכן מוצרים (אך הסוכן הראשי נשאר primary ורק מנתב את הבקשה)
        response = main_agent.run("אני רוצה להוסיף מוצר חדש")
        
        # וידוא שהסוכן הראשי עדיין primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # בקשה לחזור לסוכן הראשי (למרות שהוא כבר primary)
        response = main_agent.run("חזור לסוכן הראשי")
        
        # וידוא שהתקבלה תגובה מתאימה
        assert response is not None
        assert isinstance(response, str)
        assert "ראשי" in response or "עיקרי" in response or "primary" in response
        
        # וידוא שהסוכן עדיין primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        logger.info(f"תגובת הסוכן לבקשת חזרה לסוכן הראשי: {response}")
    
    def test_contextual_routing(self, main_agent):
        """בדיקת ניתוב הקשרי בין סוכנים"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        # שליחת בקשה למוצרים - הסוכן נשאר primary אבל מנתב לסוכן המוצרים
        products_response = main_agent.run("הראה לי את כל המוצרים")
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # שליחת בקשה לדוחות - הסוכן נשאר primary אבל מנתב לסוכן הדוחות
        reports_response = main_agent.run("הראה לי דוח מכירות")
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # וידוא שהתקבלו תשובות רלוונטיות מהסוכנים השונים
        assert products_response is not None
        assert reports_response is not None
        assert isinstance(products_response, str)
        assert isinstance(reports_response, str)
        
        # וידוא שהתשובות מכילות מילות מפתח רלוונטיות
        assert "מוצר" in products_response
        assert "דוח" in reports_response or "דו\"ח" in reports_response or "מכירות" in reports_response
        
        logger.info(f"תגובת הסוכן לבקשת מוצרים: {products_response}")
        logger.info(f"תגובת הסוכן לבקשת דוחות: {reports_response}")
    
    def test_multi_agent_conversation(self, main_agent):
        """בדיקת שיחה ארוכה עם מעבר בין סוכנים שונים"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        # רצף שאלות לסוכנים שונים
        responses = []
        
        # שאלה לסוכן המוצרים
        product_response = main_agent.run("כמה מוצרים יש בחנות?")
        responses.append(product_response)
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # שאלה לסוכן ההזמנות
        order_response = main_agent.run("כמה הזמנות התקבלו החודש?")
        responses.append(order_response)
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # שאלה לסוכן הקטגוריות
        category_response = main_agent.run("אילו קטגוריות יש בחנות?")
        responses.append(category_response)
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # וידוא שהתקבלו תשובות סבירות
        for response in responses:
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 10  # תשובה סבירה צפויה להיות ארוכה מ-10 תווים
        
        logger.info(f"תגובות השיחה הרב-סוכנית: {responses}")
    
    def test_agent_memory(self, main_agent):
        """בדיקת זיכרון בין בקשות לאותו סוכן"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        # שאלה ראשונה לסוכן המוצרים (דרך הראשי)
        first_response = main_agent.run("הראה לי מוצרים שעולים פחות מ-100 שקל")
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # שאלת המשך שמתייחסת לשאלה הקודמת
        second_response = main_agent.run("כמה מוצרים כאלה יש?")
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # וידוא שהתקבלו תשובות הגיוניות
        assert first_response is not None
        assert second_response is not None
        assert isinstance(first_response, str)
        assert isinstance(second_response, str)
        
        # וידוא שהתשובה השנייה מכילה מידע מספרי או התייחסות לכמות
        assert any(word in second_response.lower() for word in ["מוצרים", "נמצאו", "כמות", "מספר", "יש"])
        
        logger.info(f"תגובה ראשונה: {first_response}")
        logger.info(f"תגובה שנייה (המשך): {second_response}")
    
    def test_agent_identification(self, main_agent):
        """בדיקת זיהוי עצמי של סוכנים"""
        # אפס את המצב התחילי
        main_agent.run("חזור לסוכן הראשי")
        
        # שאלת זיהוי לסוכן הראשי
        primary_response = main_agent.run("איזה סוכן אתה?")
        
        # וידוא שהתשובה מכילה מידע על הסוכן הראשי
        assert "ראשי" in primary_response.lower() or "primary" in primary_response.lower() or "עיקרי" in primary_response.lower()
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # מעבר לסוכן ההגדרות (בארכיטקטורה החדשה, רק ניתוב)
        settings_transition = main_agent.run("אני רוצה לשנות את הגדרות החנות")
        
        # וידוא שהסוכן הראשי נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        # שאלת זיהוי כשהסוכן הראשי ניתב לסוכן ההגדרות
        settings_response = main_agent.run("איזה סוכן אתה?")
        
        # בארכיטקטורה החדשה, הסוכן הראשי הוא שעונה, לכן התשובה צריכה לציין שהוא הסוכן הראשי
        assert "ראשי" in settings_response.lower() or "primary" in settings_response.lower() or "עיקרי" in settings_response.lower()
        
        # וידוא שהסוכן נשאר primary
        current_agent_type = main_agent.get_current_agent_type()
        assert current_agent_type == "primary"
        
        logger.info(f"תגובת הסוכן הראשי לזיהוי עצמי: {primary_response}")
        logger.info(f"תגובת הסוכן לזיהוי עצמי אחרי ניתוב לסוכן ההגדרות: {settings_response}")
    
    def test_response_time(self):
        """בדיקה שזמן התגובה של הסוכן הוא מהיר מספיק"""
        from agents.main_agent import create_agent
        
        test_query = "מה אתה יכול לעזור לי?"
        
        # יצירת סוכן נסיוני
        agent = create_agent()
        
        start_time = time.time()
        response = agent.run(test_query)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # זמן תגובה צריך להיות מהיר (פחות מ-20 שניות)
        # הערה: זמני תגובה של OpenAI יכולים להשתנות ולא תמיד בשליטתנו
        assert elapsed_time < 20
        
        # וידוא שקיבלנו תגובה כלשהי
        assert response and len(response) > 0
        
        logger.info(f"זמן תגובה לשאלה פשוטה: {elapsed_time:.2f} שניות")
    
    def test_ambiguous_request_handling(self, main_agent):
        """בדיקת טיפול בבקשה לא ברורה"""
        # חזרה לסוכן הראשי
        if main_agent.get_current_agent_type() != "primary":
            main_agent.run("חזור לסוכן הראשי")
        
        # בקשה עמומה
        response = main_agent.run("אני רוצה לעדכן")
        
        # התגובה אמורה לבקש הבהרה או להציע אפשרויות
        assert response is not None
        assert isinstance(response, str)
        assert "לעדכן מה" in response or "איזה סוג" in response or "למה" in response or "?" in response
        
        logger.info(f"תגובת הסוכן לבקשה עמומה: {response}") 