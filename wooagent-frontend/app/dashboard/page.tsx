"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAgentStatus } from "@/hooks/useAgentStatus";
import { Loader2, Power, RefreshCw } from "lucide-react";
import { toast } from "@/components/ui/toast";
import { formatDistance } from "date-fns";
import { he } from "date-fns/locale";

export default function Dashboard() {
  const { status, isLoading, error, startAgent, stopAgent, restartAgent, refreshStatus } = useAgentStatus();
  
  const handleStartAgent = async () => {
    const result = await startAgent();
    
    if (result.success) {
      toast.success({
        title: "הסוכן הופעל בהצלחה",
      });
    } else {
      toast.error({
        title: "שגיאה בהפעלת הסוכן",
        description: result.error
      });
    }
  };
  
  const handleStopAgent = async () => {
    const result = await stopAgent();
    
    if (result.success) {
      toast.success({
        title: "הסוכן הופסק בהצלחה",
      });
    } else {
      toast.error({
        title: "שגיאה בהפסקת הסוכן",
        description: result.error
      });
    }
  };
  
  const handleRestartAgent = async () => {
    const result = await restartAgent();
    
    if (result.success) {
      toast.success({
        title: "הסוכן הופעל מחדש בהצלחה",
      });
    } else {
      toast.error({
        title: "שגיאה בהפעלה מחדש של הסוכן",
        description: result.error
      });
    }
  };
  
  const formatUptime = (seconds: number | undefined) => {
    if (!seconds) return "לא זמין";
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours} שעות ו-${minutes} דקות`;
    } else {
      return `${minutes} דקות`;
    }
  };
  
  const formatStartTime = (startTime: string | undefined) => {
    if (!startTime) return "לא זמין";
    
    return formatDistance(new Date(startTime), new Date(), { 
      addSuffix: true,
      locale: he 
    });
  };
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">דשבורד</h1>
      <p className="text-muted-foreground">ברוכים הבאים לממשק הניהול של WooAgent.</p>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>סטטוס סוכן</CardTitle>
            <CardDescription>מצב נוכחי של הסוכן</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex items-center justify-center h-12">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className={`h-3 w-3 rounded-full ${status?.isRunning ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <div>{status?.isRunning ? "פעיל" : "לא פעיל"}</div>
                </div>
                
                {status?.isRunning && (
                  <>
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">מודל: </span>
                      <span>{status?.modelName || "לא ידוע"}</span>
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">זמן פעילות: </span>
                      <span>{formatUptime(status?.uptime)}</span>
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">הופעל: </span>
                      <span>{formatStartTime(status?.startTime)}</span>
                    </div>
                  </>
                )}
                
                <div className="flex gap-2 mt-4">
                  {status?.isRunning ? (
                    <>
                      <Button size="sm" variant="outline" onClick={handleRestartAgent}>
                        <RefreshCw className="ml-2 h-4 w-4" />
                        הפעל מחדש
                      </Button>
                      <Button size="sm" variant="destructive" onClick={handleStopAgent}>
                        <Power className="ml-2 h-4 w-4" />
                        הפסק
                      </Button>
                    </>
                  ) : (
                    <Button size="sm" onClick={handleStartAgent}>
                      <Power className="ml-2 h-4 w-4" />
                      הפעל
                    </Button>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>חנות WooCommerce</CardTitle>
            <CardDescription>סטטוס החיבור לחנות</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className={`h-3 w-3 rounded-full ${status?.connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <div>{status?.connectionStatus === 'connected' ? "מחובר" : "מנותק"}</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>פעילות אחרונה</CardTitle>
            <CardDescription>הפעולות האחרונות של הסוכן</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm">אין פעילות אחרונה</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 