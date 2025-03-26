import { Server, Socket } from 'socket.io';
import { Server as HttpServer } from 'http';
import logger, { addLogListener, addTraceListener, TraceGroup } from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';
import { logService } from './logService';

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  message: string;
  agent: string;
  details?: any;
  traceId?: string;
  parentId?: string;
  stepType?: string;
  duration?: number;
}

class SocketService {
  private io: Server | null = null;
  private activeSockets: Set<string> = new Set();

  public initialize(server: HttpServer): void {
    this.io = new Server(server, {
      cors: {
        origin: process.env.CLIENT_URL || "http://localhost:3000",
        methods: ["GET", "POST"],
        credentials: true
      }
    });

    this.io.on('connection', async (socket: Socket) => {
      const socketId = socket.id;
      this.activeSockets.add(socketId);
      logger.info(`Socket connected: ${socketId}`, 'SocketService');
      
      // כאשר לקוח מתחבר, שלח אליו את כל הלוגים הקיימים
      socket.emit('connection_status', { isConnected: true });
      
      // שליחת היסטוריית לוגים אחרונים
      try {
        const recentLogs = await logService.getLogs({ limit: 100 });
        if (recentLogs && recentLogs.length > 0) {
          logger.info(`שולח ${recentLogs.length} לוגים אחרונים ללקוח חדש`, 'SocketService');
          socket.emit('log_history', recentLogs);
        }
      } catch (error) {
        logger.error(`שגיאה בשליחת היסטוריית לוגים: ${error}`, 'SocketService');
      }
      
      // שליחת Traces פעילים
      try {
        const activeTraces = logger.getActiveTraces();
        if (activeTraces.length > 0) {
          logger.info(`שולח ${activeTraces.length} traces פעילים ללקוח חדש`, 'SocketService');
          activeTraces.forEach((trace: TraceGroup) => {
            socket.emit('trace', trace);
          });
        }
      } catch (error) {
        logger.error(`שגיאה בשליחת traces פעילים: ${error}`, 'SocketService');
      }
      
      // מאזין לבקשות התנתקות
      socket.on('disconnect', () => {
        this.activeSockets.delete(socketId);
        logger.info(`Socket disconnected: ${socketId}`, 'SocketService');
      });
      
      // מאזין לבקשות לוגים
      socket.on('get_logs', async (data: { limit?: number }) => {
        try {
          const recentLogs = await logService.getLogs({ 
            limit: data.limit || 100 
          });
          socket.emit('log_history', recentLogs);
        } catch (error) {
          logger.error(`שגיאה בשליחת היסטוריית לוגים: ${error}`, 'SocketService');
        }
      });
      
      // מאזין לבקשות traces
      socket.on('get_traces', async (data: { limit?: number }) => {
        try {
          const activeTraces = logger.getActiveTraces();
          socket.emit('trace_history', activeTraces);
        } catch (error) {
          logger.error(`שגיאה בשליחת היסטוריית traces: ${error}`, 'SocketService');
        }
      });
      
      // מאזין לבקשות פרטי trace לפי מזהה
      socket.on('get_trace', async (data: { traceId: string }) => {
        try {
          const trace = logger.getTraceById(data.traceId);
          if (trace) {
            socket.emit('trace', trace);
          } else {
            socket.emit('error', { message: `Trace with ID ${data.traceId} not found` });
          }
        } catch (error) {
          logger.error(`שגיאה בשליחת פרטי trace: ${error}`, 'SocketService');
        }
      });
      
      // מאזין לבקשות צ'אט
      socket.on('chat_message', (data) => {
        // כאן נעביר את ההודעה למודול הטיפול בצ'אט
        logger.info(`Received chat message: ${JSON.stringify(data)}`, 'SocketService');
      });
    });
    
    // התחברות למערכת הלוגים להעברת עדכונים בזמן אמת
    addLogListener((logEntry: LogEntry) => {
      if (this.io) {
        this.io.emit('log', logEntry);
      }
    });
    
    // התחברות למערכת ה-traces להעברת עדכונים בזמן אמת
    addTraceListener((trace: TraceGroup) => {
      if (this.io) {
        this.io.emit('trace', trace);
      }
    });
    
    logger.info('Socket.IO service initialized', 'SocketService');
  }
  
  public sendLogUpdate(logEntry: LogEntry): void {
    if (!this.io) {
      logger.warn('Attempted to send log update before Socket.IO initialization', 'SocketService');
      return;
    }
    
    this.io.emit('log', logEntry);
  }
  
  public sendTraceUpdate(trace: TraceGroup): void {
    if (!this.io) {
      logger.warn('Attempted to send trace update before Socket.IO initialization', 'SocketService');
      return;
    }
    
    this.io.emit('trace', trace);
  }
  
  public sendChatResponse(userId: string, response: any): void {
    if (!this.io) {
      logger.warn('Attempted to send chat response before Socket.IO initialization', 'SocketService');
      return;
    }
    
    this.io.emit('chat_response', { userId, ...response });
  }
  
  public broadcastAgentStatus(status: any): void {
    if (!this.io) {
      logger.warn('Attempted to broadcast agent status before Socket.IO initialization', 'SocketService');
      return;
    }
    
    this.io.emit('agent_status', status);
  }
  
  public getActiveConnections(): number {
    return this.activeSockets.size;
  }
}

// יצירת מופע יחיד של השירות
export const socketService = new SocketService();
export default socketService; 