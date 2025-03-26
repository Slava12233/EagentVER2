"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function TrainingPage() {
  const [selectedTrainingMethod, setSelectedTrainingMethod] = useState<string>("conversations");
  const [isTraining, setIsTraining] = useState<boolean>(false);

  const startTraining = () => {
    setIsTraining(true);
    // כאן יהיה קוד להתחלת האימון
    setTimeout(() => {
      setIsTraining(false);
    }, 3000);
  };

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-3xl font-bold mb-6">אימון סוכן</h1>
      
      <Tabs defaultValue="training" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="training">אימון הסוכן</TabsTrigger>
          <TabsTrigger value="history">היסטוריית אימון</TabsTrigger>
          <TabsTrigger value="settings">הגדרות אימון</TabsTrigger>
        </TabsList>
        
        <TabsContent value="training" className="space-y-4 mt-4">
          <Card>
            <CardHeader>
              <CardTitle>בחירת שיטת אימון</CardTitle>
              <CardDescription>בחר את שיטת האימון המתאימה לצרכיך</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card 
                  className={`cursor-pointer border-2 ${selectedTrainingMethod === "conversations" ? "border-primary" : "border-border"}`} 
                  onClick={() => setSelectedTrainingMethod("conversations")}
                >
                  <CardHeader>
                    <CardTitle className="text-lg">אימון משיחות</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>אימון הסוכן על בסיס שיחות ותשובות קודמות</p>
                  </CardContent>
                </Card>
                
                <Card 
                  className={`cursor-pointer border-2 ${selectedTrainingMethod === "data" ? "border-primary" : "border-border"}`} 
                  onClick={() => setSelectedTrainingMethod("data")}
                >
                  <CardHeader>
                    <CardTitle className="text-lg">אימון מנתונים</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>העלאת קבצים ונתונים לאימון המודל</p>
                  </CardContent>
                </Card>
                
                <Card 
                  className={`cursor-pointer border-2 ${selectedTrainingMethod === "manual" ? "border-primary" : "border-border"}`} 
                  onClick={() => setSelectedTrainingMethod("manual")}
                >
                  <CardHeader>
                    <CardTitle className="text-lg">אימון ידני</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p>הכנסת דוגמאות ומקרים ספציפיים לאימון</p>
                  </CardContent>
                </Card>
              </div>
              
              {selectedTrainingMethod === "conversations" && (
                <div className="mt-6 space-y-4">
                  <div className="space-y-2">
                    <Label>בחר שיחות לאימון</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="בחר טווח תאריכים" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">כל השיחות</SelectItem>
                        <SelectItem value="last-week">שיחות מהשבוע האחרון</SelectItem>
                        <SelectItem value="last-month">שיחות מהחודש האחרון</SelectItem>
                        <SelectItem value="custom">טווח מותאם אישית</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Checkbox id="only-positive" />
                    <Label htmlFor="only-positive">השתמש רק בשיחות שקיבלו משוב חיובי</Label>
                  </div>
                </div>
              )}
              
              {selectedTrainingMethod === "data" && (
                <div className="mt-6 space-y-4">
                  <div className="border-2 border-dashed border-border rounded-lg p-12 text-center">
                    <h3 className="text-lg font-medium mb-2">העלאת קבצים</h3>
                    <p className="text-muted-foreground mb-4">גרור קבצים לכאן או לחץ לבחירת קבצים</p>
                    <Button variant="outline">בחר קבצים</Button>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>סוג הנתונים</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="בחר סוג נתונים" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="product-data">נתוני מוצרים</SelectItem>
                        <SelectItem value="customer-data">נתוני לקוחות</SelectItem>
                        <SelectItem value="orders-data">נתוני הזמנות</SelectItem>
                        <SelectItem value="mixed">נתונים מעורבים</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
              
              {selectedTrainingMethod === "manual" && (
                <div className="mt-6 space-y-4">
                  <div className="space-y-2">
                    <Label>שאלה לדוגמה</Label>
                    <Input placeholder="הכנס שאלה לדוגמה" />
                  </div>
                  
                  <div className="space-y-2">
                    <Label>תשובה רצויה</Label>
                    <Textarea placeholder="הכנס את התשובה הרצויה" className="min-h-[120px]" />
                  </div>
                  
                  <Button variant="outline">הוסף דוגמה נוספת</Button>
                </div>
              )}
              
              <div className="mt-6">
                <Button onClick={startTraining} disabled={isTraining}>
                  {isTraining ? "מאמן..." : "התחל אימון"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>היסטוריית אימון</CardTitle>
              <CardDescription>צפייה בתהליכי אימון קודמים והתקדמות</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-center text-muted-foreground py-8">אין היסטוריית אימון זמינה</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>הגדרות אימון</CardTitle>
              <CardDescription>התאמת הגדרות תהליך האימון</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>מספר סבבי אימון</Label>
                  <Input type="number" defaultValue="3" />
                </div>
                
                <div className="space-y-2">
                  <Label>קצב למידה</Label>
                  <Select defaultValue="medium">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">נמוך (0.0001)</SelectItem>
                      <SelectItem value="medium">בינוני (0.001)</SelectItem>
                      <SelectItem value="high">גבוה (0.01)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex items-center space-x-2 space-x-reverse">
                  <Checkbox id="enable-notifications" defaultChecked />
                  <Label htmlFor="enable-notifications">קבל התראות בסיום תהליך האימון</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 