#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
שרת פשוט למימוש ממשק משתמש לצ'אט בוט של Agent WooCommerce
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI
from agents.main_agent import MainAgent
from api.woocommerce_client import WooCommerceClient
from config import get_openai_config, get_woocommerce_config
import logging

# טעינת משתני הסביבה
load_dotenv()

# הגדרת השרת
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret-key-for-dev')

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# יצירת לקוח OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# יצירת לקוח WooCommerce
try:
    woo_config = get_woocommerce_config()
    logger.info(f"מנסה להתחבר לחנות WooCommerce בכתובת: {woo_config['url']}")
    logger.info(f"משתמש במפתח צרכן: {woo_config['consumer_key'][:4]}...{woo_config['consumer_key'][-4:] if len(woo_config['consumer_key']) > 8 else ''}")
    
    woo_client = WooCommerceClient(
        url=woo_config["url"],
        consumer_key=woo_config["consumer_key"],
        consumer_secret=woo_config["consumer_secret"]
    )
    
    # בדיקת חיבור באמצעות בקשת נתונים בסיסיים
    logger.info("בודק חיבור לחנות WooCommerce...")
    connection_test = woo_client.wcapi.get("").json()
    logger.info(f"תוצאת בדיקת חיבור: {connection_test}")
    
    # בדיקה אם יש מוצרים בחנות
    logger.info("בודק גישה למוצרים...")
    products_test = woo_client.get_products(per_page=1)
    logger.info(f"נמצאו מוצרים בחנות: {products_test is not None and len(products_test) > 0}")
    
    logger.info(f"התחברות לחנות WooCommerce הצליחה: {woo_config['url']}")
except Exception as e:
    logger.error(f"שגיאה מפורטת בהתחברות לחנות WooCommerce: {str(e)}")
    logger.error(f"סוג השגיאה: {type(e).__name__}")
    import traceback
    logger.error(f"מידע נוסף על השגיאה: {traceback.format_exc()}")
    logger.info("ממשיך ללא חיבור לחנות...")
    woo_client = None

# יצירת ה-MainAgent
agent = MainAgent(client, woo_client=woo_client)

@app.route('/')
def index():
    """מציג את דף הבית עם ממשק הצ'אט"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """מטפל בבקשות צ'אט"""
    try:
        # קבלת הודעת המשתמש
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'חסרה הודעה'}), 400
        
        logger.info(f"התקבלה הודעה: {user_message}")
        
        # שליחת ההודעה ל-Agent
        response = agent.run(user_message)
        
        return jsonify({
            'response': response
        })
    
    except Exception as e:
        logger.error(f"שגיאה בעת עיבוד הבקשה: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # יצירת תיקיית התבניות אם לא קיימת
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # הפעלת השרת
    app.run(debug=True) 