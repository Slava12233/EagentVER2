import { useState, useEffect } from 'react';
import { StoreConnectionConfig, storeApi } from '@/lib/api/storeApi';

export function useStoreSettings() {
  const [settings, setSettings] = useState<StoreConnectionConfig | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // טעינת הגדרות בעת טעינת הדף
  useEffect(() => {
    async function loadSettings() {
      try {
        setIsLoading(true);
        setError(null);
        const data = await storeApi.getStoreSettings();
        setSettings(data);
      } catch (err) {
        console.error('Failed to load store settings:', err);
        setError('שגיאה בטעינת הגדרות החנות');
      } finally {
        setIsLoading(false);
      }
    }
    
    loadSettings();
  }, []);
  
  // שמירת הגדרות
  const saveSettings = async (newSettings: StoreConnectionConfig) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await storeApi.saveStoreSettings(newSettings);
      
      if (result.success) {
        setSettings(newSettings);
        return { success: true };
      } else {
        throw new Error('שגיאה בשמירת ההגדרות');
      }
    } catch (err) {
      console.error('Failed to save store settings:', err);
      setError('שגיאה בשמירת הגדרות החנות');
      return { success: false, error: err instanceof Error ? err.message : 'שגיאה לא ידועה' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // בדיקת חיבור
  const testConnection = async (config: StoreConnectionConfig) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await storeApi.testConnection(config);
      return result;
    } catch (err) {
      console.error('Failed to test connection:', err);
      setError('שגיאה בבדיקת החיבור');
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'שגיאה לא ידועה' 
      };
    } finally {
      setIsLoading(false);
    }
  };
  
  return {
    settings,
    isLoading,
    error,
    saveSettings,
    testConnection
  };
} 