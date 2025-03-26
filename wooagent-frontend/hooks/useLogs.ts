import { useState, useEffect } from 'react';
import { LogEntry, socketClient } from '@/lib/api/socketClient';

export function useLogs(initialAutoConnect = true) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [filter, setFilter] = useState<{ 
    level: 'all' | 'debug' | 'info' | 'warning' | 'error', 
    agent: string | 'all' 
  }>({
    level: 'all',
    agent: 'all'
  });
  
  // התחברות לשרת
  useEffect(() => {
    if (initialAutoConnect) {
      connect();
    }
    
    // התחברות לאירועי לוגים וסטטוס החיבור
    const logUnsubscribe = socketClient.onLog((log) => {
      setLogs(prev => [log, ...prev].slice(0, 500)); // שמירת 500 הלוגים האחרונים
    });
    
    // האזנה להיסטוריית לוגים
    const logHistoryUnsubscribe = socketClient.onLogHistory((historyLogs) => {
      console.log(`התקבלו ${historyLogs.length} לוגים מההיסטוריה`);
      // מיזוג הלוגים הקיימים עם ההיסטוריה החדשה
      // הסרת כפילויות לפי id
      setLogs(prev => {
        const existingIds = new Set(prev.map(log => log.id));
        const newLogs = historyLogs.filter(log => !existingIds.has(log.id));
        
        // מיון לפי זמן יצירה (חדש לישן)
        return [...newLogs, ...prev]
          .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
          .slice(0, 500);
      });
    });
    
    const connUnsubscribe = socketClient.onConnectionChange((connected) => {
      setIsConnected(connected);
    });
    
    // ניקוי בעת ניתוק
    return () => {
      logUnsubscribe();
      logHistoryUnsubscribe();
      connUnsubscribe();
      disconnect();
    };
  }, [initialAutoConnect]);
  
  // פונקציה לחיבור
  const connect = () => {
    socketClient.connect();
  };
  
  // פונקציה לניתוק
  const disconnect = () => {
    socketClient.disconnect();
  };
  
  // ניקוי לוגים
  const clearLogs = () => {
    setLogs([]);
  };
  
  // בקשת לוגים מהשרת
  const refreshLogs = (limit = 100) => {
    if (isConnected) {
      socketClient.requestLogHistory(limit);
    }
  };
  
  // פילטור לוגים
  const filteredLogs = logs.filter(log => {
    if (filter.level !== 'all' && log.level !== filter.level) return false;
    if (filter.agent !== 'all' && log.agent !== filter.agent) return false;
    return true;
  });
  
  return {
    logs: filteredLogs,
    allLogs: logs,
    isConnected,
    autoScroll,
    filter,
    setAutoScroll,
    setFilter,
    connect,
    disconnect,
    clearLogs,
    refreshLogs
  };
} 