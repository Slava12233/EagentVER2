"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logService = void 0;
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const readline_1 = __importDefault(require("readline"));
const logger_1 = __importDefault(require("../utils/logger"));
/**
 * שירות לטיפול בלוגים של המערכת
 */
class LogService {
    constructor() {
        this.logsDirectory = path_1.default.join(process.cwd(), 'logs');
        this.combinedLogFile = path_1.default.join(this.logsDirectory, 'combined.log');
        this.errorLogFile = path_1.default.join(this.logsDirectory, 'error.log');
        this.maxLogEntries = 1000; // מספר מקסימלי של רשומות לוג להחזרה
        // בדיקה שספריית הלוגים קיימת
        if (!fs_1.default.existsSync(this.logsDirectory)) {
            try {
                fs_1.default.mkdirSync(this.logsDirectory, { recursive: true });
                logger_1.default.info(`נוצרה ספריית לוגים: ${this.logsDirectory}`, { agent: 'LogService' });
            }
            catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                logger_1.default.error(`שגיאה ביצירת ספריית לוגים: ${errorMessage}`, { agent: 'LogService' });
            }
        }
    }
    /**
     * קריאת לוגים מקובץ לוג
     * @param logFile נתיב לקובץ הלוג
     * @param limit מספר שורות מקסימלי לקריאה
     * @param filter פילטר אופציונלי לסינון לוגים
     */
    async readLogFile(logFile, limit = this.maxLogEntries, filter) {
        const logs = [];
        // בדיקה אם הקובץ קיים
        if (!fs_1.default.existsSync(logFile)) {
            logger_1.default.warn(`קובץ לוג לא קיים: ${logFile}`, { agent: 'LogService' });
            return logs;
        }
        try {
            const fileStream = fs_1.default.createReadStream(logFile);
            const rl = readline_1.default.createInterface({
                input: fileStream,
                crlfDelay: Infinity
            });
            // קריאת הקובץ שורה-שורה
            for await (const line of rl) {
                try {
                    // התעלמות משורות ריקות
                    if (!line.trim())
                        continue;
                    // ניסיון לפרסר את שורת הלוג כ-JSON
                    const logEntry = JSON.parse(line);
                    // פילטור לפי רמת לוג
                    if (filter?.level && logEntry.level !== filter.level) {
                        continue;
                    }
                    // פילטור לפי סוכן
                    if (filter?.agent && logEntry.agent !== filter.agent) {
                        continue;
                    }
                    // פילטור לפי חיפוש טקסט
                    if (filter?.search) {
                        const searchTerm = filter.search.toLowerCase();
                        const messageIncludes = logEntry.message.toLowerCase().includes(searchTerm);
                        const agentIncludes = logEntry.agent.toLowerCase().includes(searchTerm);
                        const detailsInclude = logEntry.details
                            ? JSON.stringify(logEntry.details).toLowerCase().includes(searchTerm)
                            : false;
                        if (!messageIncludes && !agentIncludes && !detailsInclude) {
                            continue;
                        }
                    }
                    logs.push(logEntry);
                    // יציאה מהלולאה אם הגענו למגבלת הרשומות
                    if (logs.length >= limit) {
                        break;
                    }
                }
                catch (parseError) {
                    logger_1.default.warn(`שגיאה בפרסור שורת לוג: ${line}`, { agent: 'LogService', error: parseError });
                    continue;
                }
            }
            // סידור הלוגים מהחדש לישן
            return logs.reverse();
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בקריאת קובץ לוג ${logFile}: ${errorMessage}`, { agent: 'LogService' });
            return [];
        }
    }
    /**
     * קבלת לוגים מאוחדים
     */
    async getLogs(options = {}) {
        const { limit = this.maxLogEntries, level, agent, search, errorOnly = false } = options;
        const filter = { level, agent, search };
        // אם נדרשים רק לוגים מסוג שגיאה, נקרא רק מקובץ השגיאות
        if (errorOnly || level === 'error') {
            return this.readLogFile(this.errorLogFile, limit, filter);
        }
        // אחרת, נקרא מהקובץ המאוחד
        return this.readLogFile(this.combinedLogFile, limit, filter);
    }
}
// יצירת מופע יחיד של השירות
exports.logService = new LogService();
exports.default = exports.logService;
//# sourceMappingURL=logService.js.map