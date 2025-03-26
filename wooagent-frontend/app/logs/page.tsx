"use client";

import React, { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { useLogs } from "@/hooks/useLogs";
import { toast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";

export default function LogsPage() {
  const { 
    logs, 
    isConnected, 
    autoScroll, 
    setAutoScroll, 
    filter, 
    setFilter, 
    clearLogs, 
    connect, 
    disconnect,
    refreshLogs
  } = useLogs(true);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [expandedLogs, setExpandedLogs] = useState<string[]>([]);
  const [expandedDetails, setExpandedDetails] = useState<string[]>([]);
  
  // גלילה אוטומטית כאשר מתקבלים לוגים חדשים
  useEffect(() => {
    if (autoScroll && scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);
  
  const handleClearLogs = () => {
    clearLogs();
    toast.info({ title: "הלוגים נוקו" });
  };

  const handleRefreshLogs = () => {
    refreshLogs(200); // בקשת 200 הלוגים האחרונים
    toast.info({ title: "מרענן לוגים..." });
  };
  
  // פונקציות להרחבת והסתרת תוכן ארוך
  const toggleLogExpansion = (logId: string) => {
    setExpandedLogs(prev => 
      prev.includes(logId) 
        ? prev.filter(id => id !== logId) 
        : [...prev, logId]
    );
  };
  
  const toggleDetailsExpansion = (logId: string) => {
    setExpandedDetails(prev => 
      prev.includes(logId) 
        ? prev.filter(id => id !== logId) 
        : [...prev, logId]
    );
  };
  
  // פונקצית עזר להצגת תג צבעוני לפי רמת הלוג
  function getLevelBadge(level: string) {
    const variants: Record<string, string> = {
      error: "destructive",
      warning: "default", // נשתמש ב-default עם צבע מותאם
      debug: "secondary",
      info: "default"
    };
    
    const hebrewLabels: Record<string, string> = {
      error: "שגיאה",
      warning: "אזהרה",
      debug: "דיבאג",
      info: "מידע"
    };
    
    // שימוש ב-cn כדי להוסיף צבעים מותאמים לאזהרות
    const className = level === "warning" ? "bg-yellow-500 hover:bg-yellow-600" : "";
    
    return (
      <Badge variant={variants[level] as any} className={className}>
        {hebrewLabels[level] || level}
      </Badge>
    );
  }
  
  const handleFilterClick = (level: "all" | "debug" | "info" | "warning" | "error") => {
    setFilter(prev => ({ ...prev, level }));
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">לוגים</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRefreshLogs}>
            רענן לוגים
          </Button>
          <Button variant="outline" onClick={handleClearLogs}>
            נקה לוגים
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>לוגי מערכת</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Badge 
                variant={filter.level === "all" ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => handleFilterClick("all")}
              >
                הכל
              </Badge>
              <Badge 
                variant={filter.level === "info" ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => handleFilterClick("info")}
              >
                מידע
              </Badge>
              <Badge 
                variant={filter.level === "debug" ? "secondary" : "outline"}
                className="cursor-pointer"
                onClick={() => handleFilterClick("debug")}
              >
                דיבאג
              </Badge>
              <Badge 
                variant={filter.level === "warning" ? "default" : "outline"}
                className={cn("cursor-pointer", filter.level === "warning" ? "bg-yellow-500 hover:bg-yellow-600" : "")}
                onClick={() => handleFilterClick("warning")}
              >
                אזהרות
              </Badge>
              <Badge 
                variant={filter.level === "error" ? "destructive" : "outline"}
                className="cursor-pointer"
                onClick={() => handleFilterClick("error")}
              >
                שגיאות
              </Badge>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Switch
                  checked={autoScroll}
                  onCheckedChange={setAutoScroll}
                  id="auto-scroll"
                />
                <label htmlFor="auto-scroll" className="text-sm">גלילה אוטומטית</label>
              </div>
              
              <Badge 
                variant={isConnected ? "default" : "destructive"} 
                className={isConnected ? "bg-green-600 hover:bg-green-700" : ""}
              >
                {isConnected ? "מחובר" : "מנותק"}
              </Badge>
            </div>
          </div>

          <ScrollArea className="h-[400px] border rounded-md" ref={scrollAreaRef}>
            <div className="p-4 space-y-2">
              {logs.length === 0 ? (
                <div className="flex h-40 items-center justify-center text-muted-foreground">
                  אין לוגים להצגה
                </div>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className="p-2 border-b last:border-b-0">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        {getLevelBadge(log.level)}
                        <span className="font-medium">{log.agent}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleTimeString("he-IL")}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">
                      {log.message.length > 300 
                        ? (
                          <>
                            {expandedLogs.includes(log.id) 
                              ? log.message 
                              : log.message.substring(0, 300) + '...'}
                            <Button 
                              variant="link" 
                              size="sm" 
                              className="p-0 h-auto text-xs" 
                              onClick={() => toggleLogExpansion(log.id)}
                            >
                              {expandedLogs.includes(log.id) ? 'הסתר' : 'הצג הכל'}
                            </Button>
                          </>
                        ) 
                        : log.message
                      }
                    </p>
                    {log.details && (
                      <>
                        <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-x-auto max-h-[150px] overflow-y-auto">
                          {typeof log.details === 'string' 
                            ? (log.details.length > 500 && !expandedDetails.includes(log.id)
                                ? log.details.substring(0, 500) + '...' 
                                : log.details)
                            : JSON.stringify(log.details, null, 2).length > 500 && !expandedDetails.includes(log.id)
                              ? JSON.stringify(log.details, null, 2).substring(0, 500) + '...'
                              : JSON.stringify(log.details, null, 2)
                          }
                        </pre>
                        {((typeof log.details === 'string' && log.details.length > 500) ||
                          (typeof log.details !== 'string' && JSON.stringify(log.details, null, 2).length > 500)) && (
                          <Button 
                            variant="link" 
                            size="sm" 
                            className="p-0 h-auto text-xs mt-1" 
                            onClick={() => toggleDetailsExpansion(log.id)}
                          >
                            {expandedDetails.includes(log.id) ? 'הסתר פרטים' : 'הצג את כל הפרטים'}
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
} 