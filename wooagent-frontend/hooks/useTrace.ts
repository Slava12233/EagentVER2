import { useState, useEffect } from 'react';
import { socketClient, TraceGroup } from '@/lib/api/socketClient';

export function useTrace(initialAutoConnect = true) {
  const [traces, setTraces] = useState<TraceGroup[]>([]);
  const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [filterStatus, setFilterStatus] = useState<'all' | 'running' | 'completed' | 'error'>('all');
  
  // התחברות לשרת והאזנה ל-traces
  useEffect(() => {
    if (initialAutoConnect) {
      socketClient.connect();
    }
    
    // האזנה לעדכוני traces
    const traceUnsubscribe = socketClient.onTrace((trace) => {
      setTraces(prev => {
        // החלפת trace קיים או הוספת חדש
        const exists = prev.some(t => t.id === trace.id);
        if (exists) {
          return prev.map(t => t.id === trace.id ? trace : t);
        } else {
          return [...prev, trace];
        }
      });
    });
    
    // האזנה לשינויים בסטטוס החיבור
    const connUnsubscribe = socketClient.onConnectionChange((connected) => {
      setIsConnected(connected);
      
      // טעינת traces קיימים בעת החיבור
      if (connected) {
        setTraces(socketClient.getAllTraces());
      }
    });
    
    // ניקוי בעת ניתוק
    return () => {
      traceUnsubscribe();
      connUnsubscribe();
      if (!initialAutoConnect) {
        socketClient.disconnect();
      }
    };
  }, [initialAutoConnect]);
  
  // בחירת trace
  const selectTrace = (traceId: string) => {
    setSelectedTraceId(traceId);
  };
  
  // ניקוי traces
  const clearTraces = () => {
    setTraces([]);
    setSelectedTraceId(null);
  };
  
  // פילטור traces לפי סטטוס
  const filteredTraces = traces.filter(trace => {
    if (filterStatus === 'all') return true;
    return trace.status === filterStatus;
  });
  
  // מיון traces - החדשים ביותר קודם
  const sortedTraces = [...filteredTraces].sort(
    (a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime()
  );
  
  // קבלת trace נבחר
  const selectedTrace = selectedTraceId 
    ? traces.find(t => t.id === selectedTraceId) 
    : null;
  
  return {
    traces: sortedTraces,
    allTraces: traces,
    selectedTrace,
    selectedTraceId,
    isConnected,
    filterStatus,
    selectTrace,
    setFilterStatus,
    clearTraces
  };
} 