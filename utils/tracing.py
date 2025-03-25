#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
מודול לניטור ודיבוג של פעולות ה-Agents
----------------------------------------

מודול זה מספק פונקציות לניטור ודיבוג של פעולות ה-Agents.
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List

class Trace:
    """מחלקה לניטור פעולות ה-Agents"""
    
    def __init__(self):
        self.start_time = datetime.datetime.now().isoformat()
        self.end_time = None
        self.steps = []
        self.events = []
    
    def add_step(self, step_type: str, data: Dict[str, Any]):
        """הוספת צעד לרצף הפעולות"""
        self.steps.append({
            "type": step_type,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def add_event(self, event_type: str, data: Dict[str, Any]):
        """הוספת אירוע לרצף האירועים"""
        self.events.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def end(self):
        """סיום הניטור"""
        self.end_time = datetime.datetime.now().isoformat()
    
    def to_json(self) -> Dict[str, Any]:
        """המרה לפורמט JSON"""
        if not self.end_time:
            self.end()
        
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (datetime.datetime.fromisoformat(self.end_time) - 
                        datetime.datetime.fromisoformat(self.start_time)).total_seconds(),
            "steps": self.steps,
            "events": self.events
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """המרה למילון (לצורך שמירה בפורמט JSON)"""
        return self.to_json()
    
    @classmethod
    def capture(cls):
        """יצירת הקשר ניטור חדש"""
        return cls()

def setup_tracing_directory(trace_dir="traces"):
    """
    מגדיר את תיקיית ה-traces לשמירת קבצי ה-trace.
    
    Args:
        trace_dir: שם התיקייה (ברירת מחדל: "traces")
    
    Returns:
        נתיב התיקייה שנוצרה
    """
    trace_path = Path(trace_dir)
    trace_path.mkdir(exist_ok=True)
    return trace_path

def save_trace(trace: Trace, trace_dir="traces"):
    """
    שומר את ה-trace לקובץ JSON.
    
    Args:
        trace: אובייקט ה-Trace
        trace_dir: שם התיקייה (ברירת מחדל: "traces")
    
    Returns:
        נתיב הקובץ שנוצר
    """
    trace_path = Path(trace_dir)
    trace_path.mkdir(exist_ok=True)
    
    # יצירת שם קובץ עם חותמת זמן
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trace_{timestamp}.json"
    file_path = trace_path / filename
    
    # המרת ה-trace לפורמט JSON
    trace_data = trace.to_json()
    
    # שמירת ה-trace לקובץ
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, ensure_ascii=False, indent=2)
    
    return file_path

def analyze_trace(trace_file):
    """
    מנתח קובץ trace ומחזיר מידע מסוכם.
    
    Args:
        trace_file: נתיב לקובץ ה-trace
    
    Returns:
        מידע מסוכם על ה-trace
    """
    with open(trace_file, "r", encoding="utf-8") as f:
        trace_data = json.load(f)
    
    # ניתוח בסיסי של ה-trace
    summary = {
        "start_time": trace_data.get("start_time"),
        "end_time": trace_data.get("end_time"),
        "duration": trace_data.get("duration"),
        "steps": len(trace_data.get("steps", [])),
        "tools_used": [],
        "handoffs": []
    }
    
    # איסוף מידע על כלים שהיו בשימוש
    for step in trace_data.get("steps", []):
        if step.get("type") == "tool_call":
            tool_name = step.get("data", {}).get("name")
            if tool_name and tool_name not in summary["tools_used"]:
                summary["tools_used"].append(tool_name)
        
        if step.get("type") == "handoff":
            handoff_name = step.get("data", {}).get("name")
            if handoff_name and handoff_name not in summary["handoffs"]:
                summary["handoffs"].append(handoff_name)
    
    return summary

def list_traces(trace_dir="traces"):
    """
    מחזיר רשימה של כל קבצי ה-trace בתיקייה.
    
    Args:
        trace_dir: שם התיקייה (ברירת מחדל: "traces")
    
    Returns:
        רשימה של נתיבי קבצי ה-trace
    """
    trace_path = Path(trace_dir)
    if not trace_path.exists():
        return []
    
    return sorted(trace_path.glob("*.json"), key=os.path.getmtime, reverse=True)

def get_latest_trace(trace_dir="traces"):
    """
    מחזיר את קובץ ה-trace האחרון שנוצר.
    
    Args:
        trace_dir: שם התיקייה (ברירת מחדל: "traces")
    
    Returns:
        נתיב לקובץ ה-trace האחרון, או None אם אין קבצים
    """
    traces = list_traces(trace_dir)
    return traces[0] if traces else None
