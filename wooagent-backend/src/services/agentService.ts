import logger from '../utils/logger';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import { AgentStatus } from '../models/interfaces';
import fs from 'fs';
import { v4 as uuidv4 } from 'uuid';
import { socketService } from './socketService';
import axios from 'axios';

/**
 * שירות לניהול הסוכן
 */
class AgentService {
  private agentProcess: ChildProcess | null = null;
  private status: AgentStatus = {
    isRunning: false,
    connectionStatus: 'disconnected'
  };
  private startTime: Date | null = null;
  private modelName: string = 'gpt-4o';
  private pythonPath: string = 'python'; // ברירת מחדל
  private agentPath: string = path.resolve(process.env.AGENT_PATH || '../woo_agent');
  private agentPort: number = 5000; // פורט ברירת מחדל של Flask
  private lastAgentOutput: string[] = []; // מערך לשמירת פלט הסוכן האחרון

  constructor() {
    // בדיקת נתיב הסוכן
    if (!fs.existsSync(this.agentPath)) {
      logger.warn(`נתיב הסוכן לא נמצא: ${this.agentPath}`, 'AgentService');
      
      // ניסיון למצוא נתיב יחסי
      const relativePath = path.resolve(process.cwd(), '..', 'woo_agent');
      if (fs.existsSync(relativePath)) {
        this.agentPath = relativePath;
        logger.info(`נמצא נתיב יחסי לסוכן: ${relativePath}`, 'AgentService');
      } else {
        logger.error(`לא ניתן למצוא נתיב לסוכן. נסה להגדיר AGENT_PATH במשתני הסביבה.`, 'AgentService');
      }
    }
  }

  /**
   * הפעלת הסוכן
   */
  public async startAgent(): Promise<{ success: boolean, error?: string }> {
    if (this.agentProcess) {
      logger.info('הסוכן כבר פעיל', 'AgentService');
      return { success: true };
    }

    try {
      const trace = logger.startTrace('הפעלת הסוכן', 'AgentService');
      
      trace.addStep(`מנסה להפעיל סוכן מנתיב: ${this.agentPath}`);
      
      // איפוס מערך הפלט
      this.lastAgentOutput = [];
      
      // בדיקת קיום קובץ app.py
      const appFilePath = path.join(this.agentPath, 'app.py');
      if (!fs.existsSync(appFilePath)) {
        const error = `קובץ app.py לא נמצא בנתיב: ${appFilePath}`;
        trace.error(error);
        logger.error(error, 'AgentService');
        return { success: false, error };
      }

      trace.addStep('הפעלת תהליך Python');
      
      // הפעלת התהליך
      this.agentProcess = spawn(this.pythonPath, [appFilePath], {
        cwd: this.agentPath,
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });

      const processId = this.agentProcess.pid;
      trace.addStep(`הסוכן הופעל עם מזהה תהליך: ${processId}`);
      logger.info(`הסוכן הופעל עם מזהה תהליך: ${processId}`, 'AgentService');

      // טיפול בפלט
      this.agentProcess.stdout?.on('data', (data) => {
        const output = data.toString().trim();
        // שמירת הפלט למקרה שנזדקק לו כתשובה
        this.lastAgentOutput.push(output);
        // הגבלת גודל המערך כדי למנוע דליפת זכרון
        if (this.lastAgentOutput.length > 20) {
          this.lastAgentOutput.shift();
        }
        logger.info(`פלט סוכן: ${output}`, 'AgentService');
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
        logger.error(`שגיאת סוכן: ${errorOutput}`, 'AgentService');
      });

      // טיפול בסיום תהליך
      this.agentProcess.on('close', (code) => {
        logger.info(`הסוכן הסתיים עם קוד: ${code}`, 'AgentService');
        this.status = {
          isRunning: false,
          connectionStatus: 'disconnected'
        };
        this.agentProcess = null;
        this.startTime = null;
        
        // עדכון סטטוס לכל הלקוחות
        socketService.broadcastAgentStatus(this.getStatus());
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
      socketService.broadcastAgentStatus(this.getStatus());
      
      trace.complete('הפעלת הסוכן הושלמה בהצלחה');
      return { success: true };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      const trace = logger.startTrace('שגיאה בהפעלת הסוכן', 'AgentService');
      trace.error(`שגיאה בהפעלת הסוכן: ${errorMessage}`, { stack: error instanceof Error ? error.stack : undefined });
      logger.error(`שגיאה בהפעלת הסוכן: ${errorMessage}`, 'AgentService');
      
      // ניקוי אם התרחשה שגיאה
      if (this.agentProcess) {
        this.agentProcess.kill();
        this.agentProcess = null;
      }
      
      trace.complete('הטיפול בשגיאה הושלם');
      return { success: false, error: errorMessage };
    }
  }

  /**
   * הפסקת הסוכן
   */
  public async stopAgent(): Promise<{ success: boolean, error?: string }> {
    if (!this.agentProcess) {
      logger.info('הסוכן אינו פעיל', 'AgentService');
      return { success: true };
    }

    try {
      const trace = logger.startTrace('הפסקת הסוכן', 'AgentService');
      
      // ניסיון לסגור בצורה מסודרת
      trace.addStep('שולח אות סיום לתהליך הסוכן');
      this.agentProcess.kill();
      
      logger.info('הסוכן הופסק', 'AgentService');
      
      // עדכון סטטוס
      this.status = {
        isRunning: false,
        connectionStatus: 'disconnected'
      };
      this.agentProcess = null;
      this.startTime = null;
      
      // עדכון סטטוס לכל הלקוחות
      socketService.broadcastAgentStatus(this.getStatus());
      
      trace.complete('הסוכן הופסק בהצלחה');
      return { success: true };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      const trace = logger.startTrace('שגיאה בהפסקת הסוכן', 'AgentService');
      trace.error(`שגיאה בהפסקת הסוכן: ${errorMessage}`);
      logger.error(`שגיאה בהפסקת הסוכן: ${errorMessage}`, 'AgentService');
      trace.complete('הטיפול בשגיאה הושלם');
      return { success: false, error: errorMessage };
    }
  }

  /**
   * הפעלה מחדש של הסוכן
   */
  public async restartAgent(): Promise<{ success: boolean, error?: string }> {
    try {
      const trace = logger.startTrace('הפעלה מחדש של הסוכן', 'AgentService');
      
      // עצירת הסוכן אם הוא פעיל
      if (this.agentProcess) {
        trace.addStep('עוצר את הסוכן הנוכחי');
        const stopResult = await this.stopAgent();
        if (!stopResult.success) {
          trace.error(`שגיאה בעצירת הסוכן: ${stopResult.error}`);
          return stopResult;
        }
      }
      
      // המתנה קצרה לפני הפעלה מחדש
      trace.addStep('ממתין לפני הפעלה מחדש');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // הפעלת הסוכן מחדש
      trace.addStep('מפעיל את הסוכן מחדש');
      const startResult = await this.startAgent();
      
      if (startResult.success) {
        trace.complete('הפעלה מחדש הצליחה');
      } else {
        trace.error(`הפעלה מחדש נכשלה: ${startResult.error}`);
      }
      
      return startResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      const trace = logger.startTrace('שגיאה בהפעלה מחדש', 'AgentService');
      trace.error(`שגיאה בהפעלה מחדש של הסוכן: ${errorMessage}`);
      logger.error(`שגיאה בהפעלה מחדש של הסוכן: ${errorMessage}`, 'AgentService');
      trace.complete('הטיפול בשגיאה הושלם');
      return { success: false, error: errorMessage };
    }
  }

  /**
   * קבלת סטטוס נוכחי של הסוכן
   */
  public getStatus(): AgentStatus {
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
  public async sendMessage(message: string): Promise<{ message: string, timestamp: string }> {
    const trace = logger.startTrace('שליחת הודעה לסוכן', 'AgentService');
    
    // בדיקה אם הסוכן פעיל
    if (!this.isRunning()) {
      trace.addStep('הסוכן אינו פעיל, מנסה להפעיל אותו אוטומטית');
      logger.warn('ניסיון לשלוח הודעה לסוכן שאינו פעיל', 'AgentService');
      
      // הפעלת הסוכן אוטומטית אם אינו פעיל
      try {
        const startResult = await this.startAgent();
        if (!startResult.success) {
          const errorMsg = `לא ניתן להפעיל את הסוכן: ${startResult.error}`;
          trace.error(errorMsg);
          trace.complete('הפעלת הסוכן נכשלה');
          return {
            message: errorMsg,
            timestamp: new Date().toISOString()
          };
        }
        
        // המתנה לאתחול הסוכן
        trace.addStep('ממתין לאתחול הסוכן');
        await new Promise(resolve => setTimeout(resolve, 3000));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        trace.error(`שגיאה בהפעלת הסוכן לפני שליחת הודעה: ${errorMessage}`);
        logger.error(`שגיאה בהפעלת הסוכן לפני שליחת הודעה: ${errorMessage}`, 'AgentService');
        
        trace.complete('הפעלת הסוכן נכשלה');
        return {
          message: `שגיאה בהפעלת הסוכן: ${errorMessage}`,
          timestamp: new Date().toISOString()
        };
      }
    }
    
    try {
      // איפוס מערך הפלט לפני שליחת הודעה חדשה
      this.lastAgentOutput = [];
      
      trace.addStep(`שולח בקשה לסוכן: ${message.substring(0, 30)}${message.length > 30 ? '...' : ''}`);
      logger.info(`שולח הודעה לסוכן: ${message}`, 'AgentService');
      
      // שליחת הודעה לסוכן דרך REST API של Flask
      trace.addStep('מתבצעת קריאת API לשרת הסוכן');
      const startTime = Date.now();
      const response = await axios.post(`http://localhost:${this.agentPort}/api/chat`, {
        message: message
      });
      const duration = Date.now() - startTime;
      trace.addStep(`התקבלה תשובה מהסוכן (${duration}ms)`);
      
      logger.info(`התקבלה תשובה מהסוכן: ${JSON.stringify(response.data)}`, 'AgentService');
      
      // טיפול בתשובה מהסוכן - ניתוח התשובה בכל פורמט אפשרי
      let responseMessage: string;
      
      if (typeof response.data === 'string') {
        // אם התשובה היא מחרוזת פשוטה
        responseMessage = response.data;
      } else if (response.data && typeof response.data === 'object') {
        // אם התשובה היא אובייקט, ננסה למצוא את התוכן בשדות הנפוצים
        if (response.data.response) {
          responseMessage = response.data.response;
        } else if (response.data.message) {
          responseMessage = response.data.message;
        } else if (response.data.content) {
          responseMessage = response.data.content;
        } else if (response.data.text) {
          responseMessage = response.data.text;
        } else {
          // אם לא מצאנו שדה מוכר, נהפוך את כל האובייקט למחרוזת
          responseMessage = JSON.stringify(response.data);
        }
      } else {
        // אם לא הצלחנו לחלץ תשובה תקינה
        responseMessage = "התקבלה תשובה מהסוכן אך לא ניתן היה לפענח אותה";
      }
      
      // אם לא קיבלנו תשובה משמעותית, ננסה להשתמש בפלט שנאסף מהסוכן
      if (!responseMessage || responseMessage === "אין תשובה מהסוכן" || responseMessage === "{}") {
        trace.addStep('מנסה לחלץ תשובה מפלט הסוכן');
        // חיפוש תשובה במערך הפלט האחרון
        const agentOutputStr = this.lastAgentOutput.join('\n');
        
        // חיפוש מידע שימושי בפלט
        if (agentOutputStr.includes('נמצאו מוצרים')) {
          const productInfo = this.extractProductInfo(agentOutputStr);
          responseMessage = productInfo || "בחנות יש מוצרים, אך אין לי את פרטיהם כרגע.";
          trace.addStep('נמצא מידע על מוצרים בפלט הסוכן');
        } else if (agentOutputStr.includes('לא נמצאו מוצרים')) {
          responseMessage = "לא מצאתי מוצרים בחנות.";
          trace.addStep('לא נמצאו מוצרים בחנות');
        } else if (agentOutputStr.includes('WooCommerce')) {
          responseMessage = "קיים חיבור לחנות WooCommerce, אך לא הצלחתי לאסוף מידע על המוצרים.";
          trace.addStep('נמצא חיבור ל-WooCommerce אך אין מידע על מוצרים');
        } else if (agentOutputStr.length > 0) {
          // החזרת מיזוג של כל הפלט האחרון אם הוא לא ריק
          responseMessage = "התקבל פלט מהסוכן, אך הוא לא במבנה מדויק. המידע שקיבלתי: " + 
                           agentOutputStr.substring(0, 500) + 
                           (agentOutputStr.length > 500 ? "..." : "");
          trace.addStep('התקבל פלט בפורמט לא מוכר');
        }
      }
      
      trace.complete('עיבוד התשובה הושלם בהצלחה', { responseLength: responseMessage?.length || 0 });
      return {
        message: responseMessage || "אין תשובה מהסוכן",
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      trace.error(`שגיאה בשליחת הודעה לסוכן: ${errorMessage}`, { 
        stack: error instanceof Error ? error.stack : undefined 
      });
      logger.error(`שגיאה בשליחת הודעה לסוכן: ${errorMessage}`, 'AgentService');
      
      trace.complete('הטיפול בשגיאה הושלם');
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
  private extractProductInfo(output: string): string | null {
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
  private isRunning(): boolean {
    return this.agentProcess !== null && this.status.isRunning;
  }
}

// יצירת מופע יחיד של השירות
export const agentService = new AgentService();
export default agentService; 