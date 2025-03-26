import { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { chatApi, ChatMessage } from "@/lib/api/chatApi";

interface Message extends ChatMessage {
  loading?: boolean;
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // טעינת היסטוריית שיחה בטעינה ראשונית
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await chatApi.getHistory();
        if (history.length > 0) {
          setMessages(history);
        }
      } catch (err) {
        console.error("שגיאה בטעינת היסטוריית שיחה:", err);
      }
    };
    
    loadHistory();
    
    // ניקוי בעת עזיבת העמוד
    return () => {
      // אם יש צורך בניקוי כלשהו
    };
  }, []);
  
  // שליחת הודעה לסוכן
  const sendMessage = async (content: string) => {
    if (!content.trim()) return;
    
    // יצירת הודעת משתמש
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: "user",
      timestamp: new Date().toISOString(),
    };
    
    // יצירת הודעת טעינה לסוכן
    const loadingMessage: Message = {
      id: uuidv4(),
      content: "",
      role: "agent",
      timestamp: new Date().toISOString(),
      loading: true,
    };
    
    // הוספת ההודעות למערך
    const updatedMessages = [...messages, userMessage, loadingMessage];
    setMessages(updatedMessages);
    
    // הגדרת מצב טעינה
    setIsLoading(true);
    setError(null);
    
    try {
      // שליחת ההודעה דרך ה-API
      const response = await chatApi.sendMessage(content);
      
      // עדכון הודעת הטעינה להודעה אמיתית
      const agentMessage: Message = {
        id: uuidv4(),
        content: response.message,
        role: "agent",
        timestamp: response.timestamp || new Date().toISOString(),
      };
      
      // הסרת הודעת הטעינה והוספת הודעת הסוכן
      const finalMessages = messages
        .concat(userMessage)
        .filter(msg => !msg.loading)
        .concat(agentMessage);
      
      setMessages(finalMessages);
      
      // שמירת ההיסטוריה המקומית
      chatApi.saveHistory(finalMessages);
      
    } catch (err) {
      console.error("שגיאה בשליחת הודעה:", err);
      setError(err instanceof Error ? err.message : "שגיאה לא ידועה");
      
      // הסרת הודעת הטעינה במקרה של שגיאה
      setMessages(messages.concat(userMessage).filter(msg => !msg.loading));
    } finally {
      setIsLoading(false);
    }
  };
  
  // ניקוי היסטוריית שיחה
  const clearHistory = async () => {
    try {
      await chatApi.clearHistory();
      setMessages([]);
    } catch (err) {
      console.error("שגיאה בניקוי היסטוריית שיחה:", err);
      setError(err instanceof Error ? err.message : "שגיאה בניקוי היסטוריה");
    }
  };
  
  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearHistory
  };
} 