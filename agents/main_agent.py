#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent ראשי משופר למערכת AI Agents לניהול חנות WooCommerce
---------------------------------------------------------

קובץ זה מגדיר את ה-Agent הראשי המשופר שמנהל את השיחה עם המשתמש
ומעביר משימות ל-Agents מתמחים באמצעות מנגנון handoff מתקדם.

שיפורים:
- זיהוי אוטומטי של ה-Agent המתאים
- שיתוף מידע בין ה-Agents
- מנגנון לחזרה ל-Agent הקודם
"""

from .base import Agent, Handoff, Guardrail, Thread, Tool, function_tool
from utils.tracing import Trace
from memory.vector_store import AdvancedVectorStore
from agents.product_agent import create_product_agent
from agents.order_agent import create_order_agent
from agents.coupon_agent import create_coupon_agent
from agents.category_agent import create_category_agent
from agents.customer_agent import create_customer_agent
from agents.report_agent import create_report_agent
from agents.settings_agent import create_settings_agent
import json
from typing import Dict, List, Optional, Any, Tuple
import re
import asyncio
import logging
from .base_agent import BaseAgent
import os
import glob
import importlib.util
import yaml
import hashlib
import pkg_resources

# הגדרת מודל ברירת המחדל
DEFAULT_MODEL = "gpt-4o"

logger = logging.getLogger(__name__)

class AgentContext:
    """
    מחלקה לשמירת הקשר ומידע משותף בין ה-Agents.
    """
    
    def __init__(self):
        """
        אתחול הקשר ה-Agent.
        """
        self.shared_data = {}
        self.conversation_history = []
        self.agent_history = []
        self.current_task = None
    
    def add_to_history(self, user_input: str, response: str, agent_name: str):
        """
        מוסיף פריט לשיחה להיסטוריה.
        
        Args:
            user_input: קלט המשתמש
            response: תגובת ה-Agent
            agent_name: שם ה-Agent שטיפל בבקשה
        """
        self.conversation_history.append({
            "user_input": user_input,
            "response": response,
            "agent_name": agent_name,
            "timestamp": self._get_timestamp()
        })
        
        self.agent_history.append(agent_name)
    
    def _get_timestamp(self):
        """
        מחזיר חותמת זמן נוכחית.
        
        Returns:
            חותמת זמן כמחרוזת
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def set_shared_data(self, key: str, value: Any):
        """
        מגדיר מידע משותף.
        
        Args:
            key: מפתח
            value: ערך
        """
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """
        מחזיר מידע משותף.
        
        Args:
            key: מפתח
            default: ערך ברירת מחדל אם המפתח לא קיים
        
        Returns:
            הערך המשותף
        """
        return self.shared_data.get(key, default)
    
    def set_current_task(self, task: str):
        """
        מגדיר את המשימה הנוכחית.
        
        Args:
            task: תיאור המשימה
        """
        self.current_task = task
    
    def get_conversation_summary(self, last_n=5):
        """
        מחזיר סיכום של ההיסטוריה האחרונה של השיחה.
        
        Args:
            last_n: מספר הפריטים האחרונים לסיכום (ברירת מחדל: 5)
        
        Returns:
            str: סיכום ההיסטוריה
        """
        if not self.conversation_history:
            return ""
        
        # הגבלת מספר הפריטים
        last_items = self.conversation_history[-last_n:] if last_n > 0 else self.conversation_history
        
        summary = []
        for item in last_items:
            user_input = item.get("user_input", "")
            response = item.get("response", "")
            agent_name = item.get("agent_name", "לא ידוע")
            
            summary.append(f"משתמש: {user_input}")
            summary.append(f"סוכן ({agent_name}): {response}")
            summary.append("---")
        
        return "\n".join(summary)
    
    def get_previous_agent(self):
        """
        מחזיר את הסוכן הקודם בהיסטוריה.
        
        Returns:
            str: שם הסוכן הקודם, או None אם אין היסטוריה
        """
        if len(self.agent_history) > 1:
            return self.agent_history[-2]
        return None
        
    def get_context_for_model(self):
        """
        מכין הקשר לשימוש במודל השפה, כולל היסטוריית השיחה.
        מאפשר למודל להבין את ההקשר של שיחות קודמות.
        
        Returns:
            str: הקשר מפורמט לשימוש במודל השפה
        """
        if not self.conversation_history:
            return ""
            
        # נשתמש ב-3 השיחות האחרונות לכל היותר
        context_items = self.conversation_history[-3:]
        
        context_parts = []
        context_parts.append("### היסטוריית שיחה קודמת:")
        
        for item in context_items:
            user_input = item.get("user_input", "")
            response = item.get("response", "")
            
            context_parts.append(f"משתמש: {user_input}")
            context_parts.append(f"מערכת: {response}")
            context_parts.append("---")
            
        context_parts.append("### שים לב להיסטוריה לעיל בעת מתן תשובה לשאלה הנוכחית.")
        
        return "\n".join(context_parts)

class AgentRouter:
    """
    מחלקה לניתוב בקשות לסוכנים המתאימים ביותר
    """
    
    def __init__(self, client, model_name="gpt-4o"):
        """
        אתחול המנתב
        
        Args:
            client: הלקוח של OpenAI 
            model_name: שם המודל לשימוש
        """
        self.client = client
        self.model = model_name
        self.topic_mapping = {
            "מוצרים": "product",
            "הזמנות": "order",
            "קופונים": "coupon",
            "קטגוריות": "category",
            "לקוחות": "customer",
            "דוחות": "report",
            "הגדרות": "settings",
        }
    
    def identify_agent(self, user_input, context=None):
        """
        מזהה את הסוכן המתאים ביותר לטיפול בקלט המשתמש
        
        Args:
            user_input: קלט המשתמש
            context: הקשר השיחה (אופציונלי)
            
        Returns:
            str: שם הסוכן המתאים
        """
        # בדיקה אם זו שאלה על זהות הסוכן - תמיד תחזיר primary
        if "איזה סוכן אתה" in user_input or "מי אתה" in user_input:
            return "primary"
            
        # בדיקה ישירה לביטויים הקשורים לקטגוריות
        if any(phrase in user_input.lower() for phrase in [
            "קטגוריה חדשה", "צור קטגוריה", "יצירת קטגוריה", "הוסף קטגוריה",
            "עדכן קטגוריה", "שנה קטגוריה", "מחק קטגוריה", "רשימת קטגוריות",
            "חפש קטגוריה", "פרטי קטגוריה"
        ]):
            return "category"
            
        prompt = f"""
        שאלה או בקשה של המשתמש: {user_input}
        
        באיזה תחום עוסקת השאלה או הבקשה של המשתמש? נא לבחור אחד מהתחומים הבאים:
        - מוצרים (ניהול מוצרים, יצירת מוצרים, עדכון מוצרים, מחירים, מלאי וכו')
        - הזמנות (ניהול הזמנות, סטטוס הזמנות, משלוחים וכו')
        - קופונים (יצירת קופונים, הנחות, מבצעים וכו')
        - קטגוריות (ניהול קטגוריות מוצרים, מאפיינים וכו')
        - לקוחות (ניהול לקוחות, פרטי לקוחות וכו')
        - דוחות (נתונים, סטטיסטיקות, מכירות וכו')
        - הגדרות (הגדרות חנות, תשלומים, משלוחים, מיסים וכו')
        
        נא לענות בתחום אחד בלבד מהרשימה לעיל, ללא הסברים נוספים.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "אתה מומחה לסיווג בקשות ושאלות בתחום של ניהול חנות WooCommerce. תפקידך לזהות את התחום אליו שייכת השאלה."},
                {"role": "user", "content": prompt},
            ]
        )
        
        agent_area = response.choices[0].message.content.strip()
        
        # המרה לקוד הסוכן המתאים
        for topic, agent_type in self.topic_mapping.items():
            if topic in agent_area:
                return agent_type
        
        # ברירת מחדל היא הסוכן הראשי
        return "primary"

class MainAgent(BaseAgent):
    """
    הסוכן הראשי של המערכת
    אחראי על ניתוב בקשות המשתמש לסוכן המתאים
    """
    
    # מיפוי בין סוגי הסוכנים לפונקציות ליצירת הסוכנים
    AGENT_MAPPING = {
        "product": create_product_agent,
        "category": create_category_agent,
        "order": create_order_agent,
        "coupon": create_coupon_agent,
        "customer": create_customer_agent,
        "settings": create_settings_agent,
        "report": create_report_agent
    }
    
    def __init__(self, client, model_name=DEFAULT_MODEL, woo_client=None):
        """
        אתחול הסוכן הראשי
        מקבל לקוח WooCommerce לשימוש הסוכנים
        """
        super().__init__(model_name)
        
        self.client = client
        self.woocommerce = woo_client
        self.model = model_name  # שמירת שם המודל כמשתנה מחלקה
        self.current_agent_type = "primary"  # Agent ראשי כברירת מחדל
        self.context = AgentContext()
        self.router = None
        
        # יצירת מנתב אם קיים לקוח
        if client:
            self.router = AgentRouter(client, model_name)
        
        # מחזיק את הסוכנים המתמחים
        self.specialized_agents = {}
        self.agents = {}  # תמיכה לאחורה בשמות ישנים
        self.primary_agent = None  # הסוכן הראשי
        self.handoffs = []  # רשימת העברות
        
        # אתחול הסוכנים המתמחים אם קיים לקוח וסטור WooCommerce
        if client and woo_client:
            self._create_specialized_agents()
        
    def run(self, user_input):
        """
        מעבד בקשת משתמש ומנתב אותה לסוכן המתאים
        
        הסוכן הראשי תמיד נשאר בשליטה ומשתמש בסוכנים המתמחים ככלים
        
        Args:
            user_input: קלט המשתמש (טקסט)
            
        Returns:
            str: תשובת הסוכן המתאים
        """
        logger.info(f"MainAgent.run קיבל קלט: {user_input}")
        
        # בדיקה אם זו בקשה לחזור לסוכן הראשי או שאלה על זהות הסוכן
        if ("חזור לסוכן הראשי" in user_input or 
            "חזור לסוכן הכללי" in user_input or 
            "איזה סוכן אתה" in user_input or 
            "מי אתה" in user_input):
            # אין צורך לשנות סוג סוכן כי הסוכן הראשי תמיד נשאר בשליטה
            return self._get_primary_agent_response(user_input)
            
        # בדיקה אם זו בקשה עמומה (מעט מילים ללא הקשר ברור)
        if len(user_input.split()) < 4 and not any(specific in user_input.lower() for specific in 
            ["מוצר", "הזמנ", "קטגור", "קופון", "לקוח", "דוח", "הגדר"]):
            return f"אשמח לעזור! האם תוכל לפרט יותר לגבי מה שאתה רוצה לעדכן? האם מדובר במוצר, הזמנה, קטגוריה, או משהו אחר?"
        
        # בדיקה אם מדובר בשאלת המשך (שאלה קצרה שמתייחסת לשיחה קודמת)
        is_followup = len(user_input.split()) <= 5 and any(word in user_input.lower() for word in 
                                                       ["כמה", "איזה", "מה", "למה", "כמות", "פרטים", "עוד", "אחר", "נוסף"])
        
        # אם יש היסטוריית שיחה ומדובר בשאלת המשך, נחפש את הסוכן האחרון שענה ונעביר אליו את השאלה
        if is_followup and self.context.conversation_history:
            # מציאת הסוכן האחרון שטיפל בבקשה
            last_agent_type = self.context.agent_history[-1] if self.context.agent_history else "primary"
            
            # אם זה לא הסוכן הראשי, נעביר את השאלה לסוכן המתאים
            if last_agent_type != "primary" and last_agent_type in self.specialized_agents:
                agent = self.specialized_agents[last_agent_type]
                
                # הכנת הקשר השיחה להעברה לסוכן
                conversation_context = self.context.get_context_for_model()
                
                # בניית קלט עם הקשר
                enhanced_input = f"{conversation_context}\n\nשאלה נוכחית: {user_input}"
                
                # שליחה לסוכן המתאים
                if hasattr(agent, 'agent'):
                    response = agent.agent.run(enhanced_input)
                else:
                    response = agent.run(enhanced_input)
                    
                # הוספת התגובה להיסטוריה
                self.context.add_to_history(user_input, response, last_agent_type)
                return response
        
        # בדיקה אם מדובר בבקשה ליצירת מוצר במינוח מעורפל כמו "תמצא מוצר"
        if re.search(r'^(תמצא מוצר|מצא מוצר)\s+.+\s+כמות\s+\d+\s+מחיר\s+\d+', user_input, re.IGNORECASE):
            logger.info(f"זוהתה בקשה מעורפלת ליצירת מוצר: {user_input}")
            # עיבוד הקלט לפני העברה לסוכן המוצרים
            processed_input, was_processed = self._process_user_intent(user_input)
            
            if was_processed and "product" in self.specialized_agents:
                agent = self.specialized_agents["product"]
                
                # הכנת הקשר השיחה להעברה לסוכן
                conversation_context = self.context.get_context_for_model()
                
                # בניית קלט עם הקשר
                enhanced_input = processed_input
                if conversation_context:
                    enhanced_input = f"{conversation_context}\n\nשאלה נוכחית: {processed_input}"
                
                # שליחה לסוכן המוצרים
                if hasattr(agent, 'agent'):
                    response = agent.agent.run(enhanced_input)
                else:
                    response = agent.run(enhanced_input)
                
                # הוספת התגובה להיסטוריה
                self.context.add_to_history(user_input, response, "product")
                return response
        
        # זיהוי סוכן מתאים לטיפול בבקשה
        if self.router:
            target_agent_type = self.router.identify_agent(user_input, self.context)
            
            # אם זוהה סוכן מתמחה מתאים, העבר אליו את הבקשה
            if target_agent_type != "primary" and target_agent_type in self.specialized_agents:
                agent = self.specialized_agents[target_agent_type]
                
                # הכנת הקשר השיחה להעברה לסוכן אם יש היסטוריה
                conversation_context = self.context.get_context_for_model()
                
                # בניית קלט עם הקשר אם יש היסטוריה
                enhanced_input = user_input
                if conversation_context:
                    enhanced_input = f"{conversation_context}\n\nשאלה נוכחית: {user_input}"
                
                # בדיקה אם מדובר באובייקט Handoff
                if hasattr(agent, 'agent'):
                    # קריאה לסוכן דרך אובייקט Handoff
                    response = agent.agent.run(enhanced_input)
                else:
                    # קריאה ישירה לסוכן
                    response = agent.run(enhanced_input)
                    
                # הוסף את התגובה להיסטוריה ושמור את סוג הסוכן שטיפל בבקשה
                self.context.add_to_history(user_input, response, target_agent_type)
                return response
        
        # אם לא זוהה סוכן ספציפי או שהבקשה היא כללית, הסוכן הראשי מטפל בה
        processed_input, was_processed = self._process_user_intent(user_input)
        
        # אם הקלט עבר עיבוד, נסה שוב לזהות סוכן מתאים
        if was_processed and self.router:
            target_agent_type = self.router.identify_agent(processed_input, self.context)
            
            if target_agent_type != "primary" and target_agent_type in self.specialized_agents:
                agent = self.specialized_agents[target_agent_type]
                
                # הכנת הקשר השיחה להעברה לסוכן
                conversation_context = self.context.get_context_for_model()
                
                # בניית קלט עם הקשר אם יש היסטוריה
                enhanced_input = processed_input
                if conversation_context:
                    enhanced_input = f"{conversation_context}\n\nשאלה נוכחית: {processed_input}"
                
                if hasattr(agent, 'agent'):
                    response = agent.agent.run(enhanced_input)
                else:
                    response = agent.run(enhanced_input)
                    
                self.context.add_to_history(user_input, response, target_agent_type)
                return response
        
        # טיפול בבקשה על ידי הסוכן הראשי
        # מענה לשאלות כלליות, הכוונה או עזרה
        primary_response = self._get_primary_agent_response(user_input)
        self.context.add_to_history(user_input, primary_response, "primary")
        return primary_response

    def _get_primary_agent_response(self, user_input):
        """
        מחזיר תשובה של הסוכן הראשי לשאלות כלליות
        
        Args:
            user_input: קלט המשתמש
            
        Returns:
            str: תשובת הסוכן הראשי
        """
        # בדיקה אם זו שאלה על הסוכן עצמו
        if "איזה סוכן אתה" in user_input or "מי אתה" in user_input:
            return "אני הסוכן הראשי (Primary Agent) של מערכת ניהול החנות. אני מסייע בניתוב שאלות לסוכנים מתמחים ומטפל בבקשות כלליות."
            
        # בדיקה אם זו בקשה לעזרה
        if "עזרה" in user_input or "מה אתה יכול לעשות" in user_input:
            return """אני הסוכן הראשי ואני יכול לעזור לך בניהול חנות ה-WooCommerce שלך. למשל:
            - ניהול מוצרים (הוספה, עדכון, מחיקה)
            - ניהול הזמנות (צפייה, עדכון סטטוס)
            - ניהול קופונים והנחות
            - ניהול קטגוריות מוצרים
            - ניהול לקוחות
            - הפקת דוחות על ביצועי החנות
            - שינוי הגדרות החנות
            
            פשוט ציין מה אתה רוצה לעשות ואנתב אותך לסוכן המתאים."""
        
        # בדיקה אם זו בקשה ראשונית
        if "שלום" in user_input or "היי" in user_input or "ברוך הבא" in user_input or "צריך עזרה" in user_input:
            return "שלום! אני הסוכן הראשי ואני כאן כדי לעזור לך בניהול חנות ה-WooCommerce שלך. במה אוכל לסייע לך היום?"
            
        # ברירת מחדל - מציע עזרה כללית
        return "אני הסוכן הראשי ואני יכול לעזור לך בניהול חנות ה-WooCommerce שלך. אנא פרט במה אתה מעוניין: מוצרים, הזמנות, קופונים, קטגוריות, לקוחות, דוחות או הגדרות?"

    def get_current_agent_type(self):
        """
        מחזיר את סוג הסוכן הנוכחי
        
        Returns:
            str: סוג הסוכן הנוכחי (primary, product, order, וכו')
        """
        return self.current_agent_type

    def _create_specialized_agents(self):
        """
        יוצר סוכנים מיוחדים עבור תחומים שונים בחנות ומוסיף אותם למערכת
        """
        # הוספת סוכנים מתמחים
        self.add_specialized_agent("product", create_product_agent(self.client, self.model, self.woocommerce))
        self.add_specialized_agent("order", create_order_agent(self.client, self.model, self.woocommerce))
        self.add_specialized_agent("coupon", create_coupon_agent(self.client, self.model, self.woocommerce))
        self.add_specialized_agent("category", create_category_agent(self.client, self.model, self.woocommerce))
        self.add_specialized_agent("customer", create_customer_agent(self.client, self.model, self.woocommerce))
        self.add_specialized_agent("report", create_report_agent(self.client, self.model, self.woocommerce))
        self.add_specialized_agent("settings", create_settings_agent(self.client, self.model, self.woocommerce))

        # הוספת handoff agents עבור זיהוי מתי להעביר לסוכן מתמחה
        # סוכן מוצרים: טיפול בבקשות הקשורות למוצרים, מלאי, מחירים וכו
        handoff = Handoff(
            name="product_handoff",
            agent=self.specialized_agents["product"],
            description="לטיפול בבקשות הקשורות למוצרים, רשימת מוצרים, יצירת מוצרים, עדכון מוצרים, מלאי, מחירים וכו'"
        )
        self.add_specialized_agent(handoff.name, handoff)
        
        # עדכון רשימת העברות
        self.handoffs = []
        
        # הוספת handoff לכל סוכן מתמחה
        product_handoff = Handoff(
            name="product",
            agent=self.specialized_agents["product"],
            description="העבר לסוכן מוצרים כשהמשתמש מבקש לנהל מוצרים, לחפש מוצרים, ליצור או לעדכן מוצרים, או לעבוד עם מלאי."
        )
        
        order_handoff = Handoff(
            name="order",
            agent=self.specialized_agents["order"],
            description="העבר לסוכן הזמנות כשהמשתמש מבקש לנהל הזמנות, לחפש הזמנות, לעדכן סטטוס הזמנות או לבצע פעולות הקשורות להזמנות."
        )
        
        coupon_handoff = Handoff(
            name="coupon",
            agent=self.specialized_agents["coupon"],
            description="העבר לסוכן קופונים כשהמשתמש מבקש ליצור קופונים, לנהל קופונים, או לעדכן מבצעים והנחות."
        )
        
        category_handoff = Handoff(
            name="category",
            agent=self.specialized_agents["category"],
            description="העבר לסוכן קטגוריות כשהמשתמש מבקש לנהל קטגוריות מוצרים, תגיות, או מבנה המוצרים בחנות."
        )
        
        customer_handoff = Handoff(
            name="customer",
            agent=self.specialized_agents["customer"],
            description="העבר לסוכן לקוחות כשהמשתמש מבקש לנהל לקוחות, לחפש לקוחות, או לעדכן פרטי לקוחות."
        )
        
        report_handoff = Handoff(
            name="report",
            agent=self.specialized_agents["report"],
            description="העבר לסוכן דו״חות כשהמשתמש מבקש לקבל דו״חות מכירות, נתונים סטטיסטיים, או ניתוח ביצועים של החנות."
        )
        
        settings_handoff = Handoff(
            name="settings_handoff",
            agent=self.specialized_agents["settings"],
            description="העבר לסוכן הגדרות כשהמשתמש מבקש לעדכן הגדרות חנות, להגדיר שיטות משלוח, שיטות תשלום או הגדרות כלליות."
        )
        
        # הוספת כל ה-handoffs לסוכן הראשי
        self.handoffs.extend([
            product_handoff, order_handoff, coupon_handoff, 
            category_handoff, customer_handoff, report_handoff, 
            settings_handoff
        ])
        
        # הוספת ה-handoffs לרשימת הכלים
        for handoff in self.handoffs:
            self.add_specialized_agent(handoff.name, handoff)

    def add_specialized_agent(self, name, agent):
        """
        מוסיף סוכן מתמחה למערכת
        
        Args:
            name: שם הסוכן המתמחה
            agent: אובייקט הסוכן
            
        Returns:
            self: להמשך שרשור קריאות
        """
        self.specialized_agents[name] = agent
        self.agents[name] = agent  # שמירה גם במילון הישן לתמיכה לאחורה
        
        return self

    def _process_user_intent(self, user_input):
        """
        מזהה את הכוונה האמיתית של המשתמש מתוך הקלט
        מחזיר את הקלט המעובד ודגל שמציין אם הקלט השתנה
        """
        original_input = user_input
        
        # בדיקה אם מדובר בבקשה ליצירת מוצר אך במינוח "תמצא מוצר"
        find_product_match = re.match(r'^(תמצא מוצר|מצא מוצר)\s+(.+?)(?:\s+כמות\s+(\d+))?(?:\s+מחיר\s+(\d+(?:\.\d+)?))?$', user_input, re.DOTALL)
        if find_product_match:
            product_name = find_product_match.group(2).strip()
            quantity = find_product_match.group(3) if find_product_match.group(3) else None
            price = find_product_match.group(4) if find_product_match.group(4) else None
            
            # אם יש גם מחיר וגם כמות, כנראה שהמשתמש התכוון ליצור מוצר
            if price and quantity:
                # שימור שם המוצר המדויק ורק החלפת הפקודה עצמה
                processed_input = f"צור מוצר {product_name} כמות {quantity} מחיר {price}"
                logger.info(f"התגלתה כוונה ליצירת מוצר במינוח 'תמצא מוצר'. קלט מקורי: '{user_input}', קלט מעובד: '{processed_input}'")
                logger.info(f"שם המוצר: '{product_name}', כמות: {quantity}, מחיר: {price}")
                return processed_input, True
                
        # בדיקה אם מדובר בבקשה לעדכון מלאי בצורה עמומה
        update_product_match = re.match(r'^עדכן את המוצר\s+(\d+)\s+ל-(\d+)$', user_input)
        if update_product_match:
            product_id = update_product_match.group(1)
            value = update_product_match.group(2)
            
            # ההנחה היא שהמשתמש מתכוון לעדכן מלאי
            processed_input = f"עדכן מלאי למוצר {product_id} לכמות {value}"
            logger.info(f"התגלתה כוונה לעדכון מלאי בצורה עמומה. קלט מקורי: '{user_input}', קלט מעובד: '{processed_input}'")
            return processed_input, True
            
        # החזרת הקלט המקורי אם לא בוצע עיבוד
        return user_input, (user_input != original_input)
            
    def _detect_complex_action(self, user_input):
        """
        זיהוי פעולות מורכבות שדורשות אימות
        מחזיר סוג הפעולה ופרטים רלוונטיים, או None אם לא זוהתה פעולה מורכבת
        """
        # זיהוי יצירת מוצר
        product_match = re.search(r'צור מוצר|יצירת מוצר|מוצר חדש|תמצא מוצר.*מחיר', user_input, re.IGNORECASE)
        if product_match:
            # חילוץ פרטים רלוונטיים
            name_match = re.search(r'(?:בשם|שם:?|ששמו)\s+[\'"]?([^\'",]+)[\'"]?', user_input)
            price_match = re.search(r'(?:מחיר:?|במחיר)\s+(\d+(?:\.\d+)?)', user_input)
            quantity_match = re.search(r'(?:כמות:?|במלאי)\s+(\d+)', user_input)
            
            details = {}
            if name_match:
                details["name"] = name_match.group(1).strip()
            if price_match:
                details["price"] = price_match.group(1)
            if quantity_match:
                details["quantity"] = quantity_match.group(1)
                
            return "create_product", details
            
        # זיהוי עדכון מחיר
        price_update_match = re.search(r'עדכן מחיר|שנה מחיר|לשנות מחיר', user_input, re.IGNORECASE)
        if price_update_match:
            # חילוץ מזהה מוצר ומחיר חדש
            product_id_match = re.search(r'מוצר\s+(\d+)', user_input)
            new_price_match = re.search(r'(?:מחיר חדש|למחיר|מחיר:?)\s+(\d+(?:\.\d+)?)', user_input)
            
            details = {}
            if product_id_match:
                details["product_id"] = product_id_match.group(1)
            if new_price_match:
                details["new_price"] = new_price_match.group(1)
                
            return "update_price", details
            
        # זיהוי עדכון מלאי
        stock_update_match = re.search(r'עדכן מלאי|עדכן כמות|שנה מלאי|לשנות מלאי', user_input, re.IGNORECASE)
        if stock_update_match:
            # חילוץ מזהה מוצר וכמות חדשה
            product_id_match = re.search(r'מוצר\s+(\d+)', user_input)
            new_stock_match = re.search(r'(?:כמות חדשה|לכמות|כמות:?|ל-)\s+(\d+)', user_input)
            
            details = {}
            if product_id_match:
                details["product_id"] = product_id_match.group(1)
            if new_stock_match:
                details["new_stock"] = new_stock_match.group(1)
                
            return "update_stock", details
            
        # זיהוי יצירת קטגוריה
        category_match = re.search(r'צור קטגוריה|יצירת קטגוריה|קטגוריה חדשה', user_input, re.IGNORECASE)
        if category_match:
            # חילוץ שם הקטגוריה
            name_match = re.search(r'(?:בשם|שם:?|ששמה)\s+[\'"]?([^\'",]+)[\'"]?', user_input)
            
            details = {}
            if name_match:
                details["name"] = name_match.group(1).strip()
                
            return "create_category", details
            
        # לא זוהתה פעולה מורכבת
        return None, None
        
    def _generate_confirmation_message(self, action_type, action_details):
        """
        יצירת הודעת אימות מותאמת לסוג הפעולה והפרטים שלה
        """
        if action_type == "create_product":
            name = action_details.get("name", "מוצר חדש")
            price = action_details.get("price", "לא צוין")
            quantity = action_details.get("quantity", "לא צוין")
            
            return f"האם אתה מעוניין ליצור מוצר חדש עם הפרטים הבאים?\n" \
                   f"שם: {name}\n" \
                   f"מחיר: {price}\n" \
                   f"כמות במלאי: {quantity}\n\n" \
                   f"אנא אשר עם 'כן' או בטל עם 'לא'."
                   
        elif action_type == "update_price":
            product_id = action_details.get("product_id", "לא צוין")
            new_price = action_details.get("new_price", "לא צוין")
            
            return f"האם אתה מעוניין לעדכן את מחיר המוצר עם מזהה {product_id} למחיר {new_price}?\n\n" \
                   f"אנא אשר עם 'כן' או בטל עם 'לא'."
                   
        elif action_type == "update_stock":
            product_id = action_details.get("product_id", "לא צוין")
            new_stock = action_details.get("new_stock", "לא צוין")
            
            return f"האם אתה מעוניין לעדכן את כמות המלאי של המוצר עם מזהה {product_id} לכמות {new_stock}?\n\n" \
                   f"אנא אשר עם 'כן' או בטל עם 'לא'."
                   
        elif action_type == "create_category":
            name = action_details.get("name", "קטגוריה חדשה")
            
            return f"האם אתה מעוניין ליצור קטגוריה חדשה בשם '{name}'?\n\n" \
                   f"אנא אשר עם 'כן' או בטל עם 'לא'."
                   
        else:
            # הודעה כללית למקרה שלא זוהה סוג פעולה ספציפי
            return f"האם אתה מעוניין לבצע את הפעולה הזו?\n\n" \
                   f"אנא אשר עם 'כן' או בטל עם 'לא'."
    
    def _is_confirmation_response(self, user_input):
        """
        בדיקה האם הקלט של המשתמש הוא תגובה לבקשת אימות
        """
        # בדיקת ביטויים שונים של אישור או ביטול בעברית
        confirmation_pattern = r'^(?:כן|אישור|מאשר|נכון|אכן|בהחלט|בבקשה|אוקיי|אוקי|ok|yes|y)$'
        rejection_pattern = r'^(?:לא|ביטול|מבטל|לבטל|שגוי|לא מאשר|no|n)$'
        
        return (re.search(confirmation_pattern, user_input.strip(), re.IGNORECASE) is not None or
                re.search(rejection_pattern, user_input.strip(), re.IGNORECASE) is not None)
    
    def _is_positive_confirmation(self, user_input):
        """
        בדיקה האם התגובה היא אישור חיובי
        """
        # בדיקת ביטויים שונים של אישור בעברית
        confirmation_pattern = r'^(?:כן|אישור|מאשר|נכון|אכן|בהחלט|בבקשה|אוקיי|אוקי|ok|yes|y)$'
        
        return re.search(confirmation_pattern, user_input.strip(), re.IGNORECASE) is not None

def create_agent(client=None, model_name="gpt-4o", woo_client=None):
    """
    יוצר ומחזיר סוכן ראשי עם כל הסוכנים המתמחים
    
    Args:
        client: הלקוח של OpenAI (אופציונלי)
        model_name: שם המודל לשימוש (ברירת מחדל: gpt-4o)
        woo_client: לקוח WooCommerce (אופציונלי)
    
    Returns:
        MainAgent: סוכן ראשי מוכן לשימוש
    """
    # יצירת לקוח OpenAI אם לא סופק
    if not client:
        from openai import OpenAI
        import os
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # יצירת נתב
    router = AgentRouter(client, model_name)
    
    # יצירת הסוכן הראשי
    main_agent = MainAgent(client, model_name, woo_client)
    
    return main_agent
