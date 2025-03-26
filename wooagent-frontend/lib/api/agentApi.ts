import { apiClient } from './apiClient';

export interface AgentStatus {
  isRunning: boolean;
  startTime?: string;
  uptime?: number; // בשניות
  modelName?: string;
  connectionStatus?: 'connected' | 'disconnected' | 'error';
}

// בשלב זה נשתמש במוק-אפ פשוט לתשובות מהשרת
export const agentApi = {
  getStatus: async (): Promise<AgentStatus> => {
    // כרגע נחזיר תשובות מדומות
    console.log('Getting agent status');
    
    // נבדוק אם יש מידע באחסון מקומי לגבי סטטוס הסוכן
    const savedStatus = localStorage.getItem('agentStatus');
    
    if (savedStatus) {
      return JSON.parse(savedStatus);
    }
    
    // ברירת מחדל - הסוכן פעיל
    const defaultStatus: AgentStatus = {
      isRunning: true,
      startTime: new Date().toISOString(),
      uptime: 3600, // שעה
      modelName: 'gpt-4o',
      connectionStatus: 'connected'
    };
    
    return defaultStatus;
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.get<AgentStatus>('/agent/status');
  },
  
  startAgent: async (): Promise<{ success: boolean }> => {
    // כרגע נחזיר תשובה מדומה של הצלחה
    console.log('Starting agent');
    
    const status: AgentStatus = {
      isRunning: true,
      startTime: new Date().toISOString(),
      uptime: 0,
      modelName: 'gpt-4o',
      connectionStatus: 'connected'
    };
    
    // שמירה באחסון מקומי
    localStorage.setItem('agentStatus', JSON.stringify(status));
    
    return { success: true };
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.post<{ success: boolean }>('/agent/start', {});
  },
  
  stopAgent: async (): Promise<{ success: boolean }> => {
    // כרגע נחזיר תשובה מדומה של הצלחה
    console.log('Stopping agent');
    
    const status: AgentStatus = {
      isRunning: false,
      connectionStatus: 'disconnected'
    };
    
    // שמירה באחסון מקומי
    localStorage.setItem('agentStatus', JSON.stringify(status));
    
    return { success: true };
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.post<{ success: boolean }>('/agent/stop', {});
  },
  
  restartAgent: async (): Promise<{ success: boolean }> => {
    // כרגע נחזיר תשובה מדומה של הצלחה
    console.log('Restarting agent');
    
    const status: AgentStatus = {
      isRunning: true,
      startTime: new Date().toISOString(),
      uptime: 0,
      modelName: 'gpt-4o',
      connectionStatus: 'connected'
    };
    
    // שמירה באחסון מקומי
    localStorage.setItem('agentStatus', JSON.stringify(status));
    
    return { success: true };
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.post<{ success: boolean }>('/agent/restart', {});
  }
}; 