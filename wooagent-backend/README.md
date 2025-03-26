# WooAgent Backend

צד שרת (Backend) למערכת WooAgent - סוכן AI חכם לניהול חנות WooCommerce.

## דרישות מקדימות

- Node.js 18 ומעלה
- Python 3.10 ומעלה (להפעלת הסוכן)
- WooCommerce API מוגדר בחנות שלך

## התקנה

1. התקן את תלויות Node.js:

```bash
npm install
```

2. קבע את משתני הסביבה בקובץ `.env`:

```
PORT=3001
NODE_ENV=development
OPENAI_API_KEY=your-api-key-here
LOG_LEVEL=debug
AGENT_PATH=../woo_agent  # נתיב לקוד הסוכן
```

3. בנה את הפרויקט:

```bash
npm run build
```

## הרצה

להרצת הפרויקט במצב פיתוח:

```bash
npm run dev
```

להרצת הפרויקט במצב ייצור:

```bash
npm start
```

## מבנה הפרויקט

- `src/index.ts` - נקודת הכניסה הראשית
- `src/server.ts` - הגדרות שרת ה-Express
- `src/routes/` - הגדרות נתיבי API
- `src/services/` - שירותים שונים (סוכן, לוגים, חנות, וכו')
- `src/utils/` - כלי עזר כלליים
- `src/models/` - ממשקים והגדרות מודלים של נתונים

## נתיבי API

### חנות

- `GET /api/store/config` - קבלת הגדרות חיבור לחנות
- `POST /api/store/config` - שמירת הגדרות חיבור לחנות
- `POST /api/store/test-connection` - בדיקת חיבור לחנות

### סוכן

- `GET /api/agent/status` - קבלת סטטוס הסוכן
- `POST /api/agent/start` - הפעלת הסוכן
- `POST /api/agent/stop` - עצירת הסוכן
- `POST /api/agent/restart` - הפעלה מחדש של הסוכן

### צ'אט

- `POST /api/chat/message` - שליחת הודעה לסוכן

### לוגים

- `GET /api/logs` - קבלת היסטוריית לוגים (עם אפשרויות פילטור)

## חיבור Socket.IO

השרת מציע חיבור Socket.IO בנתיב הבסיסי של השרת, עם האירועים הבאים:

- `connection_status` - סטטוס חיבור
- `log` - לוגים בזמן אמת
- `chat_response` - תשובות צ'אט מהסוכן
- `agent_status` - עדכוני סטטוס של הסוכן

## פיתוח עתידי

- הוספת תמיכה בתבניות צ'אט מותאמות אישית
- ניהול תוכן מתקדם (מוצרים, הזמנות, לקוחות)
- ויזואליזציות ודוחות נתונים
- אינטגרציה עם כלים נוספים 