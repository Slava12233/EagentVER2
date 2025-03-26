import express, { Request, Response } from 'express';
import logger from '../utils/logger';
import { storeService } from '../services/storeService';
import { agentService } from '../services/agentService';
import { logService } from '../services/logService';
import { StoreConnectionConfig } from '../models/interfaces';
import { v4 as uuidv4 } from 'uuid';

const router = express.Router();

/**
 * נתיבים לעבודה עם החנות
 */
// קבלת הגדרות חיבור לחנות
router.get('/store/config', (req: Request, res: Response) => {
  try {
    const config = storeService.getConfig();
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
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בקבלת הגדרות חיבור: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ success: false, message: 'שגיאה בקבלת הגדרות החיבור' });
  }
});

// שמירת הגדרות חיבור לחנות
router.post('/store/config', (req: Request, res: Response) => {
  try {
    const config: StoreConnectionConfig = req.body;
    
    // בדיקות תקינות בסיסיות
    if (!config.url || !config.consumerKey || !config.consumerSecret) {
      return res.status(400).json({ 
        success: false, 
        message: 'חסרים שדות חובה בהגדרות החיבור' 
      });
    }
    
    // שמירת ההגדרות
    const result = storeService.saveConnectionConfig(config);
    
    if (result.success) {
      res.json({ success: true, message: 'הגדרות החיבור נשמרו בהצלחה' });
    } else {
      res.status(500).json({ 
        success: false, 
        message: `שגיאה בשמירת הגדרות החיבור: ${result.error}` 
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בשמירת הגדרות חיבור: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ success: false, message: 'שגיאה בשמירת הגדרות החיבור' });
  }
});

// בדיקת חיבור לחנות
router.post('/store/test-connection', async (req: Request, res: Response) => {
  try {
    // אם יש נתוני חיבור בבקשה, נשתמש בהם. אחרת נשתמש בהגדרות השמורות
    const config: StoreConnectionConfig | undefined = req.body.config;
    
    const result = await storeService.testConnection(config);
    res.json(result);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בבדיקת חיבור לחנות: ${errorMessage}`, { agent: 'API' });
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
router.get('/agent/status', (req: Request, res: Response) => {
  try {
    const status = agentService.getStatus();
    res.json({ success: true, status });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בקבלת סטטוס האיג'נט: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ 
      success: false, 
      message: 'שגיאה בקבלת סטטוס האיג\'נט' 
    });
  }
});

// הפעלת האיג'נט
router.post('/agent/start', async (req: Request, res: Response) => {
  try {
    const result = await agentService.startAgent();
    if (result.success) {
      res.json({ 
        success: true, 
        message: 'האיג\'נט הופעל בהצלחה',
        status: agentService.getStatus()
      });
    } else {
      res.status(500).json({ 
        success: false, 
        message: `שגיאה בהפעלת האיג'נט: ${result.error}`,
        status: agentService.getStatus()
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בהפעלת האיג'נט: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ 
      success: false, 
      message: 'שגיאה בהפעלת האיג\'נט', 
      status: agentService.getStatus()
    });
  }
});

// עצירת האיג'נט
router.post('/agent/stop', async (req: Request, res: Response) => {
  try {
    const result = await agentService.stopAgent();
    if (result.success) {
      res.json({ 
        success: true, 
        message: 'האיג\'נט נעצר בהצלחה',
        status: agentService.getStatus()
      });
    } else {
      res.status(500).json({ 
        success: false, 
        message: `שגיאה בעצירת האיג'נט: ${result.error}`,
        status: agentService.getStatus()
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בעצירת האיג'נט: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ 
      success: false, 
      message: 'שגיאה בעצירת האיג\'נט',
      status: agentService.getStatus() 
    });
  }
});

// הפעלה מחדש של האיג'נט
router.post('/agent/restart', async (req: Request, res: Response) => {
  try {
    const result = await agentService.restartAgent();
    if (result.success) {
      res.json({ 
        success: true, 
        message: 'האיג\'נט הופעל מחדש בהצלחה',
        status: agentService.getStatus()
      });
    } else {
      res.status(500).json({ 
        success: false, 
        message: `שגיאה בהפעלה מחדש של האיג'נט: ${result.error}`,
        status: agentService.getStatus()
      });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בהפעלה מחדש של האיג'נט: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ 
      success: false, 
      message: 'שגיאה בהפעלה מחדש של האיג\'נט',
      status: agentService.getStatus()
    });
  }
});

// שליחת הודעה לאיג'נט
router.post('/chat/message', async (req: Request, res: Response) => {
  try {
    const { message } = req.body;
    
    if (!message || typeof message !== 'string' || message.trim() === '') {
      return res.status(400).json({ 
        success: false, 
        message: 'הודעה ריקה או לא תקינה' 
      });
    }
    
    const messageId = uuidv4();
    logger.info(`התקבלה הודעת צ'אט חדשה: ${message.substring(0, 50)}${message.length > 50 ? '...' : ''}`, { 
      agent: 'ChatAPI',
      messageId 
    });
    
    const response = await agentService.sendMessage(message);
    res.json({ success: true, response });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בשליחת הודעה לאיג'נט: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ 
      success: false, 
      message: 'שגיאה בשליחת ההודעה לאיג\'נט' 
    });
  }
});

// קבלת היסטוריית לוגים
router.get('/logs', async (req: Request, res: Response) => {
  try {
    const { limit, level, agent, search, errorOnly } = req.query;
    
    // קריאה והחזרת הלוגים
    const logs = await logService.getLogs({
      limit: limit ? Number(limit) : undefined,
      level: level as string | undefined,
      agent: agent as string | undefined,
      search: search as string | undefined,
      errorOnly: errorOnly === 'true'
    });
    
    res.json({ 
      success: true, 
      logs,
      total: logs.length
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.error(`שגיאה בקבלת לוגים: ${errorMessage}`, { agent: 'API' });
    res.status(500).json({ success: false, message: 'שגיאה בקבלת לוגים' });
  }
});

export default router; 