/**
 * ממשקים לשימוש ברחבי האפליקציה
 */

/**
 * מבנה של רשומת לוג
 */
export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  agent: string;
  details?: any;
}

/**
 * מצב הסוכן
 */
export interface AgentStatus {
  isRunning: boolean;
  startTime?: string;
  uptime?: number; // בשניות
  modelName?: string;
  connectionStatus?: 'connected' | 'disconnected' | 'error';
}

/**
 * תצורת חיבור לחנות WooCommerce
 */
export interface StoreConnectionConfig {
  name: string;
  url: string;
  consumerKey: string;
  consumerSecret: string;
  apiVersion: string;
  description?: string;
}

/**
 * תוצאת בדיקת חיבור לחנות
 */
export interface ConnectionTestResult {
  success: boolean;
  error?: string;
  products?: number;
  orders?: number;
}

/**
 * הודעת צ'אט
 */
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'agent';
  timestamp: string;
}

/**
 * תגובת צ'אט
 */
export interface ChatResponse {
  message: string;
  timestamp: string;
} 