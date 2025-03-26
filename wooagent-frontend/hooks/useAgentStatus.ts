import { useState, useEffect } from 'react';
import { AgentStatus, agentApi } from '@/lib/api/agentApi';

export function useAgentStatus() {
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // טעינת סטטוס בעת טעינת הדף
  useEffect(() => {
    loadStatus();
    
    // עדכון הסטטוס כל 30 שניות
    const interval = setInterval(() => {
      loadStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  async function loadStatus() {
    try {
      setIsLoading(true);
      setError(null);
      const data = await agentApi.getStatus();
      setStatus(data);
    } catch (err) {
      console.error('Failed to load agent status:', err);
      setError('שגיאה בטעינת סטטוס הסוכן');
    } finally {
      setIsLoading(false);
    }
  }
  
  // הפעלת הסוכן
  const startAgent = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await agentApi.startAgent();
      
      if (result.success) {
        await loadStatus();
        return { success: true };
      } else {
        throw new Error('שגיאה בהפעלת הסוכן');
      }
    } catch (err) {
      console.error('Failed to start agent:', err);
      setError('שגיאה בהפעלת הסוכן');
      return { success: false, error: err instanceof Error ? err.message : 'שגיאה לא ידועה' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // הפסקת הסוכן
  const stopAgent = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await agentApi.stopAgent();
      
      if (result.success) {
        await loadStatus();
        return { success: true };
      } else {
        throw new Error('שגיאה בהפסקת הסוכן');
      }
    } catch (err) {
      console.error('Failed to stop agent:', err);
      setError('שגיאה בהפסקת הסוכן');
      return { success: false, error: err instanceof Error ? err.message : 'שגיאה לא ידועה' };
    } finally {
      setIsLoading(false);
    }
  };
  
  // הפעלה מחדש של הסוכן
  const restartAgent = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await agentApi.restartAgent();
      
      if (result.success) {
        await loadStatus();
        return { success: true };
      } else {
        throw new Error('שגיאה בהפעלה מחדש של הסוכן');
      }
    } catch (err) {
      console.error('Failed to restart agent:', err);
      setError('שגיאה בהפעלה מחדש של הסוכן');
      return { success: false, error: err instanceof Error ? err.message : 'שגיאה לא ידועה' };
    } finally {
      setIsLoading(false);
    }
  };
  
  return {
    status,
    isLoading,
    error,
    startAgent,
    stopAgent,
    restartAgent,
    refreshStatus: loadStatus
  };
} 