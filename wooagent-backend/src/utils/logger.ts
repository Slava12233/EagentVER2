import winston from 'winston';
import { EventEmitter } from 'events';

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  agent: string;
  details?: any;
  traceId?: string;      
  parentId?: string;     
  stepType?: string;     
  duration?: number;     
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

// מקסימום אורך להודעת לוג במקרה של הודעה ארוכה
const MAX_LOG_MESSAGE_LENGTH = 1000;
// מקסימום אורך לפרטים של לוג
const MAX_LOG_DETAILS_LENGTH = 2000;

// רשימת שגיאות שיש לסנן או לקצר
const ERROR_PATTERNS_TO_CLEANUP = [
  // שגיאות Python נפוצות עם מידע מיותר
  { pattern: /Traceback \(most recent call last\)[\s\S]*?(?=Error:)/g, replacement: ''},
  { pattern: /File ".*?", line \d+, in .*?\n/g, replacement: ''},
  // קיצור של מסגרות מחסנית שאינן רלוונטיות
  { pattern: /(Stack trace:[\s\S]*?)(\n\s+at\s+.*?){10,}/g, replacement: '$1\n  ... (stack frames omitted)' },
  // הסרת מחרוזות JSON ארוכות
  { pattern: /({".*?){500,}/g, replacement: '{...}' }
];

// תיקון בעיות קידוד UTF-8
function fixUtf8Encoding(text: string): string {
  if (!text) return '';
  
  // החלפת סימנים לא תקינים בקידוד UTF-8
  return text
    .replace(/\uFFFD/g, '') // הסרת תווים לא חוקיים
    .replace(/\\u([0-9a-fA-F]{4})/g, (match, hex) => {
      // המרת קודי יוניקוד חזרה לתווים
      return String.fromCharCode(parseInt(hex, 16));
    })
    .replace(/\\n/g, '\n') // המרת מחרוזות קו חדש לקו חדש אמיתי
    .replace(/\\t/g, '\t'); // המרת מחרוזות טאב לטאב אמיתי
}

// ניקוי וקיצור הודעות שגיאה
function cleanupErrorMessage(message: string): string {
  if (!message) return '';
  
  let cleanedMessage = message;
  
  // הפעלת כל הדפוסים לניקוי
  ERROR_PATTERNS_TO_CLEANUP.forEach(({pattern, replacement}) => {
    cleanedMessage = cleanedMessage.replace(pattern, replacement);
  });
  
  // קיצור הודעות ארוכות
  if (cleanedMessage.length > MAX_LOG_MESSAGE_LENGTH) {
    cleanedMessage = cleanedMessage.substring(0, MAX_LOG_MESSAGE_LENGTH) + '... (truncated)';
  }
  
  return fixUtf8Encoding(cleanedMessage);
}

// ניקוי פרטים עודפים בלוג
function cleanupLogDetails(details: any): any {
  if (!details) return undefined;
  
  try {
    if (typeof details === 'string') {
      // תיקון קידוד וקיצור אם צריך
      const fixedDetails = fixUtf8Encoding(details);
      if (fixedDetails.length > MAX_LOG_DETAILS_LENGTH) {
        return fixedDetails.substring(0, MAX_LOG_DETAILS_LENGTH) + '... (truncated)';
      }
      return fixedDetails;
    } 
    
    if (typeof details === 'object') {
      // אם זה אובייקט שגיאה, ננקה את המידע
      if (details.stack) {
        return {
          message: details.message || 'Unknown error',
          stack: cleanupErrorMessage(details.stack)
        };
      }
      
      // המרה לJSON וחזרה כדי לוודא שאין מבנים מעגליים
      const detailsStr = JSON.stringify(details);
      if (detailsStr.length > MAX_LOG_DETAILS_LENGTH) {
        return JSON.parse(detailsStr.substring(0, MAX_LOG_DETAILS_LENGTH) + '..."} (truncated)');
      }
      return JSON.parse(detailsStr);
    }
    
    return details;
  } catch (error: any) {
    return `[Error processing details: ${error.message}]`;
  }
}

// אירועים לשליחת לוגים ועדכונים
export const logEvents = new EventEmitter();

// יומן winston
const logger = winston.createLogger({
  level: 'debug',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { agent: 'system' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error',
      format: winston.format.json()
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log',
      format: winston.format.json()
    })
  ]
});

// האזנה ללוגים פעילים
const logListeners: Function[] = [];
// האזנה לעדכוני trace
const traceListeners: Function[] = [];

// מאגר נתונים לשמירת traces
const activeTraces: { [key: string]: TraceGroup } = {};

// פונקציה ליצירת לוג בסיסי
export function createLogEntry(
  level: 'debug' | 'info' | 'warning' | 'error',
  message: string,
  agent: string = 'system',
  details?: any,
  traceId?: string,
  parentId?: string,
  stepType?: string,
  duration?: number
): LogEntry {
  // ניקוי ההודעה והפרטים
  const cleanedMessage = cleanupErrorMessage(message);
  const cleanedDetails = cleanupLogDetails(details);
  
  // יצירת רשומת לוג
  const logEntry: LogEntry = {
    id: Date.now().toString() + Math.random().toString(36).substring(2, 7),
    timestamp: new Date().toISOString(),
    level,
    message: cleanedMessage,
    agent,
    details: cleanedDetails
  };

  // הוספת פרטי מעקב אם סופקו
  if (traceId) logEntry.traceId = traceId;
  if (parentId) logEntry.parentId = parentId;
  if (stepType) logEntry.stepType = stepType;
  if (duration) logEntry.duration = duration;

  // רישום ללוג
  logger.log({
    level,
    message,
    agent,
    details: cleanedDetails,
    ...(traceId && { traceId }),
    ...(parentId && { parentId }),
    ...(stepType && { stepType }),
    ...(duration && { duration })
  });

  // שליחת הלוג למאזינים
  notifyLogListeners(logEntry);
  
  // אם יש traceId, מעדכנים גם את מאזיני ה-trace
  if (traceId) {
    const traceUpdate = {
      id: traceId,
      name: `Trace ${traceId.substring(0, 8)}`,
      step: logEntry
    };
    notifyTraceListeners(traceUpdate);
  }

  return logEntry;
}

// עדכון המאזינים ללוגים
function notifyLogListeners(logEntry: LogEntry) {
  logEvents.emit('log', logEntry);
  logListeners.forEach(listener => listener(logEntry));
}

// עדכון המאזינים ל-trace
function notifyTraceListeners(traceUpdate: any) {
  // עדכון המאגר של traces פעילים
  const { id, step } = traceUpdate;
  
  if (!activeTraces[id]) {
    // אם זה trace חדש, נוסיף אותו למאגר
    activeTraces[id] = {
      id,
      name: `Trace ${id.substring(0, 8)}`,
      startTime: new Date().toISOString(),
      status: 'running',
      steps: [step]
    };
  } else {
    // עדכון trace קיים
    activeTraces[id].steps.push(step);
    
    // אם זה צעד סיום או שגיאה, נעדכן את הסטטוס
    if (step.stepType === 'completion') {
      activeTraces[id].status = 'completed';
      activeTraces[id].endTime = new Date().toISOString();
    } else if (step.stepType === 'error') {
      activeTraces[id].status = 'error';
      activeTraces[id].endTime = new Date().toISOString();
    }
  }
  
  logEvents.emit('trace', activeTraces[id]);
  traceListeners.forEach(listener => listener(activeTraces[id]));
}

// הוספת מאזין ללוגים
export function addLogListener(listener: Function) {
  logListeners.push(listener);
  return () => {
    const index = logListeners.indexOf(listener);
    if (index > -1) {
      logListeners.splice(index, 1);
    }
  };
}

// הוספת מאזין ל-trace
export function addTraceListener(listener: Function) {
  traceListeners.push(listener);
  return () => {
    const index = traceListeners.indexOf(listener);
    if (index > -1) {
      traceListeners.splice(index, 1);
    }
  };
}

// המשתנה שמחזיק את ה-trace הפעיל הנוכחי
let activeTraceId: string | null = null;
let activeTraceParentId: string | null = null;

// פונקציה להגדרת ה-trace הפעיל
export function setActiveTrace(traceId: string | null, parentId: string | null = null) {
  activeTraceId = traceId;
  activeTraceParentId = parentId;
}

// פונקציות לוג בסיסיות
export function debug(message: string, agent: string = 'system', details?: any) {
  return createLogEntry('debug', message, agent, details);
}

export function info(message: string, agent: string = 'system', details?: any) {
  return createLogEntry('info', message, agent, details);
}

export function warn(message: string, agent: string = 'system', details?: any) {
  return createLogEntry('warning', message, agent, details);
}

// המשך פונקציות יצירת הלוגים מוצג בהמשך הקובץ
// ... existing code ...

// פונקציות תיעוד של trace
export function addThought(message: string, agent: string = 'system', details?: any, traceId: string | null = activeTraceId, parentId: string | null = activeTraceParentId) {
  return createLogEntry(
    'info',
    message,
    agent,
    details,
    traceId || undefined,
    parentId || undefined,
    'thought'
  );
}

export function addToolCall(toolName: string, params: any, agent: string = 'system', traceId: string | null = activeTraceId, parentId: string | null = activeTraceParentId) {
  const message = `Calling tool: ${toolName}`;
  return createLogEntry(
    'info',
    message,
    agent,
    params,
    traceId || undefined,
    parentId || undefined,
    'tool_call'
  );
}

export function addToolResult(toolName: string, result: any, agent: string = 'system', traceId: string | null = activeTraceId, parentId: string | null = activeTraceParentId, duration?: number) {
  const message = `Tool result: ${toolName}`;
  return createLogEntry(
    'info',
    message,
    agent,
    result,
    traceId || undefined,
    parentId || undefined,
    'tool_result',
    duration
  );
}

export function addMessage(role: 'system' | 'user' | 'assistant', content: string, agent: string = 'system', traceId: string | null = activeTraceId, parentId: string | null = activeTraceParentId) {
  const message = `${role}: ${content.substring(0, 100)}${content.length > 100 ? '...' : ''}`;
  return createLogEntry(
    'info',
    message,
    agent,
    { role, content },
    traceId || undefined,
    parentId || undefined,
    'message'
  );
}

export function complete(message: string, details?: any, agent: string = 'system', traceId: string | null = activeTraceId, parentId: string | null = activeTraceParentId, status: 'completed' | 'error' = 'completed') {
  if (traceId === activeTraceId) {
    setActiveTrace(null);
  }
  
  return createLogEntry(
    status === 'error' ? 'error' : 'info',
    message,
    agent,
    details,
    traceId || undefined,
    parentId || undefined,
    'completion'
  );
}

export function error(message: string, details?: any, agent: string = 'system', traceId: string | null = activeTraceId, parentId: string | null = activeTraceParentId) {
  // כאשר מתרחשת שגיאה, נסמן את ה-trace הפעיל כשגיאה אם קיים
  const logEntry = createLogEntry(
    'error',
    message,
    agent,
    details,
    traceId || undefined,
    parentId || undefined,
    'error'
  );
  
  // אם יש trace פעיל, נסיים אותו עם סטטוס שגיאה
  if (traceId && traceId === activeTraceId) {
    complete(`Error occurred: ${message.substring(0, 100)}`, details, agent, traceId, parentId, 'error');
  }
  
  return logEntry;
}

// פונקציה ליצירת trace שלם
export function createTrace(name: string, agent: string = 'system') {
  const traceId = Date.now().toString() + Math.random().toString(36).substring(2, 7);
  setActiveTrace(traceId);
  
  // לוג התחלת תהליך
  createLogEntry(
    'info',
    `Starting process: ${name}`,
    agent,
    { name },
    traceId,
    undefined,
    'start'
  );
  
  // אובייקט שמחזיר את כל הפונקציות עם ה-trace ID מוגדר מראש
  return {
    traceId,
    
    // העתקת כל פונקציות התיעוד עם traceId קבוע
    addStep: (message: string, details?: any) => 
      createLogEntry('info', message, agent, details, traceId, undefined, 'step'),
      
    addThought: (message: string, details?: any) =>
      addThought(message, agent, details, traceId, undefined),
      
    addToolCall: (toolName: string, params: any) =>
      addToolCall(toolName, params, agent, traceId, undefined),
      
    addToolResult: (toolName: string, result: any, duration?: number) =>
      addToolResult(toolName, result, agent, traceId, undefined, duration),
      
    addMessage: (role: 'system' | 'user' | 'assistant', content: string) =>
      addMessage(role, content, agent, traceId, undefined),
      
    complete: (message: string, details?: any) => {
      setActiveTrace(null); // ניקוי הטרייס הפעיל
      return complete(message, details, agent, traceId, undefined, 'completed');
    },
    
    error: (message: string, details?: any) => {
      setActiveTrace(null); // ניקוי הטרייס הפעיל
      return error(message, details, agent, traceId, undefined);
    }
  };
}

// פונקציה לתחילת מעקב חדש - אליאס ל-createTrace לתאימות לאחור
export function startTrace(name: string, agent: string = 'system') {
  return createTrace(name, agent);
}

// פונקציה להחזרת כל ה-traces הפעילים
export function getActiveTraces(): TraceGroup[] {
  return Object.values(activeTraces);
}

// פונקציה להחזרת trace לפי מזהה
export function getTraceById(traceId: string): TraceGroup | undefined {
  return activeTraces[traceId];
}

export default {
  debug,
  info,
  warn,
  error,
  addLogListener,
  addTraceListener,
  setActiveTrace,
  addThought,
  addToolCall,
  addToolResult,
  addMessage,
  complete,
  createTrace,
  startTrace,
  getActiveTraces,
  getTraceById
}; 