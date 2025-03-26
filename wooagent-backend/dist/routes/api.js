"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const logger_1 = __importDefault(require("../utils/logger"));
const storeService_1 = require("../services/storeService");
const agentService_1 = require("../services/agentService");
const logService_1 = require("../services/logService");
const uuid_1 = require("uuid");
const router = express_1.default.Router();
/**
 * נתיבים לעבודה עם החנות
 */
// קבלת הגדרות חיבור לחנות
router.get('/store/config', (req, res) => {
    try {
        const config = storeService_1.storeService.getConfig();
        if (!config) {
            return res.status(404).json({
                success: false,
                message: 'לא נמצאו הגדרות חיבור לחנות'
            });
        }
        // מסירת העותק עם הסתרת הסיסמה
        const sanitizedConfig = {
            ...config,
            consumerSecret: config.consumerSecret ? '••••••••••••••••' : ''
        };
        res.json({ success: true, config: sanitizedConfig });
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בקבלת הגדרות חיבור: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({ success: false, message: 'שגיאה בקבלת הגדרות החיבור' });
    }
});
// שמירת הגדרות חיבור לחנות
router.post('/store/config', (req, res) => {
    try {
        const config = req.body;
        // בדיקות תקינות בסיסיות
        if (!config.url || !config.consumerKey || !config.consumerSecret) {
            return res.status(400).json({
                success: false,
                message: 'חסרים שדות חובה בהגדרות החיבור'
            });
        }
        // שמירת ההגדרות
        const result = storeService_1.storeService.saveConnectionConfig(config);
        if (result.success) {
            res.json({ success: true, message: 'הגדרות החיבור נשמרו בהצלחה' });
        }
        else {
            res.status(500).json({
                success: false,
                message: `שגיאה בשמירת הגדרות החיבור: ${result.error}`
            });
        }
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בשמירת הגדרות חיבור: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({ success: false, message: 'שגיאה בשמירת הגדרות החיבור' });
    }
});
// בדיקת חיבור לחנות
router.post('/store/test-connection', async (req, res) => {
    try {
        // אם יש נתוני חיבור בבקשה, נשתמש בהם. אחרת נשתמש בהגדרות השמורות
        const config = req.body.config;
        const result = await storeService_1.storeService.testConnection(config);
        res.json(result);
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בבדיקת חיבור לחנות: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({
            success: false,
            error: 'שגיאת שרת בבדיקת החיבור לחנות'
        });
    }
});
/**
 * נתיבים לעבודה עם האיג'נט
 */
// קבלת סטטוס האיג'נט
router.get('/agent/status', (req, res) => {
    try {
        const status = agentService_1.agentService.getStatus();
        res.json({ success: true, status });
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בקבלת סטטוס האיג'נט: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({
            success: false,
            message: 'שגיאה בקבלת סטטוס האיג\'נט'
        });
    }
});
// הפעלת האיג'נט
router.post('/agent/start', async (req, res) => {
    try {
        const result = await agentService_1.agentService.startAgent();
        if (result.success) {
            res.json({
                success: true,
                message: 'האיג\'נט הופעל בהצלחה',
                status: agentService_1.agentService.getStatus()
            });
        }
        else {
            res.status(500).json({
                success: false,
                message: `שגיאה בהפעלת האיג'נט: ${result.error}`,
                status: agentService_1.agentService.getStatus()
            });
        }
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בהפעלת האיג'נט: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({
            success: false,
            message: 'שגיאה בהפעלת האיג\'נט',
            status: agentService_1.agentService.getStatus()
        });
    }
});
// עצירת האיג'נט
router.post('/agent/stop', async (req, res) => {
    try {
        const result = await agentService_1.agentService.stopAgent();
        if (result.success) {
            res.json({
                success: true,
                message: 'האיג\'נט נעצר בהצלחה',
                status: agentService_1.agentService.getStatus()
            });
        }
        else {
            res.status(500).json({
                success: false,
                message: `שגיאה בעצירת האיג'נט: ${result.error}`,
                status: agentService_1.agentService.getStatus()
            });
        }
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בעצירת האיג'נט: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({
            success: false,
            message: 'שגיאה בעצירת האיג\'נט',
            status: agentService_1.agentService.getStatus()
        });
    }
});
// הפעלה מחדש של האיג'נט
router.post('/agent/restart', async (req, res) => {
    try {
        const result = await agentService_1.agentService.restartAgent();
        if (result.success) {
            res.json({
                success: true,
                message: 'האיג\'נט הופעל מחדש בהצלחה',
                status: agentService_1.agentService.getStatus()
            });
        }
        else {
            res.status(500).json({
                success: false,
                message: `שגיאה בהפעלה מחדש של האיג'נט: ${result.error}`,
                status: agentService_1.agentService.getStatus()
            });
        }
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בהפעלה מחדש של האיג'נט: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({
            success: false,
            message: 'שגיאה בהפעלה מחדש של האיג\'נט',
            status: agentService_1.agentService.getStatus()
        });
    }
});
// שליחת הודעה לאיג'נט
router.post('/chat/message', async (req, res) => {
    try {
        const { message } = req.body;
        if (!message || typeof message !== 'string' || message.trim() === '') {
            return res.status(400).json({
                success: false,
                message: 'הודעה ריקה או לא תקינה'
            });
        }
        const messageId = (0, uuid_1.v4)();
        logger_1.default.info(`התקבלה הודעת צ'אט חדשה: ${message.substring(0, 50)}${message.length > 50 ? '...' : ''}`, {
            agent: 'ChatAPI',
            messageId
        });
        const response = await agentService_1.agentService.sendMessage(message);
        res.json({ success: true, response });
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בשליחת הודעה לאיג'נט: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({
            success: false,
            message: 'שגיאה בשליחת ההודעה לאיג\'נט'
        });
    }
});
// קבלת היסטוריית לוגים
router.get('/logs', async (req, res) => {
    try {
        const { limit, level, agent, search, errorOnly } = req.query;
        // קריאה והחזרת הלוגים
        const logs = await logService_1.logService.getLogs({
            limit: limit ? Number(limit) : undefined,
            level: level,
            agent: agent,
            search: search,
            errorOnly: errorOnly === 'true'
        });
        res.json({
            success: true,
            logs,
            total: logs.length
        });
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger_1.default.error(`שגיאה בקבלת לוגים: ${errorMessage}`, { agent: 'API' });
        res.status(500).json({ success: false, message: 'שגיאה בקבלת לוגים' });
    }
});
exports.default = router;
//# sourceMappingURL=api.js.map