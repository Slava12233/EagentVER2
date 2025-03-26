"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const http_1 = __importDefault(require("http"));
const cors_1 = __importDefault(require("cors"));
const dotenv_1 = __importDefault(require("dotenv"));
const logger_1 = __importDefault(require("./utils/logger"));
const api_1 = __importDefault(require("./routes/api"));
const socketService_1 = require("./services/socketService");
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
// טעינת משתני סביבה
dotenv_1.default.config();
// יצירת ספריות נתונים אם לא קיימות
const dataDir = path_1.default.join(process.cwd(), 'data');
const logsDir = path_1.default.join(process.cwd(), 'logs');
[dataDir, logsDir].forEach(dir => {
    if (!fs_1.default.existsSync(dir)) {
        fs_1.default.mkdirSync(dir, { recursive: true });
        logger_1.default.info(`נוצרה ספריה: ${dir}`, { agent: 'Server' });
    }
});
// הגדרת האפליקציה
const app = (0, express_1.default)();
const PORT = process.env.PORT || 3001;
// ניתוב ה-NODE_ENV לפיתוח אם לא הוגדר
const NODE_ENV = process.env.NODE_ENV || 'development';
// הגדרת CORS
app.use((0, cors_1.default)({
    origin: process.env.CLIENT_URL || 'http://localhost:3000',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: true
}));
// שימוש ב-JSON middleware
app.use(express_1.default.json());
// מידלוור לתיעוד בקשות
app.use((req, res, next) => {
    logger_1.default.info(`${req.method} ${req.url}`, {
        agent: 'Server',
        ip: req.ip,
        userAgent: req.get('User-Agent')
    });
    next();
});
// נתיבי ה-API
app.use('/api', api_1.default);
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
    logger_1.default.warn(`נתיב לא קיים: ${req.method} ${req.url}`, { agent: 'Server' });
    res.status(404).json({
        success: false,
        message: 'נתיב לא קיים'
    });
});
// טיפול בשגיאות
app.use((err, req, res, next) => {
    const statusCode = 500;
    const errorMessage = err.message || 'שגיאת שרת פנימית';
    logger_1.default.error(`שגיאת שרת: ${errorMessage}`, {
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
const server = http_1.default.createServer(app);
// אתחול שירות ה-Socket.IO
socketService_1.socketService.initialize(server);
// הפעלת השרת
server.listen(PORT, () => {
    logger_1.default.info(`השרת פועל על פורט ${PORT} בסביבת ${NODE_ENV}`, { agent: 'Server' });
    // הצגת כתובת השרת
    const address = `http://localhost:${PORT}`;
    logger_1.default.info(`כתובת השרת: ${address}`, { agent: 'Server' });
});
// טיפול בסיום לא צפוי
process.on('uncaughtException', (error) => {
    logger_1.default.error(`שגיאה לא צפויה: ${error.message}`, {
        agent: 'Server',
        stack: error.stack
    });
});
process.on('unhandledRejection', (reason, promise) => {
    logger_1.default.error(`הבטחה לא מטופלת: ${reason}`, { agent: 'Server' });
});
exports.default = server;
//# sourceMappingURL=server.js.map