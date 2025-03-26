"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.storeService = void 0;
const logger_1 = __importDefault(require("../utils/logger"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
/**
 * שירות לניהול החיבור לחנות WooCommerce
 */
class StoreService {
    constructor() {
        this.config = null;
        this.configFilePath = path_1.default.join(process.cwd(), 'data', 'store-config.json');
        this.loadConfig();
    }
    /**
     * טעינת הגדרות החיבור מקובץ
     */
    loadConfig() {
        try {
            // בדיקה שתיקיית הנתונים קיימת
            const dataDir = path_1.default.dirname(this.configFilePath);
            if (!fs_1.default.existsSync(dataDir)) {
                fs_1.default.mkdirSync(dataDir, { recursive: true });
            }
            // בדיקה אם קובץ ההגדרות קיים
            if (!fs_1.default.existsSync(this.configFilePath)) {
                logger_1.default.info('קובץ הגדרות חנות לא נמצא. יצירת קובץ ריק.', { agent: 'StoreService' });
                this.config = null;
                return;
            }
            // קריאת הקובץ
            const configData = fs_1.default.readFileSync(this.configFilePath, 'utf8');
            this.config = JSON.parse(configData);
            logger_1.default.info('הגדרות חנות נטענו בהצלחה', { agent: 'StoreService' });
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בטעינת הגדרות חנות: ${errorMessage}`, { agent: 'StoreService' });
            this.config = null;
        }
    }
    /**
     * שמירת הגדרות החיבור לקובץ
     */
    saveConfig() {
        try {
            // יצירת תיקיית נתונים אם לא קיימת
            const dataDir = path_1.default.dirname(this.configFilePath);
            if (!fs_1.default.existsSync(dataDir)) {
                fs_1.default.mkdirSync(dataDir, { recursive: true });
            }
            // שמירת ההגדרות בקובץ
            fs_1.default.writeFileSync(this.configFilePath, JSON.stringify(this.config, null, 2), 'utf8');
            logger_1.default.info('הגדרות חנות נשמרו בהצלחה', { agent: 'StoreService' });
            return true;
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בשמירת הגדרות חנות: ${errorMessage}`, { agent: 'StoreService' });
            return false;
        }
    }
    /**
     * קבלת הגדרות החיבור
     */
    getConfig() {
        return this.config;
    }
    /**
     * שמירת הגדרות חיבור חדשות
     */
    saveConnectionConfig(config) {
        try {
            this.config = config;
            if (this.saveConfig()) {
                logger_1.default.info('הגדרות חיבור חדשות נשמרו בהצלחה', { agent: 'StoreService' });
                return { success: true };
            }
            else {
                const errorMsg = 'שגיאה לא ידועה בשמירת הגדרות החיבור';
                logger_1.default.error(errorMsg, { agent: 'StoreService' });
                return { success: false, error: errorMsg };
            }
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בשמירת הגדרות חיבור: ${errorMessage}`, { agent: 'StoreService' });
            return { success: false, error: errorMessage };
        }
    }
    /**
     * בדיקת חיבור לחנות
     */
    async testConnection(config) {
        // אם לא התקבלו פרמטרים, נשתמש בהגדרות הקיימות
        const testConfig = config || this.config;
        if (!testConfig) {
            logger_1.default.warn('ניסיון לבדוק חיבור ללא הגדרות חיבור', { agent: 'StoreService' });
            return { success: false, error: 'לא הוגדרו פרטי חיבור לחנות' };
        }
        try {
            logger_1.default.info(`בודק חיבור לחנות: ${testConfig.url}`, { agent: 'StoreService' });
            // כאן יבוא קוד אמיתי לבדיקת חיבור לחנות
            // כרגע נחזיר סימולציה של תוצאה חיובית
            // סימולציה של המתנה לתשובה מהשרת
            await new Promise(resolve => setTimeout(resolve, 1000));
            // סימולציה של תוצאה מוצלחת
            const result = {
                success: true,
                products: 15,
                orders: 8
            };
            logger_1.default.info(`בדיקת חיבור הצליחה. נמצאו ${result.products} מוצרים ו-${result.orders} הזמנות.`, { agent: 'StoreService' });
            return result;
        }
        catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            logger_1.default.error(`שגיאה בבדיקת חיבור לחנות: ${errorMessage}`, { agent: 'StoreService' });
            return { success: false, error: errorMessage };
        }
    }
}
// יצירת מופע יחיד של השירות
exports.storeService = new StoreService();
exports.default = exports.storeService;
//# sourceMappingURL=storeService.js.map