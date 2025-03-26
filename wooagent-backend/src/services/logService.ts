import fs from 'fs';
import path from 'path';
import readline from 'readline';
import { LogEntry } from '../models/interfaces';
import logger from '../utils/logger';

/**
 * שירות לטיפול בלוגים של המערכת
 */
class LogService {
  private logsDirectory: string = path.join(process.cwd(), 'logs');
  private combinedLogFile: string = path.join(this.logsDirectory, 'combined.log');
  private errorLogFile: string = path.join(this.logsDirectory, 'error.log');
  private maxLogEntries: number = 1000; // מספר מקסימלי של רשומות לוג להחזרה

  constructor() {
    // בדיקה שספריית הלוגים קיימת
    if (!fs.existsSync(this.logsDirectory)) {
      try {
        fs.mkdirSync(this.logsDirectory, { recursive: true });
        logger.info(`נוצרה ספריית לוגים: ${this.logsDirectory}`, { agent: 'LogService' });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger.error(`שגיאה ביצירת ספריית לוגים: ${errorMessage}`, { agent: 'LogService' });
      }
    }
  }

  /**
   * קריאת לוגים מקובץ לוג
   * @param logFile נתיב לקובץ הלוג
   * @param limit מספר שורות מקסימלי לקריאה
   * @param filter פילטר אופציונלי לסינון לוגים
   */
  private async readLogFile(
    logFile: string, 
    limit: number = this.maxLogEntries,
    filter?: { level?: string, agent?: string, search?: string }
  ): Promise<LogEntry[]> {
    const logs: LogEntry[] = [];
    
    // בדיקה אם הקובץ קיים
    if (!fs.existsSync(logFile)) {
      logger.warn(`קובץ לוג לא קיים: ${logFile}`, { agent: 'LogService' });
      return logs;
    }
    
    try {
      const fileStream = fs.createReadStream(logFile);
      const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
      });
      
      // קריאת הקובץ שורה-שורה
      for await (const line of rl) {
        try {
          // התעלמות משורות ריקות
          if (!line.trim()) continue;
          
          // ניסיון לפרסר את שורת הלוג כ-JSON
          const logEntry: LogEntry = JSON.parse(line);
          
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
        } catch (parseError) {
          logger.warn(`שגיאה בפרסור שורת לוג: ${line}`, { agent: 'LogService', error: parseError });
          continue;
        }
      }
      
      // סידור הלוגים מהחדש לישן
      return logs.reverse();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(`שגיאה בקריאת קובץ לוג ${logFile}: ${errorMessage}`, { agent: 'LogService' });
      return [];
    }
  }

  /**
   * קבלת לוגים מאוחדים
   */
  public async getLogs(options: {
    limit?: number,
    level?: string,
    agent?: string,
    search?: string,
    errorOnly?: boolean
  } = {}): Promise<LogEntry[]> {
    const {
      limit = this.maxLogEntries,
      level,
      agent,
      search,
      errorOnly = false
    } = options;
    
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
export const logService = new LogService();
export default logService; 