import { apiClient } from './apiClient';
import { v4 as uuidv4 } from 'uuid';

export interface ChatMessage {
  id: string;
  content: string;
  role: "user" | "agent";
  timestamp: string;
}

export interface ChatResponse {
  message: string;
  timestamp: string;
}

export const chatApi = {
  // שליחת הודעה לסוכן
  sendMessage: async (content: string): Promise<ChatResponse> => {
    console.log('Sending chat message to API:', content);
    
    try {
      // שליחת הבקשה לשרת האמיתי בנתיב הנכון
      const response = await apiClient.post<any>('/chat/message', { message: content });
      
      console.log('API response received:', response);
      
      // בדיקה אם התשובה היא במבנה הנכון או צריכה עיבוד
      if (typeof response === 'object') {
        if (response.message !== undefined) {
          // פורמט תקין
          return {
            message: response.message,
            timestamp: response.timestamp || new Date().toISOString()
          };
        } else if (typeof response.response === 'string') {
          // תבנית שונה שמגיעה לפעמים
          return {
            message: response.response,
            timestamp: new Date().toISOString()
          };
        } else if (typeof response === 'string') {
          // לפעמים מגיעה מחרוזת
          return {
            message: response,
            timestamp: new Date().toISOString()
          };
        }
      }
      
      // אם אי אפשר לפענח את התשובה, נחזיר את המבנה המלא כמחרוזת
      console.warn('Unknown response format:', response);
      return {
        message: typeof response === 'object' ? 
          JSON.stringify(response) : 
          String(response || 'לא התקבלה תשובה מהשרת'),
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error sending message to server:', error);
      throw error;
    }
  },
  
  // קבלת היסטוריית שיחה
  getHistory: async (): Promise<ChatMessage[]> => {
    console.log('Getting chat history');
    
    // בדיקה אם יש היסטוריה שמורה מקומית
    const savedHistory = localStorage.getItem('chatHistory');
    
    if (savedHistory) {
      return JSON.parse(savedHistory);
    }
    
    // אם אין היסטוריה, מחזירים מערך ריק
    return [];
    
    // בעתיד, כאשר השרת תומך בהיסטוריה:
    // return apiClient.get<ChatMessage[]>('/chat/history');
  },
  
  // שמירת שיחה מקומית (עד שיהיה אחסון בשרת)
  saveHistory: (messages: ChatMessage[]): void => {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  },
  
  // ניקוי היסטוריית שיחה
  clearHistory: async (): Promise<{ success: boolean }> => {
    // כרגע רק ננקה את האחסון המקומי
    console.log('Clearing chat history');
    localStorage.removeItem('chatHistory');
    
    return { success: true };
    
    // בעתיד, כאשר השרת תומך בניקוי היסטוריה:
    // return apiClient.delete<{ success: boolean }>('/chat/history');
  }
}; 