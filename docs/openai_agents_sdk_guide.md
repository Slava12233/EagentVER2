# מדריך לשימוש ב-OpenAI Agents SDK בפרויקט

## מבוא ל-OpenAI Agents SDK

[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) הוא ספריית Python רשמית מבית OpenAI שמאפשרת לבנות מערכות מבוססות agents חכמים. ה-SDK מספק תשתית מלאה ליצירת agents, הגדרת כלים (tools), ניהול שיחות, העברת משימות בין agents (handoffs), ועוד.

בפרויקט זה, אנחנו משתמשים ב-SDK כדי לבנות מערכת מודולרית ומתקדמת של agents לניהול חנות WooCommerce, עם יכולות משופרות כמו זיהוי אוטומטי של ה-Agent המתאים, שיתוף מידע בין ה-Agents, ומערכת זיכרון חכמה.

## התקנת ה-SDK

ה-SDK מותקן באמצעות pip:

```bash
pip install openai-agents
```

לתמיכה בקול (אופציונלי):

```bash
pip install 'openai-agents[voice]'
```

## רכיבי מפתח ב-SDK

### Agent

המחלקה `Agent` היא הרכיב המרכזי ב-SDK. היא מייצגת agent חכם שיכול לבצע משימות, להשתמש בכלים, ולתקשר עם המשתמש.

```python
from openai.agents import Agent

agent = Agent(
    client=client,
    model="gpt-4o",
    instructions="הוראות מפורטות ל-agent",
    tools=[tool1, tool2, tool3],
    handoffs=[handoff1, handoff2]
)
```

### Tool

המחלקה `Tool` מאפשרת להגדיר כלים שה-agent יכול להשתמש בהם. כל כלי מקושר לפונקציה בקוד שלנו.

```python
from openai.agents import Tool

def get_product(product_id: str = None, search: str = None):
    # קוד לקבלת מוצר
    pass

get_product_tool = Tool(name="get_product", function=get_product)
```

ניתן גם להשתמש במקצר `function_tool` כדקורטור:

```python
from openai.agents import function_tool

@function_tool
def get_product(product_id: str = None, search: str = None):
    # קוד לקבלת מוצר
    pass
```

### Handoff

המחלקה `Handoff` מאפשרת להגדיר העברות בין agents. כך ה-agent הראשי יכול להעביר משימות ל-agents מתמחים.

```python
from openai.agents import Handoff

handoff = Handoff(
    name="product_expert",
    agent=product_agent,
    description="מומחה למוצרים"
)
```

### Guardrail

המחלקה `Guardrail` מאפשרת להגדיר מנגנוני הגנה שבודקים את הפעולות של ה-agent לפני ביצוען.

```python
from openai.agents import Guardrail

guardrail = Guardrail(
    client=client,
    model="gpt-4o",
    instructions="בדוק אם הפעולה דורשת אישור מהמשתמש"
)
```

### Thread

המחלקה `Thread` מאפשרת לשמור את היסטוריית השיחה בין המשתמש ל-agent.

```python
from openai.agents import Thread

thread = Thread()
response = agent.run(user_input, thread=thread)
```

### Trace

המחלקה `Trace` מאפשרת לנטר את הפעולות של ה-agent לצורכי דיבוג.

```python
from openai.agents import Trace

with Trace.capture() as trace:
    response = agent.run(user_input)
    trace_file = save_trace(trace)
```

## שימוש ב-SDK בפרויקט שלנו

### 1. הגדרת ה-Agent הראשי המשופר

ב-`agents/main_agent.py`, אנחנו מגדירים את ה-agent הראשי המשופר שמנהל את השיחה עם המשתמש:

```python
from openai.agents import Agent, Handoff, Guardrail, Thread, Trace
from memory.vector_store import AdvancedVectorStore

class EnhancedMainAgent:
    """
    Agent ראשי משופר שמנהל את השיחה עם המשתמש ומעביר משימות ל-Agents מתמחים.
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
        self.memory = AdvancedVectorStore(client)
        self.thread = Thread()
        self.context = AgentContext()
        self.router = AgentRouter(client, model)
        
        # הגדרת ה-agents המתמחים
        self.product_agent = create_product_agent(client, model)
        self.order_agent = create_order_agent(client, model)
        self.coupon_agent = create_coupon_agent(client, model)
        self.category_agent = create_category_agent(client, model)
        self.customer_agent = create_customer_agent(client, model)
        self.report_agent = create_report_agent(client, model)
        self.settings_agent = create_settings_agent(client, model)
        
        # הגדרת guardrail לאישור פעולות חשובות
        self.confirmation_guardrail = Guardrail(
            client=client,
            model=model,
            instructions="""
            בדוק אם הפעולה דורשת אישור מהמשתמש.
            פעולות שדורשות אישור:
            - מחיקת מוצר, הזמנה, קופון, קטגוריה או לקוח
            - עדכון מחיר של מוצר
            - ביטול הזמנה
            - שינוי הגדרות חשובות של החנות
            אם הפעולה דורשת אישור והמשתמש לא אישר במפורש, החזר False עם הסבר.
            אחרת, החזר True.
            """
        )
        
        # הגדרת ה-agent הראשי
        self.agent = Agent(
            client=client,
            model=model,
            instructions="""
            אתה עוזר לניהול חנות WooCommerce בעברית.
            תפקידך לקבל בקשות מהמשתמש ולהעביר אותן ל-agent המתאים:
            - אם הבקשה קשורה למוצרים, העבר ל-product_expert
            - אם הבקשה קשורה להזמנות, העבר ל-order_expert
            - אם הבקשה קשורה לקופונים, העבר ל-coupon_expert
            - אם הבקשה קשורה לקטגוריות, העבר ל-category_expert
            - אם הבקשה קשורה ללקוחות, העבר ל-customer_expert
            - אם הבקשה קשורה לדוחות וניתוח נתונים, העבר ל-report_expert
            - אם הבקשה קשורה להגדרות החנות, העבר ל-settings_expert
            
            לפני ביצוע פעולות חשובות כמו מחיקה או עדכון מחיר, בקש אישור מהמשתמש.
            
            אם המשתמש מבקש לחזור ל-agent הקודם, העבר את הבקשה ל-agent שטיפל בבקשה הקודמת.
            """,
            handoffs=[
                Handoff(name="product_expert", agent=self.product_agent, description="מומחה למוצרים"),
                Handoff(name="order_expert", agent=self.order_agent, description="מומחה להזמנות"),
                Handoff(name="coupon_expert", agent=self.coupon_agent, description="מומחה לקופונים"),
                Handoff(name="category_expert", agent=self.category_agent, description="מומחה לקטגוריות"),
                Handoff(name="customer_expert", agent=self.customer_agent, description="מומחה ללקוחות"),
                Handoff(name="report_expert", agent=self.report_agent, description="מומחה לדוחות וניתוח נתונים"),
                Handoff(name="settings_expert", agent=self.settings_agent, description="מומחה להגדרות החנות")
            ],
            guardrails=[self.confirmation_guardrail]
        )
    
    def run(self, user_input: str) -> str:
        # זיהוי ה-Agent המתאים
        agent_name = self.router.identify_agent(user_input, self.context)
        
        # הוספת מידע הקשר לקלט המשתמש
        enhanced_input = self._enhance_user_input(user_input, agent_name)
        
        # הפעלת ה-agent הראשי עם tracing
        with Trace.capture() as trace:
            # אם זוהה agent ספציפי, העבר ישירות אליו
            if agent_name != "main":
                # העברה ישירה ל-agent המתאים
                response = self.agent.run(
                    enhanced_input,
                    thread=self.thread,
                    handoff_to=agent_name
                )
            else:
                # הפעלה רגילה של ה-agent הראשי
                response = self.agent.run(enhanced_input, thread=self.thread)
            
            # שמירת המידע בזיכרון ועדכון הקשר
            self._update_memory(user_input, response.content, agent_name)
            self.context.add_to_history(user_input, response.content, agent_name)
            
            # שמירת ה-trace לניטור
            trace_file = save_trace(trace)
            
        return response.content
```

### 2. מנגנון זיהוי אוטומטי של ה-Agent המתאים

ב-`agents/main_agent.py`, אנחנו מגדירים מחלקה לזיהוי אוטומטי של ה-Agent המתאים:

```python
class AgentRouter:
    """
    מחלקה לניתוב אוטומטי של בקשות ל-Agent המתאים.
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
        
        # מיפוי נושאים ל-Agents
        self.topic_mapping = {
            "מוצרים": "product_expert",
            "הזמנות": "order_expert",
            "קופונים": "coupon_expert",
            "קטגוריות": "category_expert",
            "לקוחות": "customer_expert",
            "דוחות": "report_expert",
            "הגדרות": "settings_expert"
        }
    
    def identify_agent(self, user_input: str, context: AgentContext) -> str:
        # בדיקה אם המשתמש ביקש במפורש לחזור ל-Agent הקודם
        if any(phrase in user_input.lower() for phrase in ["חזור ל-agent הקודם", "חזור לסוכן הקודם"]):
            previous_agent = context.get_previous_agent()
            if previous_agent:
                return previous_agent
        
        # בדיקה אם המשתמש ביקש במפורש לעבור ל-Agent ספציפי
        for topic, agent_name in self.topic_mapping.items():
            if f"עבור ל-{topic}" in user_input or f"דבר עם מומחה {topic}" in user_input:
                return agent_name
        
        # שימוש ב-GPT לזיהוי הנושא
        prompt = f"""
        זהה את הנושא העיקרי של הבקשה הבאה בהקשר של ניהול חנות WooCommerce.
        בחר נושא אחד בלבד מהרשימה הבאה:
        - מוצרים: כל מה שקשור למוצרים, מחירים, מלאי, תמונות, תיאורים וכו'
        - הזמנות: כל מה שקשור להזמנות, סטטוס הזמנות, משלוחים, החזרים וכו'
        - קופונים: כל מה שקשור לקופונים, הנחות, מבצעים וכו'
        - קטגוריות: כל מה שקשור לקטגוריות מוצרים, תגיות, סיווגים וכו'
        - לקוחות: כל מה שקשור ללקוחות, פרטי לקוח, היסטוריית רכישות וכו'
        - דוחות: כל מה שקשור לדוחות, סטטיסטיקות, ניתוח מכירות וכו'
        - הגדרות: כל מה שקשור להגדרות החנות, תשלומים, משלוחים, מיסים וכו'
        
        הבקשה: {user_input}
        
        החזר רק את שם הנושא, ללא הסברים נוספים.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "אתה מערכת לזיהוי נושאים בהקשר של ניהול חנות WooCommerce."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        
        topic = response.choices[0].message.content.strip().lower()
        
        # התאמת הנושא ל-Agent
        for key, agent_name in self.topic_mapping.items():
            if key.lower() in topic:
                return agent_name
        
        # ברירת מחדל - ה-Agent הראשי
        return "main"
```

### 3. מנגנון שיתוף מידע בין ה-Agents

ב-`agents/main_agent.py`, אנחנו מגדירים מחלקה לשיתוף מידע בין ה-Agents:

```python
class AgentContext:
    """
    מחלקה לשמירת הקשר ומידע משותף בין ה-Agents.
    """
    
    def __init__(self):
        self.shared_data = {}
        self.conversation_history = []
        self.agent_history = []
        self.current_task = None
    
    def add_to_history(self, user_input: str, response: str, agent_name: str):
        """
        מוסיף פריט לשיחה להיסטוריה.
        """
        self.conversation_history.append({
            "user_input": user_input,
            "response": response,
            "agent": agent_name,
            "timestamp": self._get_timestamp()
        })
        
        self.agent_history.append(agent_name)
    
    def set_shared_data(self, key: str, value: Any):
        """
        מגדיר מידע משותף.
        """
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """
        מחזיר מידע משותף.
        """
        return self.shared_data.get(key, default)
    
    def get_previous_agent(self) -> Optional[str]:
        """
        מחזיר את שם ה-Agent הקודם.
        """
        if len(self.agent_history) >= 2:
            return self.agent_history[-2]
        return None
    
    def get_conversation_summary(self, n_last: int = 5) -> str:
        """
        מחזיר סיכום של השיחה האחרונה.
        """
        last_items = self.conversation_history[-n_last:] if n_last > 0 else self.conversation_history
        summary = []
        
        for item in last_items:
            summary.append(f"User: {item['user_input']}")
            summary.append(f"Agent ({item['agent']}): {item['response']}")
            summary.append("")
        
        return "\n".join(summary)
```

### 4. מערכת זיכרון חכמה

ב-`memory/vector_store.py`, אנחנו מגדירים מחלקה למערכת זיכרון חכמה עם יכולות מתקדמות:

```python
class AdvancedVectorStore:
    """
    מחלקה לשמירת מידע בצורה וקטורית עם יכולות מתקדמות.
    """
    
    def __init__(self, client, importance_threshold=0.6, ttl_days=30, use_advanced_embeddings=True):
        self.client = client
        self.importance_threshold = importance_threshold
        self.ttl_days = ttl_days
        self.use_advanced_embeddings = use_advanced_embeddings
        self.importance_scorer = ImportanceScorer(client)
        
        # מודל הטמעה מתקדם
        self.embedding_model = "text-embedding-3-large" if use_advanced_embeddings else "text-embedding-ada-002"
    
    def add_document(self, content, metadata=None, context=None, force_add=False):
        """
        מוסיף מסמך למערכת הזיכרון אם הוא מספיק חשוב.
        """
        # חישוב ציון חשיבות
        importance_score = 1.0 if force_add else self.importance_scorer.score_importance(content, context)
        
        # בדיקה אם המידע מספיק חשוב
        if importance_score < self.importance_threshold and not force_add:
            return None
        
        # הוספת מידע נוסף למטא-דאטה
        if metadata is None:
            metadata = {}
        
        metadata["importance_score"] = importance_score
        metadata["expiry_date"] = (datetime.now() + timedelta(days=self.ttl_days)).isoformat()
        
        # הוספת המסמך לאוסף
        # ...
    
    def forget_old_documents(self):
        """
        מוחק מסמכים ישנים שעברו את תאריך התפוגה.
        """
        current_time = datetime.now().isoformat()
        
        # סינון מסמכים שעברו את תאריך התפוגה
        # ...
```

## יתרונות השימוש ב-SDK

1. **ארכיטקטורה מובנית**: ה-SDK מספק מבנה מוגדר היטב לבניית מערכות מבוססות agents.
2. **מנגנון Handoff מובנה**: ה-SDK מספק מנגנון מובנה להעברת משימות בין agents.
3. **מנגנון Guardrail מובנה**: ה-SDK מספק מנגנון מובנה לבדיקת פעולות לפני ביצוען.
4. **מנגנון Tracing מובנה**: ה-SDK מספק מנגנון מובנה לניטור ודיבוג.
5. **אינטגרציה עם OpenAI API**: ה-SDK מתממשק באופן חלק עם ה-API של OpenAI.

## השיפורים שהוספנו למערכת

1. **זיהוי אוטומטי של ה-Agent המתאים**: המערכת מזהה באופן אוטומטי את ה-Agent המתאים לטיפול בבקשה.
2. **שיתוף מידע בין ה-Agents**: מידע חשוב נשמר ומועבר בין ה-Agents השונים.
3. **מנגנון לחזרה ל-Agent הקודם**: אפשרות לחזור ל-Agent הקודם בשיחה.
4. **מערכת זיכרון חכמה**: זיהוי מידע חשוב, שכחה של מידע ישן, וחיפוש מידע רלוונטי.

## מקורות נוספים

- [תיעוד רשמי של OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [מדריך מהיר](https://openai.github.io/openai-agents-python/quickstart/)
- [דוגמאות](https://openai.github.io/openai-agents-python/examples/)
- [מאגר GitHub](https://github.com/openai/openai-agents-python)
