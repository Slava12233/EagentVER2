"use client";

import React, { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar } from "@/components/ui/avatar";
import { Loader2, Send, Trash2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useChat } from "@/hooks/useChat";
import { toast } from "@/components/ui/toast";

interface Message {
  id: string;
  content: string;
  role: "user" | "agent";
  timestamp: string;
  loading?: boolean;
}

export default function ChatPage() {
  const [inputValue, setInputValue] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { messages, isLoading, error, sendMessage, clearHistory } = useChat();
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;
    
    setInputValue("");
    await sendMessage(inputValue);
  };
  
  const handleClearHistory = async () => {
    if (messages.length === 0) {
      toast.info({ title: "אין היסטוריית שיחה למחיקה" });
      return;
    }
    
    await clearHistory();
    toast.success({ title: "היסטוריית השיחה נמחקה" });
  };
  
  // גלילה אוטומטית למטה בכל פעם שנוספת הודעה חדשה
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);
  
  // הצגת שגיאות כ-toast
  useEffect(() => {
    if (error) {
      toast.error({
        title: "שגיאת תקשורת",
        description: error
      });
    }
  }, [error]);
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">צ'אט</h1>
          <p className="text-muted-foreground">דבר עם הסוכן שלך ושאל שאלות לגבי החנות</p>
        </div>
        
        <Button
          variant="outline"
          size="sm"
          className="gap-2"
          onClick={handleClearHistory}
          disabled={messages.length === 0 || isLoading}
        >
          <Trash2 className="h-4 w-4" />
          נקה היסטוריה
        </Button>
      </div>

      <Card className="h-[calc(100vh-180px)]">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>שיחה עם הסוכן</CardTitle>
            <CardDescription>שאל שאלות ובקש מידע על המוצרים, ההזמנות והחנות</CardDescription>
          </div>
          <div className={`h-3 w-3 rounded-full ${isLoading ? 'bg-yellow-500' : 'bg-green-500'}`}></div>
        </CardHeader>
        <CardContent className="flex flex-col h-[calc(100%-5rem)]">
          <ScrollArea 
            className="flex-1 pr-4 mb-4"
            ref={scrollAreaRef}
          >
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="flex h-32 items-center justify-center text-muted-foreground">
                  עוד לא התחלת שיחה. שלח הודעה כדי להתחיל.
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.role === "agent" ? "justify-start" : "justify-end"
                    } gap-2`}
                  >
                    {message.role === "agent" && (
                      <Avatar>
                        <div className="bg-primary text-white h-full w-full flex items-center justify-center">
                          AI
                        </div>
                      </Avatar>
                    )}
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${
                        message.role === "agent"
                          ? "bg-muted"
                          : "bg-primary text-primary-foreground"
                      }`}
                    >
                      {message.loading ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <div className="whitespace-pre-wrap">{message.content}</div>
                      )}
                      <div
                        className={`text-xs mt-1 ${
                          message.role === "agent"
                            ? "text-muted-foreground"
                            : "text-primary-foreground/80"
                        }`}
                      >
                        {new Date(message.timestamp).toLocaleTimeString("he-IL")}
                      </div>
                    </div>
                    {message.role === "user" && (
                      <Avatar>
                        <div className="bg-secondary text-secondary-foreground h-full w-full flex items-center justify-center">
                          משתמש
                        </div>
                      </Avatar>
                    )}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>

          <form className="flex gap-2" onSubmit={handleSendMessage}>
            <Input
              placeholder="הקלד הודעה..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <Button type="submit" size="icon" disabled={isLoading || !inputValue.trim()}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 