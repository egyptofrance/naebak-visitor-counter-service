# -*- coding: utf-8 -*-
"""نماذج البيانات الأساسية لخدمة عداد الزوار"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import redis
import json
from datetime import datetime, timedelta
from config import Config
import constants

# إعداد اتصال Redis
redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)

@dataclass
class VisitorData:
    """نموذج بيانات الزائر"""
    ip_address: str
    user_agent: str
    page: str
    timestamp: datetime
    governorate: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل البيانات إلى قاموس"""
        return {
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'page': self.page,
            'timestamp': self.timestamp.isoformat(),
            'governorate': self.governorate,
            'device_type': self.device_type,
            'browser': self.browser
        }

@dataclass
class VisitorStats:
    """إحصائيات الزوار"""
    total_visitors: int = 0
    daily_visitors: int = 0
    unique_visitors: int = 0
    page_views: int = 0
    last_reset: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل البيانات إلى قاموس"""
        return {
            'total_visitors': self.total_visitors,
            'daily_visitors': self.daily_visitors,
            'unique_visitors': self.unique_visitors,
            'page_views': self.page_views,
            'last_reset': self.last_reset.isoformat() if self.last_reset else None
        }

@dataclass
class PageStats:
    """إحصائيات الصفحات"""
    page: str
    page_name: str
    views: int = 0
    unique_visitors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل البيانات إلى قاموس"""
        return {
            'page': self.page,
            'page_name': self.page_name,
            'views': self.views,
            'unique_visitors': self.unique_visitors
        }

class VisitorCounterService:
    """خدمة عداد الزوار"""
    
    def __init__(self):
        self.redis_client = redis_client
        self.config = Config
    
    def record_visit(self, visitor_data: VisitorData) -> bool:
        """تسجيل زيارة جديدة"""
        try:
            # التحقق من Rate Limiting
            if not self._check_rate_limit(visitor_data.ip_address):
                return False
            
            # زيادة العداد الإجمالي
            self.redis_client.incr(constants.REDIS_KEYS['TOTAL_VISITORS'])
            
            # زيادة العداد اليومي
            self.redis_client.incr(constants.REDIS_KEYS['DAILY_VISITORS'])
            
            # زيادة عداد مشاهدات الصفحة
            self.redis_client.incr(constants.REDIS_KEYS['PAGE_VIEWS'])
            
            # تسجيل الزيارة للصفحة المحددة
            page_key = f"visitors:page:{visitor_data.page}"
            self.redis_client.incr(page_key)
            
            # إضافة IP للمجموعة إذا كان فريداً
            if self.config.COUNT_UNIQUE_IPS:
                ip_added = self.redis_client.sadd(constants.REDIS_KEYS['VISITOR_IPS_SET'], visitor_data.ip_address)
                if ip_added:
                    self.redis_client.incr(constants.REDIS_KEYS['UNIQUE_IPS'])
            
            # حفظ تفاصيل الزيارة
            self._save_visit_details(visitor_data)
            
            return True
            
        except Exception as e:
            print(f"خطأ في تسجيل الزيارة: {e}")
            return False
    
    def get_visitor_stats(self) -> VisitorStats:
        """الحصول على إحصائيات الزوار"""
        stats = VisitorStats()
        
        stats.total_visitors = int(self.redis_client.get(constants.REDIS_KEYS['TOTAL_VISITORS']) or 0)
        stats.daily_visitors = int(self.redis_client.get(constants.REDIS_KEYS['DAILY_VISITORS']) or 0)
        stats.unique_visitors = int(self.redis_client.get(constants.REDIS_KEYS['UNIQUE_IPS']) or 0)
        stats.page_views = int(self.redis_client.get(constants.REDIS_KEYS['PAGE_VIEWS']) or 0)
        
        # الحصول على تاريخ آخر إعادة تعيين
        last_reset_str = self.redis_client.get(constants.REDIS_KEYS['LAST_RESET'])
        if last_reset_str:
            stats.last_reset = datetime.fromisoformat(last_reset_str)
        
        return stats
    
    def get_page_stats(self) -> List[PageStats]:
        """الحصول على إحصائيات الصفحات"""
        page_stats = []
        
        for page_info in constants.TRACKED_PAGES:
            page_key = f"visitors:page:{page_info['page']}"
            views = int(self.redis_client.get(page_key) or 0)
            
            # حساب الزوار الفريدين للصفحة (تقدير)
            unique_visitors = max(1, views // 3) if views > 0 else 0
            
            stats = PageStats(
                page=page_info['page'],
                page_name=page_info['name'],
                views=views,
                unique_visitors=unique_visitors
            )
            page_stats.append(stats)
        
        return page_stats
    
    def get_hourly_stats(self) -> Dict[int, int]:
        """الحصول على إحصائيات الساعات"""
        hourly_stats = {}
        
        for hour in range(24):
            hour_key = f"visitors:hour:{hour}"
            visits = int(self.redis_client.get(hour_key) or 0)
            hourly_stats[hour] = visits
        
        return hourly_stats
    
    def reset_daily_counters(self):
        """إعادة تعيين العدادات اليومية"""
        try:
            # إعادة تعيين العداد اليومي
            self.redis_client.set(constants.REDIS_KEYS['DAILY_VISITORS'], 0)
            
            # إعادة تعيين مجموعة IPs اليومية
            daily_ips_key = f"{constants.REDIS_KEYS['VISITOR_IPS_SET']}:daily"
            self.redis_client.delete(daily_ips_key)
            
            # حفظ تاريخ آخر إعادة تعيين
            self.redis_client.set(constants.REDIS_KEYS['LAST_RESET'], datetime.now().isoformat())
            
            print("✅ تم إعادة تعيين العدادات اليومية")
            
        except Exception as e:
            print(f"❌ خطأ في إعادة تعيين العدادات: {e}")
    
    def _check_rate_limit(self, ip_address: str) -> bool:
        """التحقق من حد المعدل للـ IP"""
        if not self.config.MAX_VISITORS_PER_IP:
            return True
        
        rate_limit_key = f"{constants.REDIS_KEYS['RATE_LIMIT_PREFIX']}{ip_address}"
        current_count = self.redis_client.get(rate_limit_key)
        
        if current_count and int(current_count) >= self.config.MAX_VISITORS_PER_IP:
            return False
        
        # زيادة العداد وتعيين انتهاء الصلاحية
        pipe = self.redis_client.pipeline()
        pipe.incr(rate_limit_key)
        pipe.expire(rate_limit_key, self.config.RATE_LIMIT_WINDOW)
        pipe.execute()
        
        return True
    
    def _save_visit_details(self, visitor_data: VisitorData):
        """حفظ تفاصيل الزيارة"""
        try:
            # حفظ تفاصيل الزيارة في قائمة
            visit_key = f"visitors:details:{datetime.now().strftime('%Y-%m-%d')}"
            visit_json = json.dumps(visitor_data.to_dict())
            
            # إضافة للقائمة مع الحفاظ على آخر 1000 زيارة فقط
            self.redis_client.lpush(visit_key, visit_json)
            self.redis_client.ltrim(visit_key, 0, 999)
            
            # تعيين انتهاء صلاحية للبيانات (7 أيام)
            self.redis_client.expire(visit_key, 7 * 24 * 3600)
            
        except Exception as e:
            print(f"خطأ في حفظ تفاصيل الزيارة: {e}")
    
    def initialize_default_data(self):
        """تهيئة البيانات الافتراضية للاختبار"""
        default_values = {
            constants.REDIS_KEYS['TOTAL_VISITORS']: 15000,
            constants.REDIS_KEYS['DAILY_VISITORS']: 450,
            constants.REDIS_KEYS['UNIQUE_IPS']: 8500,
            constants.REDIS_KEYS['PAGE_VIEWS']: 25000,
            constants.REDIS_KEYS['LAST_RESET']: datetime.now().isoformat()
        }
        
        for key, value in default_values.items():
            if not self.redis_client.exists(key):
                self.redis_client.set(key, value)
        
        # تهيئة إحصائيات الصفحات
        page_views = [1200, 800, 600, 950, 750, 400, 300]
        for i, page_info in enumerate(constants.TRACKED_PAGES):
            page_key = f"visitors:page:{page_info['page']}"
            if not self.redis_client.exists(page_key):
                views = page_views[i] if i < len(page_views) else 100
                self.redis_client.set(page_key, views)
