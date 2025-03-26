import express from 'express';
import http from 'http';
import cors from 'cors';
import dotenv from 'dotenv';
import logger from './utils/logger';
import apiRoutes from './routes/api';
import { socketService } from './services/socketService';
import path from 'path';
import fs from 'fs';

// טעינת משתני סביבה
dotenv.config();

// יצירת ספריות נתונים אם לא קיימות
const dataDir = path.join(process.cwd(), 'data');
const logsDir = path.join(process.cwd(), 'logs');

[dataDir, logsDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    logger.info(`נוצרה ספריה: ${dir}`, { agent: 'Server' });
  }
});

// הגדרת האפליקציה
const app = express();
const PORT = process.env.PORT || 3001;

// ניתוב ה-NODE_ENV לפיתוח אם לא הוגדר
const NODE_ENV = process.env.NODE_ENV || 'development';

// הגדרת CORS
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true
}));

// שימוש ב-JSON middleware
app.use(express.json());

// מידלוור לתיעוד בקשות
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.url}`, {
    agent: 'Server',
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  next();
});

// נתיבי ה-API
app.use('/api', apiRoutes);

// נתיב ברירת מחדל
app.get('/', (req, res) => {
  res.json({
    name: 'WooAgent API',
    version: '1.0.0',
    status: 'ok',
    environment: NODE_ENV
  });
});

// טיפול בנתיבים לא קיימים
app.use((req, res) => {
  logger.warn(`נתיב לא קיים: ${req.method} ${req.url}`, { agent: 'Server' });
  res.status(404).json({
    success: false,
    message: 'נתיב לא קיים'
  });
});

// טיפול בשגיאות
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  const statusCode = 500;
  const errorMessage = err.message || 'שגיאת שרת פנימית';
  
  logger.error(`שגיאת שרת: ${errorMessage}`, {
    agent: 'Server',
    stack: err.stack,
    path: req.path
  });
  
  res.status(statusCode).json({
    success: false,
    message: 'שגיאת שרת פנימית',
    error: NODE_ENV === 'development' ? errorMessage : undefined
  });
});

// יצירת שרת HTTP
const server = http.createServer(app);

// אתחול שירות ה-Socket.IO
socketService.initialize(server);

// הפעלת השרת
server.listen(PORT, () => {
  logger.info(`השרת פועל על פורט ${PORT} בסביבת ${NODE_ENV}`, { agent: 'Server' });
  
  // הצגת כתובת השרת
  const address = `http://localhost:${PORT}`;
  logger.info(`כתובת השרת: ${address}`, { agent: 'Server' });
});

// טיפול בסיום לא צפוי
process.on('uncaughtException', (error) => {
  logger.error(`שגיאה לא צפויה: ${error.message}`, {
    agent: 'Server',
    stack: error.stack
  });
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error(`הבטחה לא מטופלת: ${reason}`, { agent: 'Server' });
});

export default server; 