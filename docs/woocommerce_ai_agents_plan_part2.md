# תוכנית מפורטת לבניית מערכת AI Agents לניהול חנות WooCommerce - חלק 2

## תוכן עניינים

6. [מימוש מפורט של הרכיבים (המשך)](#6-מימוש-מפורט-של-הרכיבים-המשך)
   - [6.3 מודול agents (המשך)](#63-מודול-agents-המשך)
   - [6.4 מודול api (המשך)](#64-מודול-api-המשך)
   - [6.5 מודול tools (המשך)](#65-מודול-tools-המשך)
   - [6.6 מודול memory (המשך)](#66-מודול-memory-המשך)
   - [6.7 מודול utils (המשך)](#67-מודול-utils-המשך)
7. [תהליך הפיתוח (המשך)](#7-תהליך-הפיתוח-המשך)
8. [בדיקות ואבטחת איכות (המשך)](#8-בדיקות-ואבטחת-איכות-המשך)
   - [8.1 בדיקות יחידה](#81-בדיקות-יחידה)
   - [8.2 בדיקות אינטגרציה](#82-בדיקות-אינטגרציה)
   - [8.3 בדיקות קצה לקצה](#83-בדיקות-קצה-לקצה)
9. [הוראות הפעלה](#9-הוראות-הפעלה)
   - [9.1 התקנה](#91-התקנה)
   - [9.2 הפעלה](#92-הפעלה)
   - [9.3 שימוש](#93-שימוש)
   - [9.4 ניטור ודיבוג](#94-ניטור-ודיבוג)
10. [הרחבות עתידיות](#10-הרחבות-עתידיות)
    - [10.1 הוספת Agents נוספים](#101-הוספת-agents-נוספים)
    - [10.2 שיפור מערכת הזיכרון](#102-שיפור-מערכת-הזיכרון)
    - [10.3 שיפור מנגנון ה-Handoff](#103-שיפור-מנגנון-ה-handoff)
    - [10.4 הוספת ממשק משתמש גרפי](#104-הוספת-ממשק-משתמש-גרפי)
    - [10.5 שיפור אבטחה](#105-שיפור-אבטחה)

## 6. מימוש מפורט של הרכיבים (המשך)

### 6.3 מודול agents (המשך)

#### 6.3.2 agents/product_agent.py

```python
# agents/product_agent.py
from openai.agents import Agent, Tool
from tools.product_tools import get_product, list_products, create_product, update_product, delete_product

def create_product_agent(client, model="gpt-4o"):
    """יוצר agent מתמחה למוצרים."""
    
    # הגדרת הכלים למוצרים
    get_product_tool = Tool(name="get_product", function=get_product)
    list_products_tool = Tool(name="list_products", function=list_products)
    create_product_tool = Tool(name="create_product", function=create_product)
    update_product_tool = Tool(name="update_product", function=update_product)
    delete_product_tool = Tool(name="delete_product", function=delete_product)
    
    # יצירת ה-agent
    product_agent = Agent(
        client=client,
        model=model,
        instructions="""
        אתה מומחה למוצרים בחנות WooCommerce.
        תפקידך לעזור בניהול מוצרים בחנות:
        - הוספת מוצרים חדשים
        - עריכת מוצרים קיימים
        - מחיקת מוצרים
        - עדכון מלאי
        - עדכון מחירים
        - ניהול תמונות מוצר
        - ניהול וריאציות
        
        השתמש בכלים המתאימים לביצוע הפעולות.
        """,
        tools=[
            get_product_tool,
            list_products_tool,
            create_product_tool,
            update_product_tool,
            delete_product_tool
        ]
    )
    
    return product_agent
```

#### 6.3.3 agents/order_agent.py

```python
# agents/order_agent.py
from openai.agents import Agent, Tool
from tools.order_tools import get_order, list_orders, create_order, update_order, delete_order

def create_order_agent(client, model="gpt-4o"):
    """יוצר agent מתמחה להזמנות."""
    
    # הגדרת הכלים להזמנות
    get_order_tool = Tool(name="get_order", function=get_order)
    list_orders_tool = Tool(name="list_orders", function=list_orders)
    create_order_tool = Tool(name="create_order", function=create_order)
    update_order_tool = Tool(name="update_order", function=update_order)
    delete_order_tool = Tool(name="delete_order", function=delete_order)
    
    # יצירת ה-agent
    order_agent = Agent(
        client=client,
        model=model,
        instructions="""
        אתה מומחה להזמנות בחנות WooCommerce.
        תפקידך לעזור בניהול הזמנות בחנות:
        - צפייה בהזמנות
        - עדכון סטטוס הזמנה
        - ביטול הזמנה
        - יצירת הזמנה חדשה
        - חיפוש הזמנות
        - הפקת חשבוניות
        
        השתמש בכלים המתאימים לביצוע הפעולות.
        """,
        tools=[
            get_order_tool,
            list_orders_tool,
            create_order_tool,
            update_order_tool,
            delete_order_tool
        ]
    )
    
    return order_agent
```

#### 6.3.4 agents/coupon_agent.py

```python
# agents/coupon_agent.py
from openai.agents import Agent, Tool
from tools.coupon_tools import get_coupon, list_coupons, create_coupon, update_coupon, delete_coupon

def create_coupon_agent(client, model="gpt-4o"):
    """יוצר agent מתמחה לקופונים."""
    
    # הגדרת הכלים לקופונים
    get_coupon_tool = Tool(name="get_coupon", function=get_coupon)
    list_coupons_tool = Tool(name="list_coupons", function=list_coupons)
    create_coupon_tool = Tool(name="create_coupon", function=create_coupon)
    update_coupon_tool = Tool(name="update_coupon", function=update_coupon)
    delete_coupon_tool = Tool(name="delete_coupon", function=delete_coupon)
    
    # יצירת ה-agent
    coupon_agent = Agent(
        client=client,
        model=model,
        instructions="""
        אתה מומחה לקופונים בחנות WooCommerce.
        תפקידך לעזור בניהול קופונים בחנות:
        - יצירת קופונים חדשים
        - עריכת קופונים קיימים
        - מחיקת קופונים
        - הגדרת תנאי שימוש
        - הגדרת תאריכי תוקף
        
        השתמש בכלים המתאימים לביצוע הפעולות.
        """,
        tools=[
            get_coupon_tool,
            list_coupons_tool,
            create_coupon_tool,
            update_coupon_tool,
            delete_coupon_tool
        ]
    )
    
    return coupon_agent
```

#### 6.3.5 agents/category_agent.py

```python
# agents/category_agent.py
from openai.agents import Agent, Tool
from tools.category_tools import get_category, list_categories, create_category, update_category, delete_category

def create_category_agent(client, model="gpt-4o"):
    """יוצר agent מתמחה לקטגוריות."""
    
    # הגדרת הכלים לקטגוריות
    get_category_tool = Tool(name="get_category", function=get_category)
    list_categories_tool = Tool(name="list_categories", function=list_categories)
    create_category_tool = Tool(name="create_category", function=create_category)
    update_category_tool = Tool(name="update_category", function=update_category)
    delete_category_tool = Tool(name="delete_category", function=delete_category)
    
    # יצירת ה-agent
    category_agent = Agent(
        client=client,
        model=model,
        instructions="""
        אתה מומחה לקטגוריות בחנות WooCommerce.
        תפקידך לעזור בניהול קטגוריות בחנות:
        - יצירת קטגוריות חדשות
        - עריכת קטגוריות קיימות
        - מחיקת קטגוריות
        - ארגון היררכיית קטגוריות
        - שיוך מוצרים לקטגוריות
        
        השתמש בכלים המתאימים לביצוע הפעולות.
        """,
        tools=[
            get_category_tool,
            list_categories_tool,
            create_category_tool,
            update_category_tool,
            delete_category_tool
        ]
    )
    
    return category_agent
```

### 6.4 מודול api (המשך)

#### 6.4.2 api/order_api.py

```python
# api/order_api.py
from api.woocommerce_client import WooCommerceClient
from config import get_woocommerce_config

def get_woocommerce_client():
    """מחזיר מופע של WooCommerceClient."""
    config = get_woocommerce_config()
    return WooCommerceClient(
        url=config["url"],
        consumer_key=config["consumer_key"],
        consumer_secret=config["consumer_secret"]
    )

def get_order_by_id(order_id):
    """מחזיר הזמנה לפי מזהה."""
    client = get_woocommerce_client()
    return client.get_order(order_id)

def get_orders_by_search(search_term, **params):
    """מחזיר הזמנות לפי חיפוש."""
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_orders(**params)

def get_all_orders(**params):
    """מחזיר את כל ההזמנות."""
    client = get_woocommerce_client()
    return client.get_orders(**params)

def create_new_order(data):
    """יוצר הזמנה חדשה."""
    client = get_woocommerce_client()
    return client.create_order(data)

def update_existing_order(order_id, data):
    """מעדכן הזמנה קיימת."""
    client = get_woocommerce_client()
    return client.update_order(order_id, data)

def delete_existing_order(order_id, force=True):
    """מוחק הזמנה קיימת."""
    client = get_woocommerce_client()
    return client.delete_order(order_id, force)
```

#### 6.4.3 api/coupon_api.py

```python
# api/coupon_api.py
from api.woocommerce_client import WooCommerceClient
from config import get_woocommerce_config

def get_woocommerce_client():
    """מחזיר מופע של WooCommerceClient."""
    config = get_woocommerce_config()
    return WooCommerceClient(
        url=config["url"],
        consumer_key=config["consumer_key"],
        consumer_secret=config["consumer_secret"]
    )

def get_coupon_by_id(coupon_id):
    """מחזיר קופון לפי מזהה."""
    client = get_woocommerce_client()
    return client.get_coupon(coupon_id)

def get_coupons_by_search(search_term, **params):
    """מחזיר קופונים לפי חיפוש."""
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_coupons(**params)

def get_all_coupons(**params):
    """מחזיר את כל הקופונים."""
    client = get_woocommerce_client()
    return client.get_coupons(**params)

def create_new_coupon(data):
    """יוצר קופון חדש."""
    client = get_woocommerce_client()
    return client.create_coupon(data)

def update_existing_coupon(coupon_id, data):
    """מעדכן קופון קיים."""
    client = get_woocommerce_client()
    return client.update_coupon(coupon_id, data)

def delete_existing_coupon(coupon_id, force=True):
    """מוחק קופון קיים."""
    client = get_woocommerce_client()
    return client.delete_coupon(coupon_id, force)
```

#### 6.4.4 api/category_api.py

```python
# api/category_api.py
from api.woocommerce_client import WooCommerceClient
from config import get_woocommerce_config

def get_woocommerce_client():
    """מחזיר מופע של WooCommerceClient."""
    config = get_woocommerce_config()
    return WooCommerceClient(
        url=config["url"],
        consumer_key=config["consumer_key"],
        consumer_secret=config["consumer_secret"]
    )

def get_category_by_id(category_id):
    """מחזיר קטגוריה לפי מזהה."""
    client = get_woocommerce_client()
    return client.get_category(category_id)

def get_categories_by_search(search_term, **params):
    """מחזיר קטגוריות לפי חיפוש."""
    client = get_woocommerce_client()
    params["search"] = search_term
    return client.get_categories(**params)

def get_all_categories(**params):
    """מחזיר את כל הקטגוריות."""
    client = get_woocommerce_client()
    return client.get_categories(**params)

def create_new_category(data):
    """יוצר קטגוריה חדשה."""
    client = get_woocommerce_client()
    return client.create_category(data)

def update_existing_category(category_id, data):
    """מעדכן קטגוריה קיימת."""
    client = get_woocommerce_client()
    return client.update_category(category_id, data)

def delete_existing_category(category_id, force=True):
    """מוחק קטגוריה קיימת."""
    client = get_woocommerce_client()
    return client.delete_category(category_id, force)
```

### 6.5 מודול tools (המשך)

#### 6.5.2 tools/order_tools.py

```python
# tools/order_tools.py
from api.order_api import (
    get_order_by_id,
    get_orders_by_search,
    get_all_orders,
    create_new_order,
    update_existing_order,
    delete_existing_order
)

def get_order(order_id: str = None, search: str = None):
    """
    מחזיר מידע על הזמנה לפי מזהה או חיפוש.
    
    Args:
        order_id: מזהה ההזמנה (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על ההזמנה או ההזמנות שנמצאו
    """
    if order_id:
        return get_order_by_id(order_id)
    elif search:
        return get_orders_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה הזמנה או מונח חיפוש"}

def list_orders(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    status: str = None,
    customer: str = None
):
    """
    מחזיר רשימת הזמנות עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        status: סטטוס ההזמנה (אופציונלי)
        customer: מזהה הלקוח (אופציונלי)
    
    Returns:
        רשימת ההזמנות שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if search:
        params["search"] = search
    
    if status:
        params["status"] = status
    
    if customer:
        params["customer"] = customer
    
    return get_all_orders(**params)

def create_order(
    customer_id: str,
    payment_method: str = "cod",
    payment_method_title: str = "תשלום במזומן",
    line_items: list = None,
    shipping: dict = None,
    billing: dict = None,
    **kwargs
):
    """
    יוצר הזמנה חדשה בחנות.
    
    Args:
        customer_id: מזהה הלקוח
        payment_method: שיטת התשלום (ברירת מחדל: cod)
        payment_method_title: כותרת שיטת התשלום (ברירת מחדל: תשלום במזומן)
        line_items: פריטי ההזמנה (אופציונלי)
        shipping: פרטי משלוח (אופציונלי)
        billing: פרטי חיוב (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        ההזמנה שנוצרה
    """
    data = {
        "customer_id": customer_id,
        "payment_method": payment_method,
        "payment_method_title": payment_method_title,
        **kwargs
    }
    
    if line_items:
        data["line_items"] = line_items
    
    if shipping:
        data["shipping"] = shipping
    
    if billing:
        data["billing"] = billing
    
    return create_new_order(data)

def update_order(
    order_id: str,
    **kwargs
):
    """
    מעדכן הזמנה קיימת בחנות.
    
    Args:
        order_id: מזהה ההזמנה
        **kwargs: פרמטרים לעדכון
    
    Returns:
        ההזמנה המעודכנת
    """
    return update_existing_order(order_id, kwargs)

def delete_order(order_id: str, force: bool = True):
    """
    מוחק הזמנה מהחנות.
    
    Args:
        order_id: מזהה ההזמנה
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_order(order_id, force)
```

#### 6.5.3 tools/coupon_tools.py

```python
# tools/coupon_tools.py
from api.coupon_api import (
    get_coupon_by_id,
    get_coupons_by_search,
    get_all_coupons,
    create_new_coupon,
    update_existing_coupon,
    delete_existing_coupon
)

def get_coupon(coupon_id: str = None, search: str = None):
    """
    מחזיר מידע על קופון לפי מזהה או חיפוש.
    
    Args:
        coupon_id: מזהה הקופון (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על הקופון או הקופונים שנמצאו
    """
    if coupon_id:
        return get_coupon_by_id(coupon_id)
    elif search:
        return get_coupons_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה קופון או מונח חיפוש"}

def list_coupons(
    page: int = 1,
    per_page: int = 10,
    search: str = None
):
    """
    מחזיר רשימת קופונים עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        רשימת הקופונים שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if search:
        params["search"] = search
    
    return get_all_coupons(**params)

def create_coupon(
    code: str,
    discount_type: str,
    amount: str,
    description: str = "",
    date_expires: str = None,
    **kwargs
):
    """
    יוצר קופון חדש בחנות.
    
    Args:
        code: קוד הקופון
        discount_type: סוג ההנחה (percent, fixed_cart, fixed_product)
        amount: סכום ההנחה
        description: תיאור הקופון (אופציונלי)
        date_expires: תאריך תפוגה (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקופון שנוצר
    """
    data = {
        "code": code,
        "discount_type": discount_type,
        "amount": amount,
        "description": description,
        **kwargs
    }
    
    if date_expires:
        data["date_expires"] = date_expires
    
    return create_new_coupon(data)

def update_coupon(
    coupon_id: str,
    **kwargs
):
    """
    מעדכן קופון קיים בחנות.
    
    Args:
        coupon_id: מזהה הקופון
        **kwargs: פרמטרים לעדכון
    
    Returns:
        הקופון המעודכן
    """
    return update_existing_coupon(coupon_id, kwargs)

def delete_coupon(coupon_id: str, force: bool = True):
    """
    מוחק קופון מהחנות.
    
    Args:
        coupon_id: מזהה הקופון
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_coupon(coupon_id, force)
```

#### 6.5.4 tools/category_tools.py

```python
# tools/category_tools.py
from api.category_api import (
    get_category_by_id,
    get_categories_by_search,
    get_all_categories,
    create_new_category,
    update_existing_category,
    delete_existing_category
)

def get_category(category_id: str = None, search: str = None):
    """
    מחזיר מידע על קטגוריה לפי מזהה או חיפוש.
    
    Args:
        category_id: מזהה הקטגוריה (אופציונלי)
        search: מונח חיפוש (אופציונלי)
    
    Returns:
        מידע על הקטגוריה או הקטגוריות שנמצאו
    """
    if category_id:
        return get_category_by_id(category_id)
    elif search:
        return get_categories_by_search(search)
    else:
        return {"error": "נדרש לספק מזהה קטגוריה או מונח חיפוש"}

def list_categories(
    page: int = 1,
    per_page: int = 10,
    search: str = None,
    parent: str = None
):
    """
    מחזיר רשימת קטגוריות עם אפשרויות סינון.
    
    Args:
        page: מספר העמוד
        per_page: מספר פריטים בעמוד
        search: מונח חיפוש (אופציונלי)
        parent: מזהה קטגוריית האב (אופציונלי)
    
    Returns:
        רשימת הקטגוריות שנמצאו
    """
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if search:
        params["search"] = search
    
    if parent:
        params["parent"] = parent
    
    return get_all_categories(**params)

def create_category(
    name: str,
    description: str = "",
    parent: int = 0,
    image: dict = None,
    **kwargs
):
    """
    יוצר קטגוריה חדשה בחנות.
    
    Args:
        name: שם הקטגוריה
        description: תיאור הקטגוריה (אופציונלי)
        parent: מזהה קטגוריית האב (ברירת מחדל: 0)
        image: תמונת הקטגוריה (אופציונלי)
        **kwargs: פרמטרים נוספים
    
    Returns:
        הקטגוריה שנוצרה
    """
    data = {
        "name": name,
        "description": description,
        "parent": parent,
        **kwargs
    }
    
    if image:
        data["image"] = image
    
    return create_new_category(data)

def update_category(
    category_id: str,
    **kwargs
):
    """
    מעדכן קטגוריה קיימת בחנות.
    
    Args:
        category_id: מזהה הקטגוריה
        **kwargs: פרמטרים לעדכון
    
    Returns:
        הקטגוריה המעודכנת
    """
    return update_existing_category(category_id, kwargs)

def delete_category(category_id: str, force: bool = True):
    """
    מוחק קטגוריה מהחנות.
    
    Args:
        category_id: מזהה הקטגוריה
        force: האם למחוק לצמיתות (ברירת מחדל: True)
    
    Returns:
        תוצאת המחיקה
    """
    return delete_existing_category(category_id, force)
```

## 8. בדיקות ואבטחת איכות (המשך)

### 8.1 בדיקות יחידה

לכל רכיב במערכת יש לכתוב בדיקות יחידה שבודקות את הפונקציונליות שלו בנפרד. לדוגמה:

```python
# tests/test_product_tools.py
import unittest
from unittest.mock import patch, MagicMock
from tools.product_tools import get_product, create_product, update_product, delete_product

class TestProductTools(unittest.TestCase):
    @patch('tools.product_tools.get_product_by_id')
    def test_get_product_by_id(self, mock_get_product_by_id):
        # הגדרת התנהגות ה-mock
        mock_get_product_by_id.return_value = {"id": "123", "name": "מוצר לדוגמה"}
        
        # קריאה לפונקציה
        result = get_product(product_id="123")
        
        # בדיקת התוצאה
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["name"], "מוצר לדוגמה")
        
        # בדיקה שהפונקציה נקראה עם הפרמטרים הנכונים
        mock_get_product_by_id.assert_called_once_with("123")
    
    @patch('tools.product_tools.create_new_product')
    def test_create_product(self, mock_create_new_product):
        # הגדרת התנהגות ה-mock
        mock_create_new_product.return_value = {"id": "123", "name": "מוצר חדש"}
        
        # קריאה לפונקציה
        result = create_product(
            name="מוצר חדש",
            regular_price="99.90",
            description="תיאור המוצר"
        )
        
        # בדיקת התוצאה
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["name"], "מוצר חדש")
        
        # בדיקה שהפונקציה נקראה עם הפרמטרים הנכונים
        mock_create_new_product.assert_called_once()
        args = mock_create_new_product.call_args[0][0]
        self.assertEqual(args["name"], "מוצר חדש")
        self.assertEqual(args["regular_price"], "99.90")
        self.assertEqual(args["description"], "תיאור המוצר")
```

### 8.2 בדיקות אינטגרציה

בדיקות אינטגרציה בודקות את האינטראקציה בין הרכיבים השונים במערכת:

```python
# tests/test_integration.py
import unittest
from unittest.mock import patch, MagicMock
from agents.main_agent import MainAgent
from openai import OpenAI

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # יצירת mock ל-OpenAI client
        self.mock_client = MagicMock(spec=OpenAI)
        
        # יצירת ה-agent הראשי
        self.agent = MainAgent(self.mock_client)
    
    @patch('agents.product_agent.get_product')
    def test_product_handoff(self, mock_get_product):
        # הגדרת התנהגות ה-mock
        mock_get_product.return_value = {"id": "123", "name": "מוצר לדוגמה"}
        
        # הגדרת התנהגות ה-mock של OpenAI
        self.mock_client.chat.completions.create.return_value.choices[0].message.content = "אני אעביר את השאלה למומחה המוצרים."
        
        # קריאה לפונקציה
        result = self.agent.run("מה המחיר של מוצר 123?")
        
        # בדיקה שהיה handoff למומחה המוצרים
        self.assertIn("מומחה המוצרים", result)
```

### 8.3 בדיקות קצה לקצה

בדיקות קצה לקצה בודקות את המערכת כולה עם חנות WooCommerce אמיתית:

```python
# tests/test_e2e.py
import unittest
import os
from openai import OpenAI
from agents.main_agent import MainAgent
from dotenv import load_dotenv

class TestE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # טעינת משתני סביבה
        load_dotenv()
        
        # יצירת לקוח OpenAI
        cls.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # יצירת ה-agent הראשי
        cls.agent = MainAgent(cls.client)
    
    def test_get_product(self):
        # קריאה לפונקציה
        result = self.agent.run("הצג לי את המוצר עם המזהה 123")
        
        # בדיקה שהתוצאה מכילה מידע על המוצר
        self.assertIn("123", result)
```

## 9. הוראות הפעלה

### 9.1 התקנה

1. הורד את קוד המקור מה-repository:
   ```bash
   git clone https://github.com/your-username/woo-agent.git
   cd woo-agent
   ```

2. התקן את התלויות:
   ```bash
   pip install -r requirements.txt
   ```

3. צור קובץ `.env` עם הפרטים הבאים:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   WOO_URL=https://your-woocommerce-site.com
   WOO_CONSUMER_KEY=ck_your-consumer-key
   WOO_CONSUMER_SECRET=cs_your-consumer-secret
   ```

### 9.2 הפעלה

הפעל את המערכת באמצעות הפקודה:
```bash
python main.py
```

### 9.3 שימוש

לאחר הפעלת המערכת, תוכל לתקשר עם ה-Agent באמצעות שיחת צ'אט בעברית. לדוגמה:

- "הצג לי את כל המוצרים בחנות"
- "הוסף מוצר חדש בשם 'חולצה כחולה' במחיר 99.90"
- "עדכן את המחיר של מוצר מספר 123 ל-149.90"
- "הצג לי את ההזמנות האחרונות"
- "צור קופון הנחה של 10% בשם 'קיץ2023'"

כדי לצאת מהמערכת, הקלד `exit`.

### 9.4 ניטור ודיבוג

המערכת שומרת את כל ה-traces בתיקיית `traces`. כל trace מכיל מידע מפורט על הפעולות שבוצעו, כולל:

- הודעות המשתמש
- תגובות ה-Agent
- קריאות לכלים
- העברות (handoffs) בין ה-Agents
- בדיקות guardrail

ניתן לנתח את ה-traces באמצעות הפונקציה `analyze_trace` במודול `utils.tracing`.

## 10. הרחבות עתידיות

### 10.1 הוספת Agents נוספים

ניתן להרחיב את המערכת על ידי הוספת Agents נוספים לטיפול בתחומים נוספים של WooCommerce:

- **Agent לקוחות**: טיפול בלקוחות, כולל יצירת לקוחות חדשים, עדכון פרטי לקוחות, וצפייה בהיסטוריית הזמנות של לקוחות
- **Agent דוחות**: הפקת דוחות מכירות, מלאי, ולקוחות
- **Agent הגדרות**: שינוי הגדרות החנות, כגון שיטות תשלום, שיטות משלוח, ומיסים
- **Agent SEO**: טיפול בהיבטי SEO של החנות, כגון מטא-תיאורים, כותרות, וקישורים

### 10.2 שיפור מערכת הזיכרון

ניתן לשפר את מערכת הזיכרון על ידי:

- הוספת מנגנון לזיהוי ושמירה של מידע חשוב בלבד
- שימוש במאגרי וקטורים מתקדמים יותר כמו Pinecone או Weaviate
- הוספת מנגנון לשכחה של מידע ישן או לא רלוונטי

### 10.3 שיפור מנגנון ה-Handoff

ניתן לשפר את מנגנון ה-Handoff על ידי:

- הוספת מנגנון לזיהוי אוטומטי של ה-Agent המתאים
- הוספת מנגנון לשיתוף מידע בין ה-Agents
- הוספת מנגנון לחזרה ל-Agent הקודם

### 10.4 הוספת ממשק משתמש גרפי

ניתן להוסיף ממשק משתמש גרפי למערכת, כגון:

- אפליקציית ווב
- אפליקציית דסקטופ
- אפליקציית מובייל
- אינטגרציה עם פלטפורמות צ'אט כמו Slack או Discord

### 10.5 שיפור אבטחה

ניתן לשפר את אבטחת המערכת על ידי:

- הוספת מנגנון אימות משתמשים
- הצפנת התקשורת עם WooCommerce API
- הגבלת הרשאות לפעולות מסוימות
- הוספת מנגנון לתיעוד פעולות רגישות
