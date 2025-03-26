import { io, Socket } from 'socket.io-client';

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  agent: string;
  details?: any;
  traceId?: string;       // מזהה ייחודי של רצף פעולות (trace)
  parentId?: string;      // מזהה האב (אם זה צעד בתוך רצף)
  stepType?: string;      // סוג הצעד: 'tool_call', 'tool_result', 'thought', 'message', וכו'
  duration?: number;      // משך הצעד במילישניות
}

// עדכון המבנה לתמיכה בקבוצות של צעדים בתוך trace
export interface TraceGroup {
  id: string;
  name: string;
  startTime: string;
  endTime?: string;
  status: 'running' | 'completed' | 'error';
  steps: LogEntry[];
}

type LogCallback = (log: LogEntry) => void;
type LogHistoryCallback = (logs: LogEntry[]) => void;
type ConnectionCallback = (isConnected: boolean) => void;
type TraceCallback = (trace: TraceGroup) => void;

// מוק דאטה של לוגים לשימוש בסימולציה
const MOCK_LOGS: LogEntry[] = [
  { 
    id: "1", 
    timestamp: new Date().toISOString(), 
    level: "info", 
    message: "מערכת הופעלה", 
    agent: "MainAgent" 
  },
  { 
    id: "2", 
    timestamp: new Date().toISOString(), 
    level: "info", 
    message: "חיבור לחנות הצליח", 
    agent: "StoreAgent" 
  },
  { 
    id: "3", 
    timestamp: new Date().toISOString(), 
    level: "debug", 
    message: "טעינת מוצרים מהמערכת", 
    agent: "ProductAgent" 
  },
  { 
    id: "4", 
    timestamp: new Date().toISOString(), 
    level: "warning", 
    message: "מספר בקשות API גבוה", 
    agent: "MainAgent" 
  },
  { 
    id: "5", 
    timestamp: new Date().toISOString(), 
    level: "error", 
    message: "נכשל בטעינת פרטי לקוח", 
    agent: "CustomerAgent" 
  }
];

class SocketClient {
  private connected: boolean = false;
  private logListeners: LogCallback[] = [];
  private logHistoryListeners: LogHistoryCallback[] = [];
  private connectionListeners: ConnectionCallback[] = [];
  private traceListeners: TraceCallback[] = [];
  private socket: Socket | null = null;
  private traces: Map<string, TraceGroup> = new Map(); // אחסון traces
  
  connect() {
    if (this.connected) return;
    
    console.log('Connecting to WebSocket server');
    
    const serverUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
    this.socket = io(serverUrl, {
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });
    
    this.socket.on('connect', () => {
      console.log('Connected to WebSocket server');
      this.connected = true;
      this.notifyConnectionListeners(true);
      
      // בקשת היסטוריית לוגים מיד בהתחברות
      this.requestLogHistory();
    });
    
    this.socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
      this.connected = false;
      this.notifyConnectionListeners(false);
    });
    
    this.socket.on('log', (logEntry: LogEntry) => {
      console.log('Received log:', logEntry);
      this.notifyLogListeners(logEntry);

      // אם זהו לוג עם traceId, נוסיף אותו לקבוצת ה-trace המתאימה
      if (logEntry.traceId) {
        this.processTraceLog(logEntry);
      }
    });
    
    this.socket.on('log_history', (logs: LogEntry[]) => {
      console.log(`Received log history: ${logs.length} logs`);
      this.notifyLogHistoryListeners(logs);
      
      // מיון לוגים לפי traces
      this.organizeLodsByTraces(logs);
    });
    
    this.socket.on('trace', (trace: TraceGroup) => {
      console.log('Received trace update:', trace);
      this.traces.set(trace.id, trace);
      this.notifyTraceListeners(trace);
    });
    
    this.socket.on('agentStatus', (status: any) => {
      console.log('Agent status update:', status);
    });
    
    this.socket.on('connect_error', (error: Error) => {
      console.error('Socket connection error:', error);
    });
  }
  
  disconnect() {
    if (!this.connected || !this.socket) return;
    
    this.socket.disconnect();
    this.socket = null;
    this.connected = false;
    this.notifyConnectionListeners(false);
    console.log('Disconnected from WebSocket server');
  }
  
  requestLogHistory(limit: number = 100) {
    if (!this.connected || !this.socket) {
      console.error('Cannot request log history: not connected');
      return;
    }
    
    console.log(`Requesting log history (limit: ${limit})`);
    this.socket.emit('get_logs', { limit });
  }
  
  onLog(callback: LogCallback) {
    this.logListeners.push(callback);
    return () => {
      this.logListeners = this.logListeners.filter(cb => cb !== callback);
    };
  }
  
  onLogHistory(callback: LogHistoryCallback) {
    this.logHistoryListeners.push(callback);
    return () => {
      this.logHistoryListeners = this.logHistoryListeners.filter(cb => cb !== callback);
    };
  }
  
  onConnectionChange(callback: ConnectionCallback) {
    this.connectionListeners.push(callback);
    // מיידית עדכון על מצב הנוכחי
    callback(this.connected);
    return () => {
      this.connectionListeners = this.connectionListeners.filter(cb => cb !== callback);
    };
  }
  
  private notifyLogListeners(log: LogEntry) {
    this.logListeners.forEach(callback => callback(log));
  }
  
  private notifyLogHistoryListeners(logs: LogEntry[]) {
    this.logHistoryListeners.forEach(callback => callback(logs));
  }
  
  private notifyConnectionListeners(isConnected: boolean) {
    this.connectionListeners.forEach(callback => callback(isConnected));
  }
  
  isConnected() {
    return this.connected;
  }
  
  private processTraceLog(log: LogEntry) {
    if (!log.traceId) return;
    
    let trace = this.traces.get(log.traceId);
    
    // יצירת trace חדש אם לא קיים
    if (!trace) {
      trace = {
        id: log.traceId,
        name: `Trace ${log.traceId.substring(0, 8)}`,
        startTime: log.timestamp,
        status: 'running',
        steps: []
      };
      this.traces.set(log.traceId, trace);
    }
    
    // הוספת הלוג לצעדים של ה-trace
    trace.steps.push(log);
    
    // עדכון זמן סיום אם יש תיעוד משך
    if (log.duration) {
      const endTime = new Date(new Date(log.timestamp).getTime() + log.duration);
      trace.endTime = endTime.toISOString();
    }
    
    // עדכון סטטוס ה-trace אם זהו צעד שמסמן סיום
    if (log.stepType === 'completion' || log.message.includes('completed')) {
      trace.status = 'completed';
    } else if (log.level === 'error' && log.stepType === 'error') {
      trace.status = 'error';
    }
    
    this.notifyTraceListeners(trace);
  }
  
  private organizeLodsByTraces(logs: LogEntry[]) {
    // איפוס ה-traces הקיימים
    this.traces.clear();
    
    // מיון הלוגים לפי traceId
    for (const log of logs) {
      if (log.traceId) {
        this.processTraceLog(log);
      }
    }
  }
  
  onTrace(callback: TraceCallback) {
    this.traceListeners.push(callback);
    // שליחת כל ה-traces הקיימים לאחר ההרשמה
    for (const trace of this.traces.values()) {
      callback(trace);
    }
    return () => {
      this.traceListeners = this.traceListeners.filter(cb => cb !== callback);
    };
  }
  
  private notifyTraceListeners(trace: TraceGroup) {
    this.traceListeners.forEach(callback => callback(trace));
  }
  
  // קבלת כל ה-traces הקיימים
  getAllTraces(): TraceGroup[] {
    return Array.from(this.traces.values());
  }
  
  // קבלת trace ספציפי לפי מזהה
  getTraceById(traceId: string): TraceGroup | undefined {
    return this.traces.get(traceId);
  }
}

export const socketClient = new SocketClient(); 