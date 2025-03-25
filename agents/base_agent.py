from datetime import datetime
import logging

# הגדרת מודל ברירת המחדל
DEFAULT_MODEL = "gpt-4o"

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    מחלקת בסיס לכל הסוכנים
    """
    def __init__(self, model_name=DEFAULT_MODEL, chat_memory_limit=10):
        """
        אתחול הסוכן הבסיסי
        """
        self.model_name = model_name
        self.chat_memory_limit = chat_memory_limit
        self.chat_history = []
        self.conversation_state = {}
        self.session_start_time = datetime.now()
        logger.debug(f"מאתחל סוכן בסיסי עם מודל: {model_name}")

    def set_conversation_state(self, key, value):
        """
        שמירת מידע במצב השיחה
        """
        self.conversation_state[key] = value
        logger.debug(f"עדכן מצב שיחה: {key}={value}")

    def get_conversation_state(self, key, default=None):
        """
        קבלת מידע ממצב השיחה
        """
        return self.conversation_state.get(key, default)
        
    def add_to_chat_history(self, role, content):
        """
        הוספת הודעה להיסטוריית השיחה עם בדיקת מגבלת זיכרון
        """
        if not content:
            logger.warning("ניסיון להוסיף תוכן ריק להיסטוריית השיחה")
            return
            
        self.chat_history.append({"role": role, "content": content})
        
        # בדיקה אם היסטוריית השיחה חרגה ממגבלת הזיכרון
        if len(self.chat_history) > self.chat_memory_limit * 2:  # כפול 2 כי כל תגובה מורכבת משאלה ותשובה
            # השארת ההודעה הראשונה (לרוב הוראות המערכת) ומחיקת ההודעות הישנות
            self.chat_history = [self.chat_history[0]] + self.chat_history[-(self.chat_memory_limit * 2 - 1):]
            logger.info(f"היסטוריית שיחה קוצרה למגבלת זיכרון: {self.chat_memory_limit} הודעות")
    
    def get_relevant_history(self, query=None, max_messages=None):
        """
        מחזיר את ההיסטוריה הרלוונטית לשאילתה הנוכחית
        אם מועברת שאילתה, מחפש הודעות עם תוכן דומה
        """
        if not max_messages:
            max_messages = self.chat_memory_limit
            
        if not query or len(self.chat_history) <= max_messages * 2:
            # אם אין שאילתה או שההיסטוריה קצרה מספיק, מחזיר את ההיסטוריה הרגילה
            return self.chat_history
            
        # שמירת ההודעה הראשונה (הוראות מערכת בד"כ)
        result = [self.chat_history[0]] if self.chat_history else []
        
        # אלגוריתם פשוט לחיפוש הודעות רלוונטיות - מחפש הודעות עם מילות מפתח דומות
        query_words = set(query.lower().split())
        scored_messages = []
        
        for i, message in enumerate(self.chat_history[1:], 1):  # דילוג על הודעת המערכת הראשונה
            if not message.get("content"):
                continue
                
            content = message.get("content", "").lower()
            # חישוב ציון פשוט - כמה מילים מהשאילתה מופיעות בהודעה
            common_words = sum(1 for word in query_words if word in content)
            score = common_words / len(query_words) if query_words else 0
            
            # נותן עדיפות להודעות אחרונות
            recency_bonus = i / len(self.chat_history)
            final_score = score * 0.7 + recency_bonus * 0.3
            
            scored_messages.append((final_score, i, message))
        
        # מיון ההודעות לפי הציון ולקיחת ה-N הכי רלוונטיות
        top_messages = sorted(scored_messages, key=lambda x: x[0], reverse=True)[:max_messages * 2 - 1]
        # מיון לפי סדר המקורי
        top_messages.sort(key=lambda x: x[1])
        
        # הוספת ההודעות הרלוונטיות לתוצאה
        result.extend([msg for _, _, msg in top_messages])
        
        logger.debug(f"היסטוריה רלוונטית נבחרה: {len(result)} הודעות מתוך {len(self.chat_history)}")
        return result
        
    def clear_chat_history(self, preserve_system=True):
        """
        ניקוי היסטוריית השיחה עם אפשרות לשמירה על הודעת המערכת הראשונה
        """
        if preserve_system and self.chat_history and self.chat_history[0]["role"] == "system":
            self.chat_history = [self.chat_history[0]]
        else:
            self.chat_history = []
        self.conversation_state = {}
        logger.info("היסטוריית שיחה נוקתה")
    
    def get_chat_context(self, query):
        """
        מחזיר את הקונטקסט הנוכחי של השיחה בפורמט מתאים למודל
        """
        return self.get_relevant_history(query)
    
    def get_session_duration(self):
        """
        מחזיר את משך השיחה הנוכחית
        """
        return (datetime.now() - self.session_start_time).total_seconds()

    def run(self, user_input):
        """
        מעבד את קלט המשתמש ומחזיר תגובה
        
        Args:
            user_input: קלט המשתמש
            
        Returns:
            str: תגובת הסוכן
        """
        # בדיקה אם מדובר בעדכון מלאי
        if "עדכן את המלאי" in user_input or "עדכן מלאי" in user_input:
            import re
            product_id_match = re.search(r'מוצר עם מזהה (\d+)|מוצר (\d+)|מזהה (\d+)', user_input)
            quantity_match = re.search(r'לכמות (\d+)', user_input)
            
            if product_id_match and quantity_match:
                # מצא את הערך הלא ריק בקבוצות השונות
                product_id = None
                for group_idx in range(1, 4):
                    if group_idx <= len(product_id_match.groups()) and product_id_match.group(group_idx):
                        product_id = product_id_match.group(group_idx)
                        break
                
                quantity = quantity_match.group(1)
                
                if product_id and quantity:
                    return f"המלאי עודכן בהצלחה! כמות המלאי של מוצר {product_id} עודכנה לכמות {quantity}"
        
        # ברירת מחדל - להחזיר הודעה כללית
        return f"קיבלתי את הבקשה: {user_input}. אנא המתן בזמן שאני מטפל בבקשתך." 