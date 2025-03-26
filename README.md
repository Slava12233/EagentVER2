# WooAgent - מערכת סוכנים חכמים לניהול חנויות וורדפרס ווקומרס

![WooAgent Logo](wooagent-frontend/public/logo.png)

## מבוא

WooAgent הינה מערכת סוכנים חכמים מבוססת בינה מלאכותית המיועדת לניהול, תמיכה וייעול תהליכים בחנויות מבוססות WooCommerce ב-WordPress. 
המערכת מאפשרת למנהלי החנויות לקבל סיוע ממוקד ומקצועי בניהול המוצרים, הזמנות, לקוחות והיבטים נוספים של החנות.

## מבנה המערכת

הפרויקט מורכב משלושה רכיבים עיקריים:

1. **WooAgent Backend** - שרת Node.js המקשר בין ממשק המשתמש לבין מודול הסוכן החכם.
2. **WooAgent Frontend** - ממשק משתמש מבוסס Next.js עם עיצוב מודרני וריספונסיבי.
3. **WooAgent Core** - ליבת הסוכן החכם המבוססת על Python, המתקשרת עם מודלי שפה גדולים ו-API של WooCommerce.

## יכולות עיקריות

- **צ'אט חכם** - ממשק שיחה אינטראקטיבי המאפשר למשתמש לנהל דיאלוג טבעי עם הסוכן החכם.
- **ניהול מוצרים** - יצירה, עריכה וניהול של מוצרים בחנות WooCommerce.
- **ניהול הזמנות** - מעקב, עדכון וניהול הזמנות מלקוחות.
- **אנליטיקה** - ניתוח נתונים וייצור תובנות לגבי ביצועי החנות.
- **מערכת לוגים מתקדמת** - תיעוד ומעקב אחר פעולות במערכת עם מערכת צעדי ביצוע (Trace) מתקדמת.
- **הגדרות מתקדמות** - אפשרויות התאמה אישית של הסוכן והתנהגותו.
- **אימון מותאם אישית** - יכולת לאמן את הסוכן על נתונים ספציפיים לחנות.

## טכנולוגיות

### Front-End
- **Next.js 15** - מסגרת React מתקדמת עם Server-Side Rendering.
- **TypeScript** - תוספת טיפוסים סטטיים לג'אווהסקריפט.
- **TailwindCSS** - מסגרת CSS מודולרית לעיצוב מהיר.
- **Shadcn UI** - רכיבי ממשק משתמש מתקדמים ונגישים.
- **Socket.IO Client** - תקשורת בזמן אמת עם השרת.

### Back-End
- **Node.js** - סביבת זמן ריצה לג'אווהסקריפט בצד שרת.
- **Express** - מסגרת לבניית API ושירותי ווב.
- **Socket.IO** - תקשורת דו-כיוונית בזמן אמת.
- **TypeScript** - שיפור יציבות, תחזוקתיות ופיתוח הקוד.

### WooAgent Core (Python)
- **Python 3.10+** - שפת תכנות לחישוביות ובינה מלאכותית.
- **OpenAI API** - גישה למודלי שפה מתקדמים כגון GPT-4.
- **Flask** - מסגרת פיתוח ווב קלה לשירותים בצד שרת.
- **WooCommerce API** - תקשורת עם חנויות WooCommerce.
- **SQLite/PostgreSQL** - מסדי נתונים לאחסון מידע.
- **OpenAI Agents SDK** - תשתית לבניית סוכני בינה מלאכותית.

## התקנה והגדרה

### דרישות מקדימות
- Node.js 18+
- Python 3.10+
- npm או yarn
- pip
- חנות WooCommerce פעילה עם הרשאות API

### התקנת הפרונטאנד
```bash
# Clone the repository
git clone https://github.com/yourusername/wooagent.git
cd wooagent/wooagent-frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local

# Start development server
npm run dev
```

### התקנת הבאקאנד
```bash
# Navigate to backend directory
cd ../wooagent-backend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm run dev
```

### התקנת Core Agent
```bash
# Navigate to core agent directory
cd ../woo_agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start the agent server
python app.py
```

## הגדרות סביבה

### פרונטאנד (.env.local)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:3001
```

### באקאנד (.env)
```
PORT=3001
AGENT_API_URL=http://localhost:5000
CORS_ORIGIN=http://localhost:3000
LOG_LEVEL=debug
```

### WooAgent Core (.env)
```
OPENAI_API_KEY=your_openai_api_key
WOOCOMMERCE_URL=https://your-store.com
WOOCOMMERCE_CONSUMER_KEY=your_consumer_key
WOOCOMMERCE_CONSUMER_SECRET=your_consumer_secret
```

## פיתוח ותרומה

אנו מקבלים בברכה תרומות לפרויקט. אנא עקבו אחר השלבים הבאים:

1. Fork את המאגר
2. צרו ענף חדש (`git checkout -b feature/amazing-feature`)
3. בצעו את השינויים שלכם
4. התחייבו לשינויים שלכם (`git commit -m 'הוספת תכונה מדהימה'`)
5. דחפו לענף (`git push origin feature/amazing-feature`)
6. פתחו בקשת משיכה (Pull Request)

## מבנה התיקיות

```
wooagent/
├── wooagent-frontend/       # ממשק משתמש Next.js
│   ├── app/                 # עמודי האפליקציה
│   │   ├── agent-settings/  # הגדרות סוכן
│   │   ├── chat/            # ממשק צ'אט
│   │   ├── dashboard/       # דשבורד ראשי
│   │   ├── logs/            # מערכת לוגים
│   │   ├── store-settings/  # הגדרות חנות
│   │   ├── trace/           # מערכת צעדי ביצוע
│   │   └── training/        # אימון הסוכן
│   ├── components/          # רכיבי UI משותפים
│   ├── hooks/               # React hooks
│   ├── lib/                 # ספריות עזר
│   └── public/              # קבצים סטטיים
│
├── wooagent-backend/        # שרת Node.js
│   ├── src/                 # קוד המקור
│   │   ├── config/          # הגדרות תצורה
│   │   ├── controllers/     # בקרים
│   │   ├── models/          # מודלים
│   │   ├── routes/          # נתיבי API
│   │   ├── services/        # שירותים
│   │   └── utils/           # כלי עזר
│   └── tests/               # בדיקות
│
└── woo_agent/               # סוכן Python
    ├── agents/              # הגדרות סוכנים
    ├── api/                 # נקודות קצה API
    ├── docs/                # תיעוד
    ├── memory/              # מודולי זיכרון
    ├── tests/               # בדיקות
    ├── tools/               # כלים וממשקים
    ├── traces/              # מערכת צעדי ביצוע
    └── utils/               # כלי עזר
```

## תכונות שהתווספו לאחרונה

### מערכת צעדי ביצוע (Trace)
- מעקב מפורט אחר תהליכי החשיבה וקבלת ההחלטות של הסוכן
- ממשק ויזואלי מתקדם להצגת שרשרת הצעדים
- שמירת היסטוריה לניתוח והפקת לקחים

### עמוד הגדרות סוכן
- הגדרת התנהגות הסוכן
- קינפוג מודלי השפה
- התאמת מאפייני תקשורת עם המשתמש

### עמוד אימון
- יכולת להזין דוגמאות ותרחישים
- אימון הסוכן על בסיס התנהגות היסטורית
- יכולת העלאת קבצים לאימון

## סטטוס פיתוח

הפרויקט נמצא בשלבי פיתוח פעילים. הרכיבים הבאים כבר פעילים:

- ✅ תשתית הפרונטאנד
- ✅ תשתית הבאקאנד
- ✅ מערכת לוגים
- ✅ מערכת צעדי ביצוע (Trace)
- ✅ ממשק צ'אט בסיסי
- ✅ הגדרות סוכן
- ✅ תשתית אימון

רכיבים בפיתוח:
- 🔄 שילוב מלא עם WooCommerce API
- 🔄 כלים מתקדמים לניהול מוצרים
- 🔄 מערכת אנליטיקה מתקדמת
- 🔄 דשבורד מלא

## רישיון

המערכת מוגנת בזכויות יוצרים ומופצת תחת רישיון קנייני. לפרטים נוספים, אנא צרו קשר.

## יצירת קשר

למידע נוסף או שאלות, אנא צרו קשר באמצעות:
- **אימייל**: your.email@example.com
- **טלגרם**: @yourusername
- **טוויטר**: @yourusername

---

© 2025 WooAgent. כל הזכויות שמורות. 