#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
מערכת AI Agents לניהול חנות WooCommerce
-----------------------------------------

קובץ זה הוא נקודת הכניסה למערכת, והוא אחראי על:
1. טעינת הגדרות התצורה
2. יצירת ה-agent הראשי
3. הפעלת לולאת השיחה עם המשתמש
"""

import os
import datetime
from pathlib import Path
from openai import OpenAI
from agents.main_agent import MainAgent
from utils.tracing import setup_tracing_directory, analyze_trace, get_latest_trace
from config import get_openai_config, get_woocommerce_config
from api.woocommerce_client import WooCommerceClient

def main():
    """פונקציית הכניסה הראשית למערכת."""
    
    # הגדרת ה-API key של OpenAI
    openai_config = get_openai_config()
    api_key = openai_config["api_key"]
    
    # יצירת לקוח OpenAI
    client = OpenAI(api_key=api_key)
    
    # יצירת לקוח WooCommerce
    try:
        woo_config = get_woocommerce_config()
        woo_client = WooCommerceClient(
            url=woo_config["url"],
            consumer_key=woo_config["consumer_key"],
            consumer_secret=woo_config["consumer_secret"]
        )
        print(f"התחברות לחנות WooCommerce: {woo_config['url']}")
    except Exception as e:
        print(f"שגיאה בהתחברות לחנות WooCommerce: {str(e)}")
        print("ממשיך ללא חיבור לחנות...")
        woo_client = None
    
    # הגדרת תיקיית ה-tracing
    trace_dir = os.environ.get("TRACING_DIRECTORY", "traces")
    trace_path = setup_tracing_directory(trace_dir)
    print(f"Traces will be saved to: {trace_path}")
    
    # יצירת ה-agent הראשי
    agent = MainAgent(client, woo_client=woo_client)
    
    print("ברוכים הבאים ל-WooCommerce Agent!")
    print("הקלד 'exit' כדי לצאת")
    print("הקלד 'debug' כדי לראות את ה-trace האחרון")
    
    # לולאת שיחה
    while True:
        user_input = input("\nאתה: ")
        
        if user_input.lower() == "exit":
            break
        
        if user_input.lower() == "debug":
            latest_trace = get_latest_trace(trace_dir)
            if latest_trace:
                summary = analyze_trace(latest_trace)
                print("\n=== סיכום Trace אחרון ===")
                print(f"זמן התחלה: {summary['start_time']}")
                print(f"זמן סיום: {summary['end_time']}")
                print(f"משך: {summary['duration']} שניות")
                print(f"מספר צעדים: {summary['steps']}")
                print(f"כלים בשימוש: {', '.join(summary['tools_used']) if summary['tools_used'] else 'אין'}")
                print(f"העברות: {', '.join(summary['handoffs']) if summary['handoffs'] else 'אין'}")
                print(f"קובץ מלא: {latest_trace}")
            else:
                print("\nלא נמצאו קבצי trace.")
            continue
        
        try:
            # הפעלה ישירה של ה-agent
            response = agent.run(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nשגיאה: {str(e)}")

if __name__ == "__main__":
    main()
