# -*- coding: utf-8 -*-
"""وظائف مساعدة لخدمة عداد الزوار"""

import re
from typing import Optional
from datetime import datetime
import constants

def detect_device_type(user_agent: str) -> str:
    """تحديد نوع الجهاز من User Agent"""
    if not user_agent:
        return 'unknown'
    
    user_agent = user_agent.lower()
    
    # تحديد الهاتف المحمول
    mobile_patterns = [
        r'mobile', r'android', r'iphone', r'ipod', 
        r'blackberry', r'windows phone', r'opera mini'
    ]
    
    for pattern in mobile_patterns:
        if re.search(pattern, user_agent):
            return 'mobile'
    
    # تحديد الجهاز اللوحي
    tablet_patterns = [r'tablet', r'ipad', r'kindle', r'silk']
    
    for pattern in tablet_patterns:
        if re.search(pattern, user_agent):
            return 'tablet'
    
    # افتراضياً حاسوب مكتبي
    return 'desktop'

def detect_browser(user_agent: str) -> str:
    """تحديد المتصفح من User Agent"""
    if not user_agent:
        return 'other'
    
    user_agent = user_agent.lower()
    
    # ترتيب مهم: Chrome يجب أن يأتي قبل Safari لأن Chrome يحتوي على "safari" في user agent
    if 'edg' in user_agent or 'edge' in user_agent:
        return 'edge'
    elif 'chrome' in user_agent and 'chromium' not in user_agent:
        return 'chrome'
    elif 'firefox' in user_agent:
        return 'firefox'
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        return 'safari'
    elif 'opera' in user_agent or 'opr' in user_agent:
        return 'opera'
    else:
        return 'other'

def get_browser_name(browser_code: str) -> str:
    """الحصول على اسم المتصفح بالعربية"""
    browser_map = {browser['browser']: browser['name'] for browser in constants.BROWSERS}
    return browser_map.get(browser_code, 'أخرى')

def get_device_name(device_code: str) -> str:
    """الحصول على اسم الجهاز بالعربية"""
    device_map = {device['type']: device['name'] for device in constants.DEVICE_TYPES}
    return device_map.get(device_code, 'غير محدد')

def get_page_name(page_code: str) -> str:
    """الحصول على اسم الصفحة بالعربية"""
    page_map = {page['page']: page['name'] for page in constants.TRACKED_PAGES}
    return page_map.get(page_code, 'صفحة غير محددة')

def is_valid_ip(ip_address: str) -> bool:
    """التحقق من صحة عنوان IP"""
    if not ip_address:
        return False
    
    # تحقق بسيط من صيغة IPv4
    parts = ip_address.split('.')
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except ValueError:
        return False

def is_bot_user_agent(user_agent: str) -> bool:
    """التحقق من كون User Agent خاص بـ bot"""
    if not user_agent:
        return False
    
    user_agent = user_agent.lower()
    
    bot_patterns = [
        r'bot', r'crawler', r'spider', r'scraper',
        r'googlebot', r'bingbot', r'facebookexternalhit',
        r'twitterbot', r'linkedinbot', r'whatsapp',
        r'telegram', r'curl', r'wget', r'python-requests'
    ]
    
    for pattern in bot_patterns:
        if re.search(pattern, user_agent):
            return True
    
    return False

def get_hour_period(hour: int) -> str:
    """تحديد فترة اليوم من الساعة"""
    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def get_hour_period_name(period: str) -> str:
    """الحصول على اسم فترة اليوم بالعربية"""
    period_map = {
        'morning': 'صباحاً',
        'afternoon': 'بعد الظهر',
        'evening': 'مساءً',
        'night': 'ليلاً'
    }
    return period_map.get(period, 'غير محدد')

def format_number(number: int) -> str:
    """تنسيق الأرقام بفواصل الآلاف"""
    return f"{number:,}"

def calculate_percentage(part: int, total: int) -> float:
    """حساب النسبة المئوية"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def get_time_greeting() -> str:
    """الحصول على تحية حسب الوقت"""
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "صباح الخير"
    elif 12 <= current_hour < 17:
        return "مساء الخير"
    elif 17 <= current_hour < 21:
        return "مساء الخير"
    else:
        return "مساء الخير"
