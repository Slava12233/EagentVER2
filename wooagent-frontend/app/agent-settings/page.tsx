"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";

export default function AgentSettingsPage() {
  const [isSaving, setIsSaving] = useState<boolean>(false);

  const saveSettings = () => {
    setIsSaving(true);
    // כאן יהיה קוד לשמירת ההגדרות
    setTimeout(() => {
      setIsSaving(false);
    }, 1500);
  };

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-3xl font-bold mb-6">הגדרות סוכן</h1>
      
      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">הגדרות כלליות</TabsTrigger>
          <TabsTrigger value="behavior">התנהגות</TabsTrigger>
          <TabsTrigger value="api">הגדרות API</TabsTrigger>
          <TabsTrigger value="advanced">הגדרות מתקדמות</TabsTrigger>
        </TabsList>
        
        <TabsContent value="general" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle>הגדרות כלליות</CardTitle>
              <CardDescription>הגדר את הפרמטרים הבסיסיים של הסוכן</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="agent-name">שם הסוכן</Label>
                <Input id="agent-name" defaultValue="WooAgent" />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="agent-description">תיאור הסוכן</Label>
                <Textarea 
                  id="agent-description" 
                  placeholder="תיאור קצר של תפקיד הסוכן והיכולות שלו"
                  defaultValue="סוכן חכם לניהול חנות WooCommerce שמסייע ללקוחות, עונה על שאלות ומסייע בניהול החנות."
                  className="min-h-[100px]"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="agent-model">מודל בסיס</Label>
                <Select defaultValue="gpt-4">
                  <SelectTrigger id="agent-model">
                    <SelectValue placeholder="בחר מודל" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                    <SelectItem value="gpt-4">GPT-4</SelectItem>
                    <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                    <SelectItem value="claude-3">Claude 3</SelectItem>
                    <SelectItem value="gemini-pro">Gemini Pro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="agent-language">שפה מועדפת</Label>
                <Select defaultValue="hebrew">
                  <SelectTrigger id="agent-language">
                    <SelectValue placeholder="בחר שפה" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hebrew">עברית</SelectItem>
                    <SelectItem value="english">אנגלית</SelectItem>
                    <SelectItem value="auto">זיהוי אוטומטי</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="agent-active">הפעל סוכן</Label>
                <Switch id="agent-active" defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="behavior" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle>התנהגות הסוכן</CardTitle>
              <CardDescription>הגדר כיצד הסוכן מתנהג ומתקשר עם משתמשים</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label htmlFor="creativity">יצירתיות</Label>
                    <span className="text-muted-foreground">0.7</span>
                  </div>
                  <Slider defaultValue={[0.7]} max={1} step={0.1} />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label htmlFor="helpfulness">מידת העזרה</Label>
                    <span className="text-muted-foreground">0.9</span>
                  </div>
                  <Slider defaultValue={[0.9]} max={1} step={0.1} />
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label htmlFor="verbosity">כמות המידע</Label>
                    <span className="text-muted-foreground">0.6</span>
                  </div>
                  <Slider defaultValue={[0.6]} max={1} step={0.1} />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="greeting">הודעת פתיחה</Label>
                <Textarea 
                  id="greeting" 
                  placeholder="הודעת פתיחה לכל שיחה חדשה"
                  defaultValue="שלום! אני WooAgent, הסוכן החכם של החנות. איך אוכל לעזור לך היום?"
                  className="min-h-[100px]"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="personality">אישיות</Label>
                <Select defaultValue="helpful">
                  <SelectTrigger id="personality">
                    <SelectValue placeholder="בחר סגנון אישיות" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="helpful">עוזר ואדיב</SelectItem>
                    <SelectItem value="professional">מקצועי ותכליתי</SelectItem>
                    <SelectItem value="friendly">ידידותי וקליל</SelectItem>
                    <SelectItem value="expert">מומחה ומפורט</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="memory-enabled">זיכרון שיחות קודמות</Label>
                <Switch id="memory-enabled" defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="api" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle>הגדרות API</CardTitle>
              <CardDescription>הגדר את פרטי החיבור למודלים חיצוניים</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="openai-key">מפתח OpenAI</Label>
                <Input id="openai-key" type="password" placeholder="sk-..." />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="anthropic-key">מפתח Anthropic (Claude)</Label>
                <Input id="anthropic-key" type="password" placeholder="sk-ant-..." />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="google-key">מפתח Google AI (Gemini)</Label>
                <Input id="google-key" type="password" placeholder="AIza..." />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="api-endpoint">נקודת קצה מותאמת אישית</Label>
                <Input id="api-endpoint" placeholder="https://api.example.com/v1" />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="use-proxy">השתמש בפרוקסי</Label>
                <Switch id="use-proxy" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="advanced" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle>הגדרות מתקדמות</CardTitle>
              <CardDescription>הגדרות מתקדמות לשליטה מלאה בהתנהגות הסוכן</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="max-tokens">מספר טוקנים מקסימלי</Label>
                <Input id="max-tokens" type="number" defaultValue="2048" />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="temperature">טמפרטורה</Label>
                <div className="flex justify-between">
                  <Slider defaultValue={[0.7]} max={1} step={0.1} className="flex-1 mr-4" />
                  <Input id="temperature" type="number" defaultValue="0.7" className="w-16" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="system-prompt">הנחיית מערכת</Label>
                <Textarea 
                  id="system-prompt" 
                  placeholder="הנחיות מערכת מתקדמות"
                  defaultValue="אתה סוכן WooCommerce מועיל שמסייע למשתמשים לנהל את החנות שלהם. עליך להיות מנומס, מדויק ולספק מידע מועיל. כשאתה לא בטוח, בקש הבהרות. הימנע מלהמציא מידע."
                  className="min-h-[150px]"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="function-calling">סגנון קריאה לפונקציות</Label>
                <Select defaultValue="auto">
                  <SelectTrigger id="function-calling">
                    <SelectValue placeholder="בחר סגנון" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">אוטומטי</SelectItem>
                    <SelectItem value="none">מבוטל</SelectItem>
                    <SelectItem value="forced">מאולץ</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="debug-mode">מצב דיבאג</Label>
                <Switch id="debug-mode" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      
      <div className="mt-6 flex justify-end">
        <Button onClick={saveSettings} disabled={isSaving}>
          {isSaving ? "שומר..." : "שמור הגדרות"}
        </Button>
      </div>
    </div>
  );
} 