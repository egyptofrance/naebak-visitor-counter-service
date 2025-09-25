# -*- coding: utf-8 -*-
"""إعدادات خدمة عداد الزوار"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    """إعدادات التطبيق الأساسية"""
    
    # إعدادات Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'visitor-counter-secret-key')
    
    # إعدادات Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    
    # إعدادات الخدمة
    PORT = int(os.environ.get('PORT', 8006))
    
    # إعدادات العداد
    COUNT_UNIQUE_IPS = os.environ.get('COUNT_UNIQUE_IPS', 'true').lower() == 'true'
    RESET_DAILY = os.environ.get('RESET_DAILY', 'true').lower() == 'true'
    BACKUP_INTERVAL_HOURS = int(os.environ.get('BACKUP_INTERVAL_HOURS', 1))
    MAX_VISITORS_PER_IP = int(os.environ.get('MAX_VISITORS_PER_IP', 10))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))
