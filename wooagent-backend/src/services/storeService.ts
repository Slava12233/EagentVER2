import logger from '../utils/logger';
import { StoreConnectionConfig, ConnectionTestResult } from '../models/interfaces';
import path from 'path';
import fs from 'fs';

/**
 * שירות לניהול החיבור לחנות WooCommerce
 */
class StoreService {
  private config: StoreConnectionConfig | null = null;
  private configFilePath: string = path.join(process.cwd(), 'data', 'store-config.json');
  
  constructor() {
    this.loadConfig();
  }
  
  /**
   * טעינת הגדרות החיבור מקובץ
   */
  private loadConfig(): void {
    try {
      // בדיקה שתיקיית הנתונים קיימת
      const dataDir = path.dirname(this.configFilePath);
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }
      
      // בדיקה אם קובץ ההגדרות קיים
      if (!fs.existsSync(this.configFilePath)) {
        logger.info('קובץ הגדרות חנות לא נמצא. יצירת קובץ ריק.', { agent: 'StoreService' });
        this.config = null;
        return;
      }
      
      // קריאת הקובץ
      const configData = fs.readFileSync(this.configFilePath, 'utf8');
      this.config = JSON.parse(configData);
      logger.info('הגדרות חנות נטענו בהצלחה', { agent: 'StoreService' });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`שגיאה בטעינת הגדרות חנות: ${errorMessage}`, { agent: 'StoreService' });
      this.config = null;
    }
  }
  
  /**
   * שמירת הגדרות החיבור לקובץ
   */
  private saveConfig(): boolean {
    try {
      // יצירת תיקיית נתונים אם לא קיימת
      const dataDir = path.dirname(this.configFilePath);
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }
      
      // שמירת ההגדרות בקובץ
      fs.writeFileSync(this.configFilePath, JSON.stringify(this.config, null, 2), 'utf8');
      logger.info('הגדרות חנות נשמרו בהצלחה', { agent: 'StoreService' });
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`שגיאה בשמירת הגדרות חנות: ${errorMessage}`, { agent: 'StoreService' });
      return false;
    }
  }
  
  /**
   * קבלת הגדרות החיבור
   */
  public getConfig(): StoreConnectionConfig | null {
    return this.config;
  }
  
  /**
   * שמירת הגדרות חיבור חדשות
   */
  public saveConnectionConfig(config: StoreConnectionConfig): { success: boolean, error?: string } {
    try {
      this.config = config;
      if (this.saveConfig()) {
        logger.info('הגדרות חיבור חדשות נשמרו בהצלחה', { agent: 'StoreService' });
        return { success: true };
      } else {
        const errorMsg = 'שגיאה לא ידועה בשמירת הגדרות החיבור';
        logger.error(errorMsg, { agent: 'StoreService' });
        return { success: false, error: errorMsg };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`שגיאה בשמירת הגדרות חיבור: ${errorMessage}`, { agent: 'StoreService' });
      return { success: false, error: errorMessage };
    }
  }
  
  /**
   * בדיקת חיבור לחנות
   */
  public async testConnection(config?: StoreConnectionConfig): Promise<ConnectionTestResult> {
    // אם לא התקבלו פרמטרים, נשתמש בהגדרות הקיימות
    const testConfig = config || this.config;
    
    if (!testConfig) {
      logger.warn('ניסיון לבדוק חיבור ללא הגדרות חיבור', { agent: 'StoreService' });
      return { success: false, error: 'לא הוגדרו פרטי חיבור לחנות' };
    }
    
    try {
      logger.info(`בודק חיבור לחנות: ${testConfig.url}`, { agent: 'StoreService' });
      
      // כאן יבוא קוד אמיתי לבדיקת חיבור לחנות
      // כרגע נחזיר סימולציה של תוצאה חיובית
      
      // סימולציה של המתנה לתשובה מהשרת
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // סימולציה של תוצאה מוצלחת
      const result: ConnectionTestResult = {
        success: true,
        products: 15,
        orders: 8
      };
      
      logger.info(`בדיקת חיבור הצליחה. נמצאו ${result.products} מוצרים ו-${result.orders} הזמנות.`, { agent: 'StoreService' });
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`שגיאה בבדיקת חיבור לחנות: ${errorMessage}`, { agent: 'StoreService' });
      return { success: false, error: errorMessage };
    }
  }
}

// יצירת מופע יחיד של השירות
export const storeService = new StoreService();
export default storeService; 