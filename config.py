#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
קובץ תצורה למערכת AI Agents לניהול חנות WooCommerce
----------------------------------------------------

קובץ זה אחראי על טעינת הגדרות התצורה מקובץ JSON או מסביבת העבודה.
"""

import os
import json
from dotenv import load_dotenv

# טעינת משתני סביבה מקובץ .env
load_dotenv()

def load_config(config_file="config.json"):
    """טוען את הגדרות התצורה מקובץ JSON."""
    if not os.path.exists(config_file):
        # אם קובץ התצורה לא קיים, ננסה להשתמש במשתני סביבה
        return {
            "woocommerce": {
                "url": os.environ.get("WOO_URL"),
                "consumer_key": os.environ.get("WOO_CONSUMER_KEY"),
                "consumer_secret": os.environ.get("WOO_CONSUMER_SECRET")
            },
            "openai": {
                "api_key": os.environ.get("OPENAI_API_KEY")
            }
        }
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_woocommerce_config():
    """מחזיר את הגדרות ה-WooCommerce."""
    config = load_config()
    
    # בדיקה שכל ההגדרות הנדרשות קיימות
    required_keys = ["url", "consumer_key", "consumer_secret"]
    for key in required_keys:
        if key not in config.get("woocommerce", {}) or not config["woocommerce"][key]:
            raise ValueError(f"חסר {key} בהגדרות ה-WooCommerce")
    
    return config["woocommerce"]

def get_openai_config():
    """מחזיר את הגדרות ה-OpenAI."""
    config = load_config()
    
    # אם אין הגדרות ב-config, ננסה לקחת מסביבת העבודה
    if "openai" not in config or not config["openai"].get("api_key"):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("חסר OPENAI_API_KEY בהגדרות או בסביבת העבודה")
        
        return {"api_key": api_key}
    
    return config["openai"]
