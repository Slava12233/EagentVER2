"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Switch } from "@/components/ui/switch";
import { useTrace } from "@/hooks/useTrace";
import { toast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
import { he } from "date-fns/locale";
import { LogEntry } from "@/lib/api/socketClient";

export default function TracePage() {
  const { 
    traces, 
    selectedTrace,
    selectedTraceId,
    isConnected, 
    filterStatus,
    selectTrace,
    setFilterStatus,
    clearTraces
  } = useTrace(true);
  
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [expandedSteps, setExpandedSteps] = useState<string[]>([]);
  
  // פונקציה להרחבה/צמצום של צעד בתוך trace
  const toggleStepExpansion = (stepId: string) => {
    setExpandedSteps(prev => 
      prev.includes(stepId) 
        ? prev.filter(id => id !== stepId) 
        : [...prev, stepId]
    );
  };
  
  // פונקציה לקבלת תגית סטטוס
  function getStatusBadge(status: 'running' | 'completed' | 'error') {
    const variants: Record<string, string> = {
      running: "default",
      completed: "default",
      error: "destructive"
    };
    
    const hebrewLabels: Record<string, string> = {
      running: "פעיל",
      completed: "הושלם",
      error: "שגיאה"
    };
    
    // שימוש ב-cn כדי להוסיף צבעים מותאמים
    const className = status === "running" 
      ? "bg-blue-500 hover:bg-blue-600" 
      : status === "completed" 
        ? "bg-green-600 hover:bg-green-700" 
        : "";
    
    return (
      <Badge variant={variants[status] as any} className={className}>
        {hebrewLabels[status]}
      </Badge>
    );
  }
  
  // פונקציה לקבלת תגית סוג צעד
  function getStepTypeBadge(stepType?: string) {
    if (!stepType) return null;
    
    const variants: Record<string, string> = {
      tool_call: "secondary",
      tool_result: "default",
      thought: "outline",
      message: "default",
      error: "destructive"
    };
    
    const hebrewLabels: Record<string, string> = {
      tool_call: "קריאת כלי",
      tool_result: "תוצאת כלי",
      thought: "מחשבה",
      message: "הודעה",
      error: "שגיאה"
    };
    
    return (
      <Badge variant={variants[stepType] as any} className="ml-2">
        {hebrewLabels[stepType] || stepType}
      </Badge>
    );
  }
  
  // פונקציה לפורמט זמן יחסי
  function formatRelativeTime(timestamp: string) {
    return formatDistanceToNow(new Date(timestamp), {
      addSuffix: true,
      locale: he
    });
  }
  
  // פונקציה להצגת קוד או טקסט מובנה
  function renderContent(content: string | any) {
    if (typeof content === 'string') {
      return <pre className="text-xs whitespace-pre-wrap">{content}</pre>;
    } else {
      return <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(content, null, 2)}</pre>;
    }
  }
  
  // פונקציה להצגת דוגמה של צעד בודד
  function renderStep(step: LogEntry) {
    const isExpanded = expandedSteps.includes(step.id);
    
    return (
      <div key={step.id} className={cn(
        "p-3 border-b last:border-b-0 transition-colors",
        step.parentId ? "mr-4 border-r" : ""
      )}>
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            {getStepTypeBadge(step.stepType)}
            <span className="font-medium text-sm">{step.agent}</span>
          </div>
          <span className="text-xs text-muted-foreground">
            {formatRelativeTime(step.timestamp)}
            {step.duration && ` (${step.duration}ms)`}
          </span>
        </div>
        
        <div className="text-sm mb-2">{step.message}</div>
        
        {step.details && (
          <div className="mt-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => toggleStepExpansion(step.id)}
              className="mb-1"
            >
              {isExpanded ? "הסתר פרטים" : "הצג פרטים"}
            </Button>
            
            {isExpanded && (
              <div className="p-2 bg-muted rounded-md">
                {renderContent(step.details)}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // פונקציה להצגת Trace מלא
  function renderTrace(steps: LogEntry[]) {
    if (!steps || steps.length === 0) {
      return (
        <div className="p-4 text-center text-muted-foreground">
          אין צעדים להצגה
        </div>
      );
    }
    
    // מיון הצעדים לפי זמן
    const sortedSteps = [...steps].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    
    // ארגון צעדים לפי היררכיה
    const rootSteps = sortedSteps.filter(step => !step.parentId);
    const childrenMap = new Map<string, LogEntry[]>();
    
    sortedSteps.forEach(step => {
      if (step.parentId) {
        const children = childrenMap.get(step.parentId) || [];
        children.push(step);
        childrenMap.set(step.parentId, children);
      }
    });
    
    // פונקציה רקורסיבית להצגת צעדים
    const renderStepWithChildren = (step: LogEntry) => {
      const children = childrenMap.get(step.id) || [];
      
      return (
        <div key={step.id} className="border-r border-gray-200 mr-2 pr-2">
          {renderStep(step)}
          {children.length > 0 && (
            <div className="mt-1 mr-4 border-r pl-2">
              {children.map(renderStepWithChildren)}
            </div>
          )}
        </div>
      );
    };
    
    return (
      <div className="space-y-0">
        {rootSteps.map(renderStepWithChildren)}
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">צעדי ביצוע (Trace)</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.location.reload()}>
            רענן
          </Button>
          <Button variant="outline" onClick={clearTraces}>
            נקה
          </Button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* רשימת Traces */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex justify-between items-center">
              <span>רשימת Traces</span>
              <Badge 
                variant={isConnected ? "default" : "destructive"} 
                className={isConnected ? "bg-green-600 hover:bg-green-700" : ""}
              >
                {isConnected ? "מחובר" : "מנותק"}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-4">
              <Badge 
                variant={filterStatus === "all" ? "default" : "outline"}
                className="cursor-pointer"
                onClick={() => setFilterStatus("all")}
              >
                הכל
              </Badge>
              <Badge 
                variant={filterStatus === "running" ? "default" : "outline"}
                className={cn("cursor-pointer", filterStatus === "running" ? "bg-blue-500 hover:bg-blue-600" : "")}
                onClick={() => setFilterStatus("running")}
              >
                פעיל
              </Badge>
              <Badge 
                variant={filterStatus === "completed" ? "default" : "outline"}
                className={cn("cursor-pointer", filterStatus === "completed" ? "bg-green-600 hover:bg-green-700" : "")}
                onClick={() => setFilterStatus("completed")}
              >
                הושלם
              </Badge>
              <Badge 
                variant={filterStatus === "error" ? "destructive" : "outline"}
                className="cursor-pointer"
                onClick={() => setFilterStatus("error")}
              >
                שגיאה
              </Badge>
            </div>
            
            <ScrollArea className="h-[600px]">
              {traces.length === 0 ? (
                <div className="p-12 text-center text-muted-foreground">
                  אין Traces להצגה
                </div>
              ) : (
                <div className="space-y-2">
                  {traces.map(trace => (
                    <div 
                      key={trace.id}
                      className={cn(
                        "p-3 border rounded-md cursor-pointer hover:bg-muted transition-colors",
                        selectedTraceId === trace.id ? "border-primary bg-muted/50" : ""
                      )}
                      onClick={() => selectTrace(trace.id)}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{trace.name}</span>
                        {getStatusBadge(trace.status)}
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        <span>{formatRelativeTime(trace.startTime)}</span>
                        <span className="mx-1">•</span>
                        <span>{trace.steps.length} צעדים</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
        
        {/* פרטי Trace */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex justify-between items-center">
              <span>
                {selectedTrace 
                  ? `${selectedTrace.name} ${getStatusBadge(selectedTrace.status)}` 
                  : "פרטי Trace"}
              </span>
              <div className="flex items-center gap-2">
                <Switch
                  checked={autoScroll}
                  onCheckedChange={setAutoScroll}
                  id="auto-scroll"
                />
                <label htmlFor="auto-scroll" className="text-sm">גלילה אוטומטית</label>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px] pr-4">
              {!selectedTrace ? (
                <div className="flex h-full items-center justify-center text-muted-foreground">
                  בחר Trace מהרשימה כדי לצפות בפרטים
                </div>
              ) : (
                <div>
                  <div className="mb-4 pb-2 border-b">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="font-medium">התחלה:</span>{" "}
                        {new Date(selectedTrace.startTime).toLocaleString("he-IL")}
                      </div>
                      {selectedTrace.endTime && (
                        <div>
                          <span className="font-medium">סיום:</span>{" "}
                          {new Date(selectedTrace.endTime).toLocaleString("he-IL")}
                        </div>
                      )}
                      <div>
                        <span className="font-medium">משך:</span>{" "}
                        {selectedTrace.endTime 
                          ? `${Math.round((new Date(selectedTrace.endTime).getTime() - new Date(selectedTrace.startTime).getTime()) / 1000)} שניות`
                          : "פעיל..."}
                      </div>
                      <div>
                        <span className="font-medium">צעדים:</span> {selectedTrace.steps.length}
                      </div>
                    </div>
                  </div>
                  
                  {renderTrace(selectedTrace.steps)}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 