#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
סקריפט להרצת בדיקות עבור סוכני WooCommerce AI
הסקריפט מאפשר הרצה של כל או חלק מהבדיקות עם אפשרויות שונות
"""

import sys
import os
import glob
import argparse
import pytest

def setup_arg_parser():
    """
    הגדרת פרסר ארגומנטים לקבלת פרמטרים מהמשתמש
    """
    parser = argparse.ArgumentParser(description='הרצת בדיקות לסוכני WooCommerce AI')
    
    parser.add_argument(
        '--agent', '-a',
        choices=['all', 'main', 'product', 'order', 'category', 'coupon', 'customer', 'report', 'settings'],
        default='all',
        help='הסוכן עבורו יש להריץ בדיקות (ברירת מחדל: הכל)'
    )
    
    parser.add_argument(
        '--e2e',
        action='store_true',
        help='הרץ בדיקות קצה-לקצה במקום בדיקות יחידה'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='הצג פלט מפורט יותר'
    )
    
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='הצג רק את הבדיקות שיורצו מבלי להריץ אותן'
    )
    
    parser.add_argument(
        '--no-cleanup',
        action='store_true',
        help='אל תנקה נתוני בדיקה אחרי ריצה'
    )
    
    parser.add_argument(
        '--failfast',
        action='store_true',
        help='עצור את הריצה אחרי הכישלון הראשון'
    )
    
    parser.add_argument(
        '--markers',
        action='store_true',
        help='הצג את כל הסימונים הזמינים בטסטים'
    )
    
    return parser

def run_tests(args):
    """
    הרצת הבדיקות לפי הארגומנטים שהתקבלו
    """
    pytest_args = []
    
    # הוספת מצב מפורט אם נדרש
    if args.verbose:
        pytest_args.append('-v')
    
    # הגדרת עצירה בכישלון ראשון
    if args.failfast:
        pytest_args.append('-xvs')
    
    # הגדרת הצגת מרקרים בלבד
    if args.markers:
        pytest_args.append('--markers')
        return pytest.main(pytest_args)
    
    # הגדרת הצגת בדיקות בלבד בלי ריצה
    if args.collect_only:
        pytest_args.append('--collect-only')
    
    # הגדרת מערכת לניקוי אחרי הבדיקות
    if args.no_cleanup:
        os.environ['NO_CLEANUP'] = '1'
    else:
        os.environ.pop('NO_CLEANUP', None)
    
    # מציאת קבצי בדיקה
    tests_dir = os.path.join(os.getcwd(), 'tests')
    
    # בדיקה האם להריץ בדיקות E2E
    if args.e2e:
        test_files = [os.path.join(tests_dir, 'test_e2e.py')]
        print(f"מריץ בדיקות קצה-לקצה (E2E)...")
    elif args.agent == 'all':
        test_pattern = os.path.join(tests_dir, 'test_*_agent.py')
        test_files = glob.glob(test_pattern)
    else:
        test_files = [os.path.join(tests_dir, f'test_{args.agent}_agent.py')]
        if not os.path.exists(test_files[0]):
            print(f"שגיאה: קובץ בדיקה {test_files[0]} לא נמצא")
            return 1
    
    # הדפסת רשימת קבצי הבדיקה שנמצאו
    print(f"קבצי בדיקה שנמצאו:")
    for test_file in test_files:
        print(f"  - {os.path.basename(test_file)}")
    
    # הוספת קבצי הבדיקה לפקודה
    pytest_args.extend(test_files)
    
    # הדפסת פקודת הרצה
    command = f"pytest {' '.join(pytest_args)}"
    print(f"מריץ: {command}")
    
    # הרצת הבדיקות
    return pytest.main(pytest_args)

def main():
    """
    פונקציה ראשית
    """
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    print(f"== מערכת בדיקות סוכני WooCommerce AI ==")
    
    # בדיקה שאנחנו בתיקייה נכונה (שיש תיקיית tests)
    if not os.path.isdir('tests'):
        print("שגיאה: לא נמצאה תיקיית 'tests'")
        print("וודא כי אתה מריץ את הסקריפט מתיקיית הפרויקט הראשית")
        return 1
    
    # בדיקה שיש קובץ .env עם הגדרות
    if not os.path.isfile('.env') and not os.path.isfile('.env.example'):
        print("אזהרה: לא נמצא קובץ .env")
        print("ייתכן שהבדיקות ייכשלו אם לא הוגדרו משתני סביבה נדרשים")
    
    # הרצת הבדיקות
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main()) 