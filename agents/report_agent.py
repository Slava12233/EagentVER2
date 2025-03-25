#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent דוחות למערכת AI Agents לניהול חנות WooCommerce
-----------------------------------------------------

קובץ זה מגדיר את ה-Agent המתמחה בדוחות, שאחראי על:
- דוחות מכירות
- דוחות לקוחות
- דוחות מוצרים
- ניתוח מגמות
- התראות ביצועים
"""

from .base import Agent, Tool, function_tool

# Dummy tool functions for demonstration
def get_sales_report(period="month", start_date=None, end_date=None):
    """מחזיר דוח מכירות לתקופה מוגדרת"""
    result = {
        "period": period,
        "start_date": start_date or "2023-01-01",
        "end_date": end_date or "2023-01-31",
        "total_sales": "5000.00",
        "total_orders": 50,
        "average_order_value": "100.00"
    }
    return f"דוח מכירות לתקופה {result['period']} ({result['start_date']} עד {result['end_date']}):\n" \
           f"סה\"כ מכירות: ₪{result['total_sales']}\n" \
           f"סה\"כ הזמנות: {result['total_orders']}\n" \
           f"ערך הזמנה ממוצע: ₪{result['average_order_value']}"

def get_customer_report(period="month"):
    """מחזיר דוח לקוחות לתקופה מוגדרת"""
    result = {
        "period": period,
        "total_customers": 100,
        "new_customers": 20,
        "returning_customers": 80,
        "average_spent_per_customer": "150.00"
    }
    return f"דוח לקוחות לתקופה {result['period']}:\n" \
           f"סה\"כ לקוחות: {result['total_customers']}\n" \
           f"לקוחות חדשים: {result['new_customers']}\n" \
           f"לקוחות חוזרים: {result['returning_customers']}\n" \
           f"הוצאה ממוצעת ללקוח: ₪{result['average_spent_per_customer']}"

def get_product_report(period="month"):
    """מחזיר דוח מוצרים לתקופה מוגדרת"""
    result = {
        "period": period,
        "total_products_sold": 200,
        "best_selling_products": [
            {"id": 1, "name": "מוצר 1", "quantity": 50},
            {"id": 2, "name": "מוצר 2", "quantity": 30},
            {"id": 3, "name": "מוצר 3", "quantity": 20}
        ]
    }
    best_products_str = "\n".join([f"- {p['name']}: {p['quantity']} יחידות" for p in result["best_selling_products"]])
    
    return f"דוח מוצרים לתקופה {result['period']}:\n" \
           f"סה\"כ מוצרים שנמכרו: {result['total_products_sold']}\n" \
           f"מוצרים נמכרים ביותר:\n{best_products_str}"

def analyze_trends(metric="sales", period="month", months=3):
    """מנתח מגמות בנתוני החנות"""
    result = {
        "metric": metric,
        "period": period,
        "months": months,
        "trend": "עלייה",
        "percentage_change": "15%",
        "data_points": [
            {"date": "2023-01", "value": "4000.00"},
            {"date": "2023-02", "value": "4500.00"},
            {"date": "2023-03", "value": "5000.00"}
        ]
    }
    data_points_str = "\n".join([f"- {p['date']}: ₪{p['value']}" for p in result["data_points"]])
    
    return f"ניתוח מגמות ב{result['metric']} לתקופה של {result['months']} חודשים:\n" \
           f"מגמה: {result['trend']}\n" \
           f"שינוי באחוזים: {result['percentage_change']}\n" \
           f"נקודות מידע:\n{data_points_str}"

def get_performance_alerts():
    """מחזיר התראות ביצועים"""
    alerts = [
        {"type": "low_stock", "product_id": 1, "product_name": "מוצר 1", "current_stock": 2},
        {"type": "high_sales", "product_id": 2, "product_name": "מוצר 2", "sales_increase": "200%"},
        {"type": "no_sales", "product_id": 3, "product_name": "מוצר 3", "days_without_sales": 30}
    ]
    
    alerts_str = ""
    for alert in alerts:
        if alert["type"] == "low_stock":
            alerts_str += f"- מלאי נמוך: {alert['product_name']} (מזהה: {alert['product_id']}), מלאי נוכחי: {alert['current_stock']}\n"
        elif alert["type"] == "high_sales":
            alerts_str += f"- עלייה במכירות: {alert['product_name']} (מזהה: {alert['product_id']}), עלייה של {alert['sales_increase']}\n"
        elif alert["type"] == "no_sales":
            alerts_str += f"- אין מכירות: {alert['product_name']} (מזהה: {alert['product_id']}), {alert['days_without_sales']} ימים ללא מכירות\n"
    
    return f"התראות ביצועים עדכניות:\n{alerts_str}"

def get_inventory_report(min_stock=None, max_stock=None, out_of_stock_only=False):
    """מחזיר דוח מלאי"""
    products = [
        {"id": 1, "name": "מוצר 1", "stock": 5, "sku": "SKU001"},
        {"id": 2, "name": "מוצר 2", "stock": 0, "sku": "SKU002"},
        {"id": 3, "name": "מוצר 3", "stock": 15, "sku": "SKU003"},
        {"id": 4, "name": "מוצר 4", "stock": 3, "sku": "SKU004"}
    ]
    
    filtered_products = products
    if min_stock is not None:
        filtered_products = [p for p in filtered_products if p["stock"] >= min_stock]
    if max_stock is not None:
        filtered_products = [p for p in filtered_products if p["stock"] <= max_stock]
    if out_of_stock_only:
        filtered_products = [p for p in filtered_products if p["stock"] == 0]
    
    products_str = "\n".join([f"- {p['name']} (מק\"ט: {p['sku']}): {p['stock']} במלאי" for p in filtered_products])
    
    return f"דוח מלאי:\n{products_str}"

def get_order_status_report(period="month"):
    """מחזיר דוח סטטוס הזמנות"""
    result = {
        "period": period,
        "total_orders": 100,
        "statuses": {
            "processing": 20,
            "completed": 70,
            "refunded": 5,
            "cancelled": 5
        }
    }
    
    statuses_str = "\n".join([f"- {status}: {count} הזמנות" for status, count in result["statuses"].items()])
    
    return f"דוח סטטוס הזמנות לתקופה {result['period']}:\n" \
           f"סה\"כ הזמנות: {result['total_orders']}\n" \
           f"התפלגות לפי סטטוס:\n{statuses_str}"

def get_top_products_report(period="month", limit=10):
    """מחזיר דוח מוצרים מובילים"""
    products = [
        {"id": 1, "name": "מוצר פופולרי 1", "quantity": 50, "revenue": "5000.00"},
        {"id": 2, "name": "מוצר פופולרי 2", "quantity": 35, "revenue": "3500.00"},
        {"id": 3, "name": "מוצר פופולרי 3", "quantity": 25, "revenue": "2000.00"}
    ]
    
    products_str = "\n".join([f"- {p['name']}: {p['quantity']} יחידות, הכנסה: ₪{p['revenue']}" for p in products[:limit]])
    
    return f"דוח {limit} המוצרים המובילים לתקופה {period}:\n{products_str}"

def get_revenue_report(start_date, end_date, include_shipping=True):
    """מחזיר דוח הכנסות"""
    result = {
        "period": f"{start_date} עד {end_date}",
        "gross_revenue": "10000.00",
        "shipping_revenue": "500.00",
        "tax_collected": "1700.00",
        "refunds": "300.00",
        "net_revenue": "9700.00"
    }
    
    shipping_text = f"הכנסות ממשלוחים: ₪{result['shipping_revenue']}\n" if include_shipping else ""
    
    return f"דוח הכנסות לתקופה {result['period']}:\n" \
           f"הכנסות ברוטו: ₪{result['gross_revenue']}\n" \
           f"{shipping_text}" \
           f"מס שנגבה: ₪{result['tax_collected']}\n" \
           f"החזרים: ₪{result['refunds']}\n" \
           f"הכנסות נטו: ₪{result['net_revenue']}"

def get_top_sellers(period=30, limit=5):
    """מחזיר דוח מוצרים נמכרים ביותר"""
    products = [
        {"id": 1, "name": "מוצר פופולרי 1", "quantity": 50, "revenue": "5000.00"},
        {"id": 2, "name": "מוצר פופולרי 2", "quantity": 35, "revenue": "3500.00"},
        {"id": 3, "name": "מוצר פופולרי 3", "quantity": 25, "revenue": "2000.00"},
        {"id": 4, "name": "מוצר פופולרי 4", "quantity": 20, "revenue": "1800.00"},
        {"id": 5, "name": "מוצר פופולרי 5", "quantity": 15, "revenue": "1500.00"}
    ]
    
    products_str = "\n".join([f"- {p['name']}: {p['quantity']} יחידות, הכנסה: ₪{p['revenue']}" for p in products[:limit]])
    
    return f"דוח {limit} המוצרים הנמכרים ביותר ב-{period} הימים האחרונים:\n{products_str}"

def get_orders_total(period=30):
    """מחזיר את מספר ההזמנות הכולל"""
    return f"סה\"כ הזמנות ב-{period} הימים האחרונים: 150"

def get_customers_total(period=30):
    """מחזיר את מספר הלקוחות הכולל"""
    return f"סה\"כ לקוחות ב-{period} הימים האחרונים: 120 (מתוכם 35 לקוחות חדשים)"

def get_products_total():
    """מחזיר את מספר המוצרים הכולל בחנות"""
    return "סה\"כ מוצרים בחנות: 253"

def get_stock_status_report():
    """מחזיר דוח על מצב המלאי בחנות"""
    result = {
        "total_products": 253,
        "in_stock": 220,
        "low_stock": 15,
        "out_of_stock": 18,
        "backorder": 5
    }
    return f"דוח מצב המלאי בחנות:\n" \
           f"סה\"כ מוצרים: {result['total_products']}\n" \
           f"במלאי: {result['in_stock']}\n" \
           f"מלאי נמוך: {result['low_stock']}\n" \
           f"אזל מהמלאי: {result['out_of_stock']}\n" \
           f"בהזמנה מראש: {result['backorder']}"

def compare_periods(start_date_current, end_date_current, start_date_previous, end_date_previous):
    """משווה בין שתי תקופות מבחינת מכירות וביצועים"""
    current_period = {
        "period": f"{start_date_current} עד {end_date_current}",
        "total_sales": "8500.00",
        "total_orders": 85,
        "average_order": "100.00"
    }
    
    previous_period = {
        "period": f"{start_date_previous} עד {end_date_previous}",
        "total_sales": "7200.00",
        "total_orders": 72,
        "average_order": "100.00"
    }
    
    sales_change = ((float(current_period["total_sales"]) / float(previous_period["total_sales"])) - 1) * 100
    orders_change = ((current_period["total_orders"] / previous_period["total_orders"]) - 1) * 100
    
    return f"השוואה בין התקופות:\n\n" \
           f"תקופה נוכחית ({current_period['period']}):\n" \
           f"סה\"כ מכירות: ₪{current_period['total_sales']}\n" \
           f"סה\"כ הזמנות: {current_period['total_orders']}\n" \
           f"ערך הזמנה ממוצע: ₪{current_period['average_order']}\n\n" \
           f"תקופה קודמת ({previous_period['period']}):\n" \
           f"סה\"כ מכירות: ₪{previous_period['total_sales']}\n" \
           f"סה\"כ הזמנות: {previous_period['total_orders']}\n" \
           f"ערך הזמנה ממוצע: ₪{previous_period['average_order']}\n\n" \
           f"שינוי במכירות: {sales_change:.1f}%\n" \
           f"שינוי בהזמנות: {orders_change:.1f}%"

def get_category_sales_report(start_date, end_date):
    """מחזיר דוח מכירות לפי קטגוריות"""
    categories = [
        {"id": 1, "name": "ביגוד", "total_sales": "3500.00", "orders": 35, "percent": 41.2},
        {"id": 2, "name": "אלקטרוניקה", "total_sales": "2800.00", "orders": 28, "percent": 32.9},
        {"id": 3, "name": "ספרים", "total_sales": "1200.00", "orders": 12, "percent": 14.1},
        {"id": 4, "name": "מזון", "total_sales": "1000.00", "orders": 10, "percent": 11.8}
    ]
    
    categories_str = "\n".join([f"- {c['name']}: ₪{c['total_sales']} ({c['percent']}%)" for c in categories])
    
    return f"דוח מכירות לפי קטגוריות לתקופה {start_date} עד {end_date}:\n\n" \
           f"סה\"כ מכירות: ₪8500.00\n\n" \
           f"פילוח לפי קטגוריות:\n" \
           f"{categories_str}"

def create_report_agent(client, model="gpt-4o", woo_client=None):
    """
    יוצר agent מתמחה לדוחות.
    
    Args:
        client: לקוח OpenAI
        model: מודל השפה לשימוש (ברירת מחדל: gpt-4o)
        woo_client: לקוח WooCommerce (אופציונלי)
    
    Returns:
        Agent מתמחה לדוחות
    """
    
    # יצירת ה-agent
    report_agent = Agent(
        client=client,
        model=model,
        woo_client=woo_client  # מעביר את woo_client לסוכן
    )
    
    # הגדרת תיאור הסוכן
    report_agent.description = """
    אני סוכן AI מתמחה בהפקת דוחות מהחנות WooCommerce. אני יכול לעזור לך ב:
    - דוחות מכירות לפי תקופות שונות
    - דוחות מלאי ומוצרים
    - דוחות התנהגות לקוחות
    - ניתוח מגמות וביצועי החנות
    - מעקב אחר סטטיסטיקות הזמנות
    - דוחות הכנסות והוצאות

    אשמח לסייע בכל שאלה או בקשה הקשורה לנתונים וניתוח מידע מהחנות!
    
    כשתשאל אותי "איזה סוכן אתה?", אדע להגיד לך שאני סוכן הדוחות של המערכת.
    """
    
    # הוספת כלים כאשר יש חיבור לחנות
    if woo_client:
        @function_tool(name="get_sales_report", description="מפיק דוח מכירות")
        def get_sales_report_tool(period: str = "month", date_min: str = None, date_max: str = None):
            """
            מפיק דוח מכירות.
            
            Args:
                period: תקופת הדוח (day, week, month, year)
                date_min: תאריך התחלה (אופציונלי)
                date_max: תאריך סיום (אופציונלי)
            
            Returns:
                דוח מכירות או הודעת שגיאה
            """
            return get_sales_report(period, date_min, date_max)
        
        @function_tool(name="get_inventory_report", description="מפיק דוח מלאי")
        def get_inventory_report_tool(min_stock: int = None, max_stock: int = None, out_of_stock_only: bool = False):
            """
            מפיק דוח מלאי.
            
            Args:
                min_stock: מלאי מינימלי לסינון (אופציונלי)
                max_stock: מלאי מקסימלי לסינון (אופציונלי)
                out_of_stock_only: האם להציג רק מוצרים שאזלו מהמלאי (ברירת מחדל: False)
            
            Returns:
                דוח מלאי או הודעת שגיאה
            """
            return get_inventory_report(min_stock, max_stock, out_of_stock_only)
        
        @function_tool(name="get_customer_report", description="מפיק דוח לקוחות")
        def get_customer_report_tool(period: str = "month", top_customers: int = 10):
            """
            מפיק דוח לקוחות.
            
            Args:
                period: תקופת הדוח (day, week, month, year)
                top_customers: מספר הלקוחות המובילים להצגה (ברירת מחדל: 10)
            
            Returns:
                דוח לקוחות או הודעת שגיאה
            """
            return get_customer_report(period)
        
        @function_tool(name="get_order_status_report", description="מפיק דוח סטטוס הזמנות")
        def get_order_status_report_tool(period: str = "month"):
            """
            מפיק דוח סטטוס הזמנות.
            
            Args:
                period: תקופת הדוח (day, week, month, year)
            
            Returns:
                דוח סטטוס הזמנות או הודעת שגיאה
            """
            return get_order_status_report(period)
        
        @function_tool(name="get_top_products_report", description="מפיק דוח מוצרים מובילים")
        def get_top_products_report_tool(period: str = "month", limit: int = 10):
            """
            מפיק דוח מוצרים מובילים.
            
            Args:
                period: תקופת הדוח (day, week, month, year)
                limit: מספר המוצרים להצגה (ברירת מחדל: 10)
            
            Returns:
                דוח מוצרים מובילים או הודעת שגיאה
            """
            return get_top_products_report(period, limit)
        
        @function_tool(name="get_revenue_report", description="מפיק דוח הכנסות")
        def get_revenue_report_tool(start_date: str, end_date: str, include_shipping: bool = True):
            """
            מפיק דוח הכנסות.
            
            Args:
                start_date: תאריך התחלה בפורמט YYYY-MM-DD
                end_date: תאריך סיום בפורמט YYYY-MM-DD
                include_shipping: האם לכלול הכנסות ממשלוחים (ברירת מחדל: True)
            
            Returns:
                דוח הכנסות או הודעת שגיאה
            """
            return get_revenue_report(start_date, end_date, include_shipping)
            
        @function_tool(name="get_top_sellers", description="מפיק דוח מוצרים נמכרים ביותר")
        def get_top_sellers_tool(period: int = 30, limit: int = 5):
            """
            מפיק דוח מוצרים נמכרים ביותר.
            
            Args:
                period: תקופה בימים (ברירת מחדל: 30)
                limit: מספר המוצרים להצגה (ברירת מחדל: 5)
            
            Returns:
                דוח מוצרים נמכרים ביותר או הודעת שגיאה
            """
            return get_top_sellers(period, limit)
            
        @function_tool(name="get_orders_total", description="מחזיר את מספר ההזמנות הכולל")
        def get_orders_total_tool(period: int = 30):
            """
            מחזיר את מספר ההזמנות הכולל.
            
            Args:
                period: תקופה בימים (ברירת מחדל: 30)
            
            Returns:
                מספר ההזמנות הכולל או הודעת שגיאה
            """
            return get_orders_total(period)
            
        @function_tool(name="get_customers_total", description="מחזיר את מספר הלקוחות הכולל")
        def get_customers_total_tool(period: int = 30):
            """
            מחזיר את מספר הלקוחות הכולל.
            
            Args:
                period: תקופה בימים (ברירת מחדל: 30)
            
            Returns:
                מספר הלקוחות הכולל או הודעת שגיאה
            """
            return get_customers_total(period)
            
        @function_tool(name="get_products_total", description="מחזיר את מספר המוצרים הכולל")
        def get_products_total_tool():
            """
            מחזיר את מספר המוצרים הכולל.
            
            Returns:
                מספר המוצרים הכולל או הודעת שגיאה
            """
            return get_products_total()
        
        @function_tool(name="get_stock_status_report", description="מפיק דוח על מצב המלאי בחנות")
        def get_stock_status_report_tool():
            """
            מפיק דוח על מצב המלאי בחנות.
            
            Returns:
                מידע על מצב המלאי הנוכחי בחנות
            """
            return get_stock_status_report()
            
        @function_tool(name="compare_periods", description="משווה בין שתי תקופות מבחינת מכירות וביצועים")
        def compare_periods_tool(start_date_current: str, end_date_current: str, start_date_previous: str, end_date_previous: str):
            """
            משווה בין שתי תקופות מבחינת מכירות וביצועים.
            
            Args:
                start_date_current: תאריך התחלת התקופה הנוכחית (YYYY-MM-DD)
                end_date_current: תאריך סיום התקופה הנוכחית (YYYY-MM-DD)
                start_date_previous: תאריך התחלת התקופה הקודמת (YYYY-MM-DD)
                end_date_previous: תאריך סיום התקופה הקודמת (YYYY-MM-DD)
            
            Returns:
                השוואה מפורטת בין שתי התקופות
            """
            return compare_periods(start_date_current, end_date_current, start_date_previous, end_date_previous)

        @function_tool(name="get_category_sales_report", description="מפיק דוח מכירות לפי קטגוריות")
        def get_category_sales_report_tool(start_date: str, end_date: str):
            """
            מפיק דוח מכירות לפי קטגוריות.
            
            Args:
                start_date: תאריך התחלה (YYYY-MM-DD)
                end_date: תאריך סיום (YYYY-MM-DD)
            
            Returns:
                דוח מכירות מפורט לפי קטגוריות
            """
            return get_category_sales_report(start_date, end_date)
        
        # הוספת כל הכלים לסוכן
        report_agent.add_tool(get_sales_report_tool)
        report_agent.add_tool(get_inventory_report_tool)
        report_agent.add_tool(get_customer_report_tool)
        report_agent.add_tool(get_order_status_report_tool)
        report_agent.add_tool(get_top_products_report_tool)
        report_agent.add_tool(get_revenue_report_tool)
        report_agent.add_tool(get_top_sellers_tool)
        report_agent.add_tool(get_orders_total_tool)
        report_agent.add_tool(get_customers_total_tool)
        report_agent.add_tool(get_products_total_tool)
        report_agent.add_tool(get_stock_status_report_tool)
        report_agent.add_tool(compare_periods_tool)
        report_agent.add_tool(get_category_sales_report_tool)
    
    return report_agent
