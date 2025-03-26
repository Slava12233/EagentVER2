import { apiClient } from './apiClient';

export interface StoreConnectionConfig {
  name: string;
  url: string;
  consumerKey: string;
  consumerSecret: string;
  apiVersion: string;
  description?: string;
}

export interface ConnectionTestResult {
  success: boolean;
  products?: number;
  orders?: number;
  error?: string;
}

// בשלב זה נשתמש במוק-אפ פשוט לתשובות מהשרת
export const storeApi = {
  testConnection: async (config: StoreConnectionConfig): Promise<ConnectionTestResult> => {
    // כרגע נחזיר תשובות מדומות
    console.log('Testing connection with config:', config);
    
    // בדיקה פשוטה שה-URL מתחיל ב-http
    if (!config.url.startsWith('http')) {
      return {
        success: false,
        error: 'כתובת URL לא תקינה',
      };
    }
    
    // סימולציה של בדיקת חיבור מוצלחת
    return {
      success: true,
      products: 150,
      orders: 27,
    };
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.post<ConnectionTestResult>('/store/test-connection', config);
  },
  
  saveStoreSettings: async (config: StoreConnectionConfig): Promise<{ success: boolean }> => {
    // כרגע נחזיר תשובה מדומה של הצלחה
    console.log('Saving store settings:', config);
    
    // סימולציה של שמירת הגדרות מוצלחת
    localStorage.setItem('storeSettings', JSON.stringify(config));
    
    return { success: true };
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.post<{ success: boolean }>('/store/settings', config);
  },
  
  getStoreSettings: async (): Promise<StoreConnectionConfig | null> => {
    // ננסה לקבל הגדרות מאחסון מקומי אם קיימות
    const settings = localStorage.getItem('storeSettings');
    
    if (settings) {
      return JSON.parse(settings);
    }
    
    return null;
    
    // בעתיד, כאשר השרת מוכן:
    // return apiClient.get<StoreConnectionConfig>('/store/settings');
  }
}; 