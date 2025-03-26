"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.agentService = void 0;
const logger_1 = __importDefault(require("../utils/logger"));
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const socketService_1 = require("./socketService");
const axios_1 = __importDefault(require("axios"));
/**
 * שירות לניהול הסוכן
 */
class AgentService {
    constructor() {
        this.agentProcess = null;
        this.status = {
            isRunning: false,
            connectionStatus: 'disconnected'
        };
        this.startTime = null;
        this.modelName = 'gpt-4o';
        this.pythonPath = 'python'; // ברירת מחדל
        this.agentPath = path_1.default.resolve(process.env.AGENT_PATH || '../woo_agent');
        this.agentPort = 5000; // פורט ברירת מחדל של Flask
        this.lastAgentOutput = []; // מערך לשמירת פלט הסוכן האחרון
        // בדיקת נתיב הסוכן
        if (!fs_1.default.existsSync(this.agentPath)) {
            logger_1.default.warn(`נתיב הסוכן לא נמצא: ${this.agentPath}`, { agent: 'AgentService' });
            // ניסיון למצוא נתיב יחסי
            const relativePath = path_1.default.resolve(process.cwd(), '..', 'woo_agent');
            if (fs_1.default.existsSync(relativePath)) {
                this.agentPath = relativePath;
                logger_1.default.info(`נמצא נתיב יחסי לסוכן: ${relativePath}`, { agent: 'AgentService' });
            }
            else {
                logger_1.default.error(`לא ניתן למצוא נתיב לסוכן. נסה להגדיר AGENT_PATH במשתני הסביבה.`, { agent: 'AgentService' });
            }
        }
    }
    /**
     * הפעלת הסוכן
     */
    async startAgent() {
        if (this.agentProcess) {
            logger_1.default.info('הסוכן כבר פעיל', { agent: 'AgentService' });
            return { success: true };
        }
        try {
            logger_1.default.info(`מנסה להפעיל סוכן מנתיב: ${this.agentPath}`, { agent: 'AgentService' });
            // איפוס מערך הפלט
            this.lastAgentOutput = [];
            // בדיקת קיום קובץ app.py
            const appFilePath = path_1.default.join(this.agentPath, 'app.py');
            if (!fs_1.default.existsSync(appFilePath)) {
                const error = `קובץ app.py לא נמצא בנתיב: ${appFilePath}`;
                logger_1.default.error(error, { agent: 'AgentService' });
                return { success: false, error };
            }
            // הפעלת התהליך
            this.agentProcess = (0, child_process_1.spawn)(this.pythonPath, [appFilePath], {
                cwd: this.agentPath,
                env: { ...process.env, PYTHONUNBUFFERED: '1' }
            });
            const processId = this.agentProcess.pid;
            logger_1.default.info(`הסוכן הופעל עם מזהה תהליך: ${processId}`, { agent: 'AgentService' });
            // טיפול בפלט
            this.agentProcess.stdout?.on('data', (data) => {
                const output = data.toString().trim();
                // שמירת הפלט למקרה שנזדקק לו כתשובה
                this.lastAgentOutput.push(output);
                // הגבלת גודל המערך כדי למנוע דליפת זכרון
                if (this.lastAgentOutput.length > 20) {
                    this.lastAgentOutput.shift();
                }
                logger_1.default.info(`פלט סוכן: ${output}`, { agent: 'AgentService' });
            });
            // טיפול בשגיאות
            this.agentProcess.stderr?.on('data', (data) => {
                const errorOutput = data.toString().trim();
                // שמירת פלט השגיאה גם כן, כי לפעמים מידע חשוב מגיע דרך stderr
                this.lastAgentOutput.push(errorOutput);
                // הגבלת גודל המערך
                if (this.lastAgentOutput.length > 20) {
                    this.lastAgentOutput.shift();
                }
                logger_1.default.error(`שגיאת סוכן: ${errorOutput}`, { agent: 'AgentService' });
            });
            // טיפול בסיום תהליך
            this.agentProcess.on('close', (code) => {
                logger_1.default.info(`הסוכן הסתיים עם קוד: ${code}`, { agent: 'AgentService' });
                this.status = {
                    isRunning: false,
                    connectionStatus: 'disconnected'
                };
                this.agentProcess = null;
                this.startTime = null;
                // עדכון סטטוס לכל הלקוחות
                socketService_1.socketService.broadcastAgentStatus(this.getStatus());
            });
            // עדכון סטטוס
            this.startTime = new Date();
            this.status = {
                isRunning: true,
                startTime: this.startTime.toISOString(),
                uptime: 0,
                modelName: this.modelName,
                connectionStatus: 'connected'
            };
            // עדכון סטטוס לכל הלקוחות
            socketService_1.socketService.broadcastAgentStatus(this.getStatus());
            return { success: true };
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בהפעלת הסוכן: ${errorMessage}`, { agent: 'AgentService' });
            // ניקוי אם התרחשה שגיאה
            if (this.agentProcess) {
                this.agentProcess.kill();
                this.agentProcess = null;
            }
            return { success: false, error: errorMessage };
        }
    }
    /**
     * הפסקת הסוכן
     */
    async stopAgent() {
        if (!this.agentProcess) {
            logger_1.default.info('הסוכן אינו פעיל', { agent: 'AgentService' });
            return { success: true };
        }
        try {
            // ניסיון לסגור בצורה מסודרת
            this.agentProcess.kill();
            logger_1.default.info('הסוכן הופסק', { agent: 'AgentService' });
            // עדכון סטטוס
            this.status = {
                isRunning: false,
                connectionStatus: 'disconnected'
            };
            this.agentProcess = null;
            this.startTime = null;
            // עדכון סטטוס לכל הלקוחות
            socketService_1.socketService.broadcastAgentStatus(this.getStatus());
            return { success: true };
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בהפסקת הסוכן: ${errorMessage}`, { agent: 'AgentService' });
            return { success: false, error: errorMessage };
        }
    }
    /**
     * הפעלה מחדש של הסוכן
     */
    async restartAgent() {
        try {
            // עצירת הסוכן אם הוא פעיל
            if (this.agentProcess) {
                const stopResult = await this.stopAgent();
                if (!stopResult.success) {
                    return stopResult;
                }
            }
            // המתנה קצרה לפני הפעלה מחדש
            await new Promise(resolve => setTimeout(resolve, 1000));
            // הפעלת הסוכן מחדש
            return await this.startAgent();
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בהפעלה מחדש של הסוכן: ${errorMessage}`, { agent: 'AgentService' });
            return { success: false, error: errorMessage };
        }
    }
    /**
     * קבלת סטטוס נוכחי של הסוכן
     */
    getStatus() {
        // חישוב זמן פעילות
        if (this.startTime && this.status.isRunning) {
            const uptime = Math.floor((new Date().getTime() - this.startTime.getTime()) / 1000);
            this.status.uptime = uptime;
        }
        return this.status;
    }
    /**
     * שליחת הודעה לסוכן
     */
    async sendMessage(message) {
        // בדיקה אם הסוכן פעיל
        if (!this.isRunning()) {
            logger_1.default.warn('ניסיון לשלוח הודעה לסוכן שאינו פעיל', { agent: 'AgentService' });
            // הפעלת הסוכן אוטומטית אם אינו פעיל
            try {
                const startResult = await this.startAgent();
                if (!startResult.success) {
                    return {
                        message: `לא ניתן להפעיל את הסוכן: ${startResult.error}`,
                        timestamp: new Date().toISOString()
                    };
                }
                // המתנה לאתחול הסוכן
                await new Promise(resolve => setTimeout(resolve, 3000));
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                logger_1.default.error(`שגיאה בהפעלת הסוכן לפני שליחת הודעה: ${errorMessage}`, { agent: 'AgentService' });
                return {
                    message: `שגיאה בהפעלת הסוכן: ${errorMessage}`,
                    timestamp: new Date().toISOString()
                };
            }
        }
        try {
            // איפוס מערך הפלט לפני שליחת הודעה חדשה
            this.lastAgentOutput = [];
            logger_1.default.info(`שולח הודעה לסוכן: ${message}`, { agent: 'AgentService' });
            // שליחת הודעה לסוכן דרך REST API של Flask
            const response = await axios_1.default.post(`http://localhost:${this.agentPort}/api/chat`, {
                message: message
            });
            logger_1.default.info(`התקבלה תשובה מהסוכן: ${JSON.stringify(response.data)}`, { agent: 'AgentService' });
            // טיפול בתשובה מהסוכן - ניתוח התשובה בכל פורמט אפשרי
            let responseMessage;
            if (typeof response.data === 'string') {
                // אם התשובה היא מחרוזת פשוטה
                responseMessage = response.data;
            }
            else if (response.data && typeof response.data === 'object') {
                // אם התשובה היא אובייקט, ננסה למצוא את התוכן בשדות הנפוצים
                if (response.data.response) {
                    responseMessage = response.data.response;
                }
                else if (response.data.message) {
                    responseMessage = response.data.message;
                }
                else if (response.data.content) {
                    responseMessage = response.data.content;
                }
                else if (response.data.text) {
                    responseMessage = response.data.text;
                }
                else {
                    // אם לא מצאנו שדה מוכר, נהפוך את כל האובייקט למחרוזת
                    responseMessage = JSON.stringify(response.data);
                }
            }
            else {
                // אם לא הצלחנו לחלץ תשובה תקינה
                responseMessage = "התקבלה תשובה מהסוכן אך לא ניתן היה לפענח אותה";
            }
            // אם לא קיבלנו תשובה משמעותית, ננסה להשתמש בפלט שנאסף מהסוכן
            if (!responseMessage || responseMessage === "אין תשובה מהסוכן" || responseMessage === "{}") {
                // חיפוש תשובה במערך הפלט האחרון
                const agentOutputStr = this.lastAgentOutput.join('\n');
                // חיפוש מידע שימושי בפלט
                if (agentOutputStr.includes('נמצאו מוצרים')) {
                    const productInfo = this.extractProductInfo(agentOutputStr);
                    responseMessage = productInfo || "בחנות יש מוצרים, אך אין לי את פרטיהם כרגע.";
                }
                else if (agentOutputStr.includes('לא נמצאו מוצרים')) {
                    responseMessage = "לא מצאתי מוצרים בחנות.";
                }
                else if (agentOutputStr.includes('WooCommerce')) {
                    responseMessage = "קיים חיבור לחנות WooCommerce, אך לא הצלחתי לאסוף מידע על המוצרים.";
                }
                else if (agentOutputStr.length > 0) {
                    // החזרת מיזוג של כל הפלט האחרון אם הוא לא ריק
                    responseMessage = "התקבל פלט מהסוכן, אך הוא לא במבנה מדויק. המידע שקיבלתי: " +
                        agentOutputStr.substring(0, 500) +
                        (agentOutputStr.length > 500 ? "..." : "");
                }
            }
            return {
                message: responseMessage || "אין תשובה מהסוכן",
                timestamp: new Date().toISOString()
            };
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בשליחת הודעה לסוכן: ${errorMessage}`, { agent: 'AgentService' });
            // נחזיר תשובה ידידותית למשתמש במקרה של שגיאה
            return {
                message: `מצטער, לא הצלחתי לקבל תשובה מהסוכן. ייתכן שיש בעיה בחיבור או שהסוכן אינו פעיל כראוי.`,
                timestamp: new Date().toISOString()
            };
        }
    }
    /**
     * מחלץ מידע על מוצרים מפלט הסוכן
     */
    extractProductInfo(output) {
        // חיפוש מידע על מוצרים בפלט של הסוכן
        const productMatch = output.match(/נמצאו מוצרים בחנות:\s*(true|True)/i);
        const storeUrlMatch = output.match(/התחברות לחנות WooCommerce הצליחה:\s*(https:\/\/[^\s]+)/i);
        if (productMatch) {
            let message = "מצאתי מוצרים בחנות";
            if (storeUrlMatch) {
                message += ` בכתובת ${storeUrlMatch[1]}`;
            }
            message += ". אתה יכול לבקש ממני מידע ספציפי יותר על המוצרים, כמו רשימת מוצרים או מידע על מוצר מסוים.";
            return message;
        }
        return null;
    }
    /**
     * בדיקה אם הסוכן פעיל
     */
    isRunning() {
        return this.agentProcess !== null && this.status.isRunning;
    }
}
// יצירת מופע יחיד של השירות
exports.agentService = new AgentService();
exports.default = exports.agentService;
//# sourceMappingURL=agentService.js.map