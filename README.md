# WooCommerce AI Agent / סוכן AI ל-WooCommerce

## English

An AI-based agent system for managing WooCommerce stores. The system utilizes advanced language models to provide an intuitive natural language interface for store management tasks.

[View Architecture Diagram](docs/images/architecture.txt)

### Features

- **Product management**
  - Create new products with details (name, price, description, attributes)
  - Update existing product information
  - Delete products
  - Search and filter products
  - Manage stock levels
  - Update pricing (regular and sale prices)
  - Manage product images and galleries
  - Handle product variations

- **Category management**
  - Create and organize product categories
  - Assign products to categories
  - Update category hierarchies
  - Delete categories

- **Order tracking and management**
  - View order details
  - Update order status
  - Process refunds
  - Track shipping and fulfillment

- **Coupon creation and management**
  - Create promotional coupons with various discount types
  - Set coupon validity periods
  - Manage usage restrictions
  - Track coupon usage

- **Customer management**
  - View customer information
  - Update customer details
  - Track purchase history
  - Manage customer notes

- **Reporting capabilities**
  - Sales reports
  - Inventory status
  - Customer insights
  - Top-selling products

- **Settings management**
  - Update store settings
  - Configure shipping options
  - Manage payment methods
  - Adjust tax settings

### System Architecture

The WooCommerce AI Agent is built on a multi-agent architecture that delegates specialized tasks to purpose-built agents:

```
┌───────────────┐      ┌────────────────────┐
│               │      │                    │
│    User       │─────▶│    Main Agent      │
│   Request     │      │                    │
│               │      └──────────┬─────────┘
└───────────────┘                 │
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │             │   │             │   │             │   │
│  │  Product    │   │  Category   │   │   Order     │   │
│  │   Agent     │   │   Agent     │   │   Agent     │   │
│  │             │   │             │   │             │   │
│  └─────────────┘   └─────────────┘   └─────────────┘   │
│                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │             │   │             │   │             │   │
│  │  Coupon     │   │  Customer   │   │  Settings   │   │
│  │   Agent     │   │   Agent     │   │   Agent     │   │
│  │             │   │             │   │             │   │
│  └─────────────┘   └─────────────┘   └─────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

1. **Main Agent**: Processes initial user requests and determines which specialized agent should handle the task
2. **Specialized Agents**: Handle domain-specific operations (products, categories, orders, etc.)
3. **WooCommerce API Client**: Manages communication with the WooCommerce REST API
4. **OpenAI Integration**: Powers the natural language understanding and generation

### Request Flow

```
┌───────────┐      ┌────────────┐      ┌────────────┐      ┌───────────┐
│           │      │            │      │            │      │           │
│  User     │─────▶│ Main Agent │─────▶│Specialized │─────▶│WooCommerce│
│ Request   │      │            │      │  Agent     │      │   API     │
│           │      │            │      │            │      │           │
└───────────┘      └────────────┘      └────────────┘      └───────────┘
       ▲                 ▲                   │                  │
       │                 │                   │                  │
       │                 └───────────────────┴──────────────────┘
       │                                │
       └────────────────────────────────┘
                          Response
```

The request flow follows these steps:
1. User sends a request in natural language to the Main Agent
2. Main Agent processes and routes the request to the appropriate Specialized Agent (Product, Category, Order, etc.)
3. Specialized Agent interacts with the WooCommerce API to perform the requested operation
4. Results from WooCommerce API are received by the Specialized Agent, which processes them
5. Specialized Agent sends the processed results back to the Main Agent
6. Main Agent evaluates the response, potentially requests additional information from other agents if needed
7. When the Main Agent is satisfied with the response, it formats the final answer and sends it to the User

This centralized flow ensures the Main Agent maintains full control over the interaction, can perform quality checks on responses, and can coordinate complex operations that involve multiple specialized agents.

### Installation

1. Clone the repository:
```
git clone https://github.com/Slava12233/EagentVER2.git
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure WooCommerce credentials in a `.env` file:
```
WC_URL=your_store_url
WC_CONSUMER_KEY=your_consumer_key
WC_CONSUMER_SECRET=your_consumer_secret
OPENAI_API_KEY=your_openai_api_key
```

4. Run the application:
```
python main.py
```

### Usage Examples

**Creating a new product:**
```
"צור מוצר חדש בשם חולצת כותנה במחיר 99.90 שקל עם תיאור: חולצת כותנה איכותית במבחר צבעים"
```

**Updating stock:**
```
"עדכן את המלאי של מוצר מספר 123 ל-50 יחידות"
```

**Creating a category:**
```
"צור קטגוריה חדשה בשם הלבשה עליונה"
```

**Viewing orders:**
```
"הצג הזמנות אחרונות"
```

### Advanced Features

- **Context Awareness**: The agent maintains conversation context to handle follow-up questions
- **Ambiguity Resolution**: Handles ambiguous requests by asking clarifying questions
- **Error Handling**: Gracefully manages API failures and provides helpful error messages
- **Multilingual Support**: Works with both Hebrew and English inputs

### Testing

Run the test suite to ensure everything is working correctly:

```
python -m pytest
```

For specific test categories:
```
python -m pytest tests/test_e2e.py  # End-to-end tests
python -m pytest tests/test_product_agent.py  # Product agent tests
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## עברית

מערכת סוכן AI לניהול חנויות WooCommerce. המערכת משתמשת במודלים מתקדמים של שפה טבעית כדי לספק ממשק אינטואיטיבי מבוסס שפה טבעית למשימות ניהול חנות.

[צפה בתרשים הארכיטקטורה](docs/images/architecture_hebrew.txt)

### תכונות

- **ניהול מוצרים**
  - יצירת מוצרים חדשים עם פרטים (שם, מחיר, תיאור, תכונות)
  - עדכון מידע על מוצרים קיימים
  - מחיקת מוצרים
  - חיפוש וסינון מוצרים
  - ניהול רמות מלאי
  - עדכון מחירים (רגיל ומבצע)
  - ניהול תמונות וגלריות מוצרים
  - טיפול בווריאציות מוצרים

- **ניהול קטגוריות**
  - יצירה וארגון של קטגוריות מוצרים
  - שיוך מוצרים לקטגוריות
  - עדכון היררכיות קטגוריות
  - מחיקת קטגוריות

- **מעקב וניהול הזמנות**
  - צפייה בפרטי הזמנה
  - עדכון סטטוס הזמנה
  - עיבוד החזרים
  - מעקב אחר משלוח ומילוי הזמנות

- **יצירה וניהול קופונים**
  - יצירת קופונים פרומוציוניים עם סוגי הנחות שונים
  - הגדרת תקופות תוקף לקופונים
  - ניהול הגבלות שימוש
  - מעקב אחר שימוש בקופונים

- **ניהול לקוחות**
  - צפייה במידע על לקוחות
  - עדכון פרטי לקוח
  - מעקב אחר היסטוריית רכישות
  - ניהול הערות לקוח

- **יכולות דיווח**
  - דוחות מכירות
  - סטטוס מלאי
  - תובנות לקוחות
  - מוצרים נמכרים ביותר

- **ניהול הגדרות**
  - עדכון הגדרות חנות
  - הגדרת אפשרויות משלוח
  - ניהול שיטות תשלום
  - התאמת הגדרות מס

### ארכיטקטורת המערכת

סוכן ה-AI של WooCommerce בנוי על ארכיטקטורת מרובת-סוכנים המאצילה משימות מיוחדות לסוכנים ייעודיים:

```
┌───────────────┐      ┌────────────────────┐
│               │      │                    │
│    בקשת      │─────▶│    סוכן ראשי       │
│   משתמש      │      │                    │
│               │      └──────────┬─────────┘
└───────────────┘                 │
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │             │   │             │   │             │   │
│  │   סוכן      │   │    סוכן     │   │    סוכן     │   │
│  │  מוצרים     │   │  קטגוריות   │   │   הזמנות    │   │
│  │             │   │             │   │             │   │
│  └─────────────┘   └─────────────┘   └─────────────┘   │
│                                                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   │
│  │             │   │             │   │             │   │
│  │   סוכן      │   │    סוכן     │   │    סוכן     │   │
│  │  קופונים    │   │   לקוחות    │   │   הגדרות    │   │
│  │             │   │             │   │             │   │
│  └─────────────┘   └─────────────┘   └─────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

1. **סוכן ראשי**: מעבד בקשות משתמש ראשוניות וקובע איזה סוכן מתמחה צריך לטפל במשימה
2. **סוכנים מתמחים**: מטפלים בפעולות ספציפיות לתחום (מוצרים, קטגוריות, הזמנות וכו')
3. **לקוח API של WooCommerce**: מנהל תקשורת עם ה-REST API של WooCommerce
4. **שילוב OpenAI**: מפעיל את הבנת השפה הטבעית והיצירה

### זרימת בקשה

```
┌───────────┐      ┌────────────┐      ┌────────────┐      ┌───────────┐
│           │      │            │      │            │      │           │
│  בקשת    │─────▶│ סוכן ראשי  │─────▶│   סוכן     │─────▶│  API של   │
│ משתמש    │      │            │      │  מתמחה     │      │WooCommerce│
│           │      │            │      │            │      │           │
└───────────┘      └────────────┘      └────────────┘      └───────────┘
       ▲                 ▲                   │                  │
       │                 │                   │                  │
       │                 └───────────────────┴──────────────────┘
       │                                │
       └────────────────────────────────┘
                         תשובה
```

זרימת הבקשה כוללת את השלבים הבאים:
1. המשתמש שולח בקשה בשפה טבעית לסוכן הראשי
2. הסוכן הראשי מעבד ומנתב את הבקשה לסוכן המתמחה המתאים (מוצרים, קטגוריות, הזמנות וכו')
3. הסוכן המתמחה מתקשר עם ה-API של WooCommerce כדי לבצע את הפעולה המבוקשת
4. התוצאות מה-API של WooCommerce מתקבלות על ידי הסוכן המתמחה, אשר מעבד אותן
5. הסוכן המתמחה שולח את התוצאות המעובדות בחזרה לסוכן הראשי
6. הסוכן הראשי מעריך את התשובה, ובמידת הצורך מבקש מידע נוסף מסוכנים אחרים
7. כאשר הסוכן הראשי מרוצה מהתשובה, הוא מעצב את התשובה הסופית ושולח אותה למשתמש

זרימה מרוכזת זו מבטיחה שהסוכן הראשי שומר על שליטה מלאה באינטראקציה, יכול לבצע בדיקות איכות על תשובות, ויכול לתאם פעולות מורכבות שמערבות מספר סוכנים מתמחים.

### התקנה

1. שכפול המאגר:
```
git clone https://github.com/Slava12233/EagentVER2.git
```

2. התקנת תלויות:
```
pip install -r requirements.txt
```

3. הגדרת פרטי התחברות ל-WooCommerce בקובץ `.env`:
```
WC_URL=כתובת_החנות_שלך
WC_CONSUMER_KEY=מפתח_צרכן_שלך
WC_CONSUMER_SECRET=סוד_צרכן_שלך
OPENAI_API_KEY=מפתח_api_של_openai
```

4. הרצת האפליקציה:
```
python main.py
```

### דוגמאות שימוש

**יצירת מוצר חדש:**
```
"צור מוצר חדש בשם חולצת כותנה במחיר 99.90 שקל עם תיאור: חולצת כותנה איכותית במבחר צבעים"
```

**עדכון מלאי:**
```
"עדכן את המלאי של מוצר מספר 123 ל-50 יחידות"
```

**יצירת קטגוריה:**
```
"צור קטגוריה חדשה בשם הלבשה עליונה"
```

**צפייה בהזמנות:**
```
"הצג הזמנות אחרונות"
```

### תכונות מתקדמות

- **מודעות הקשר**: הסוכן שומר על הקשר השיחה כדי לטפל בשאלות המשך
- **פתרון עמימות**: מטפל בבקשות עמומות על ידי שאלת שאלות הבהרה
- **טיפול בשגיאות**: מנהל כשלי API בצורה אלגנטית ומספק הודעות שגיאה מועילות
- **תמיכה רב-לשונית**: עובד עם קלטים בעברית ובאנגלית

### בדיקות

הרץ את חבילת הבדיקות כדי לוודא שהכל עובד כראוי:

```
python -m pytest
```

לקטגוריות בדיקה ספציפיות:
```
python -m pytest tests/test_e2e.py  # בדיקות קצה לקצה
python -m pytest tests/test_product_agent.py  # בדיקות סוכן מוצרים
```

### תרומה לפרויקט

תרומות מתקבלות בברכה! אל תהססו להגיש בקשת משיכה (Pull Request).

1. פצל את המאגר (Fork)
2. צור את ענף התכונה שלך (`git checkout -b feature/amazing-feature`)
3. בצע קומיט לשינויים שלך (`git commit -m 'הוסף תכונה מדהימה'`)
4. דחוף לענף (`git push origin feature/amazing-feature`)
5. פתח בקשת משיכה (Pull Request)
