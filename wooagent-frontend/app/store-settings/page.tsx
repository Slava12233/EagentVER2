"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useStoreSettings } from "@/hooks/useStoreSettings";
import { StoreConnectionConfig } from "@/lib/api/storeApi";
import { toast } from "@/components/ui/toast";
import { Loader2 } from "lucide-react";

export default function StoreSettingsPage() {
  const { settings, isLoading, error, saveSettings, testConnection } = useStoreSettings();
  const [formData, setFormData] = useState<StoreConnectionConfig>({
    name: "",
    url: "",
    consumerKey: "",
    consumerSecret: "",
    apiVersion: "wc/v3",
    description: ""
  });
  const [isTesting, setIsTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // כאשר הגדרות נטענות, עדכן את הטופס
  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      const result = await saveSettings(formData);
      
      if (result.success) {
        toast.success({
          title: "ההגדרות נשמרו בהצלחה",
        });
      } else {
        toast.error({
          title: "שגיאה בשמירת ההגדרות",
          description: result.error
        });
      }
    } catch (err) {
      toast.error({
        title: "שגיאה בשמירת ההגדרות",
        description: err instanceof Error ? err.message : "שגיאה לא ידועה"
      });
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleTestConnection = async () => {
    setIsTesting(true);
    
    try {
      const result = await testConnection(formData);
      
      if (result.success) {
        toast.success({
          title: "החיבור הצליח!",
          description: `נמצאו ${result.products} מוצרים ו-${result.orders} הזמנות`
        });
      } else {
        toast.error({
          title: "החיבור נכשל",
          description: result.error || "אירעה שגיאה בחיבור לחנות"
        });
      }
    } catch (err) {
      toast.error({
        title: "החיבור נכשל",
        description: err instanceof Error ? err.message : "אירעה שגיאה בחיבור לחנות"
      });
    } finally {
      setIsTesting(false);
    }
  };
  
  if (isLoading && !settings) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">הגדרות חנות</h1>
      <p className="text-muted-foreground">הגדר את פרטי החיבור לחנות ה-WooCommerce שלך</p>

      <Card>
        <CardHeader>
          <CardTitle>פרטי חיבור</CardTitle>
          <CardDescription>פרטי החיבור לחנות WooCommerce</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div className="grid gap-2">
                <label htmlFor="name" className="text-sm font-medium">
                  שם החנות
                </label>
                <Input 
                  id="name" 
                  placeholder="הזן שם לחנות" 
                  value={formData.name}
                  onChange={handleInputChange}
                />
              </div>

              <div className="grid gap-2">
                <label htmlFor="url" className="text-sm font-medium">
                  כתובת החנות
                </label>
                <Input 
                  id="url" 
                  placeholder="https://example.com" 
                  value={formData.url}
                  onChange={handleInputChange}
                />
              </div>

              <div className="grid gap-2">
                <label htmlFor="consumerKey" className="text-sm font-medium">
                  מפתח צרכן
                </label>
                <Input 
                  id="consumerKey" 
                  placeholder="ck_xxxxxxxxxxxxxxxxxxxx" 
                  value={formData.consumerKey}
                  onChange={handleInputChange}
                />
              </div>

              <div className="grid gap-2">
                <label htmlFor="consumerSecret" className="text-sm font-medium">
                  סוד צרכן
                </label>
                <Input
                  id="consumerSecret"
                  type="password"
                  placeholder="cs_xxxxxxxxxxxxxxxxxxxx"
                  value={formData.consumerSecret}
                  onChange={handleInputChange}
                />
              </div>

              <div className="grid gap-2">
                <label htmlFor="apiVersion" className="text-sm font-medium">
                  גרסת API
                </label>
                <Input 
                  id="apiVersion" 
                  placeholder="wc/v3" 
                  defaultValue="wc/v3" 
                  value={formData.apiVersion}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="flex justify-between">
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleTestConnection}
                disabled={isTesting || isSaving}
              >
                {isTesting ? (
                  <>
                    <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                    בודק חיבור...
                  </>
                ) : (
                  "בדוק חיבור"
                )}
              </Button>
              <Button 
                type="submit"
                disabled={isTesting || isSaving}
              >
                {isSaving ? (
                  <>
                    <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                    שומר...
                  </>
                ) : (
                  "שמור הגדרות"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 