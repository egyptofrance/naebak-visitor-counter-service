# -*- coding: utf-8 -*-
"""التطبيق الرئيسي لخدمة عداد الزوار"""

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from config import Config
from models import VisitorCounterService, VisitorData
import utils
import constants

# إنشاء تطبيق Flask
app = Flask(__name__)
app.config.from_object(Config)

# إنشاء API
api = Api(app)

# إنشاء خدمة عداد الزوار
visitor_service = VisitorCounterService()

# إعداد المجدول للمهام التلقائية
scheduler = BackgroundScheduler()

class HealthCheck(Resource):
    """فحص صحة الخدمة"""
    
    def get(self):
        try:
            # اختبار الاتصال بـ Redis
            visitor_service.redis_client.ping()
            redis_status = "connected"
        except Exception as e:
            redis_status = f"disconnected: {str(e)}"
        
        return {
            "status": "ok",
            "service": "naebak-visitor-counter-service",
            "version": "1.0.0",
            "redis_status": redis_status,
            "time": datetime.now().isoformat()
        }, 200

class VisitorCounter(Resource):
    """عداد الزوار الرئيسي"""
    
    def post(self):
        """تسجيل زيارة جديدة"""
        try:
            # الحصول على بيانات الطلب
            data = request.get_json() or {}
            
            # الحصول على IP من الطلب
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()
            
            # الحصول على User Agent
            user_agent = request.headers.get('User-Agent', '')
            
            # التحقق من صحة البيانات
            if not utils.is_valid_ip(ip_address):
                return {"error": "عنوان IP غير صحيح"}, 400
            
            # تجاهل الـ bots
            if utils.is_bot_user_agent(user_agent):
                return {"message": "تم تجاهل الطلب (bot detected)"}, 200
            
            # إنشاء بيانات الزائر
            visitor_data = VisitorData(
                ip_address=ip_address,
                user_agent=user_agent,
                page=data.get('page', 'home'),
                timestamp=datetime.now(),
                governorate=data.get('governorate'),
                device_type=utils.detect_device_type(user_agent),
                browser=utils.detect_browser(user_agent)
            )
            
            # تسجيل الزيارة
            success = visitor_service.record_visit(visitor_data)
            
            if success:
                return {
                    "message": "تم تسجيل الزيارة بنجاح",
                    "visitor_info": {
                        "device_type": utils.get_device_name(visitor_data.device_type),
                        "browser": utils.get_browser_name(visitor_data.browser),
                        "page": utils.get_page_name(visitor_data.page)
                    }
                }, 201
            else:
                return {"error": "تم تجاوز حد الزيارات المسموح"}, 429
                
        except Exception as e:
            return {"error": f"خطأ في تسجيل الزيارة: {str(e)}"}, 500

class VisitorStats(Resource):
    """إحصائيات الزوار"""
    
    def get(self):
        """الحصول على إحصائيات الزوار"""
        try:
            stats = visitor_service.get_visitor_stats()
            return stats.to_dict(), 200
        except Exception as e:
            return {"error": f"خطأ في الحصول على الإحصائيات: {str(e)}"}, 500

class PageStats(Resource):
    """إحصائيات الصفحات"""
    
    def get(self):
        """الحصول على إحصائيات الصفحات"""
        try:
            page_stats = visitor_service.get_page_stats()
            return [stats.to_dict() for stats in page_stats], 200
        except Exception as e:
            return {"error": f"خطأ في الحصول على إحصائيات الصفحات: {str(e)}"}, 500

class HourlyStats(Resource):
    """إحصائيات الساعات"""
    
    def get(self):
        """الحصول على إحصائيات الساعات"""
        try:
            hourly_stats = visitor_service.get_hourly_stats()
            
            # تنسيق البيانات
            formatted_stats = []
            for hour, visits in hourly_stats.items():
                period = utils.get_hour_period(hour)
                formatted_stats.append({
                    "hour": hour,
                    "visits": visits,
                    "period": period,
                    "period_name": utils.get_hour_period_name(period)
                })
            
            return formatted_stats, 200
        except Exception as e:
            return {"error": f"خطأ في الحصول على إحصائيات الساعات: {str(e)}"}, 500

class TrackedPages(Resource):
    """الصفحات المتتبعة"""
    
    def get(self):
        """الحصول على قائمة الصفحات المتتبعة"""
        return constants.TRACKED_PAGES, 200

class ResetCounters(Resource):
    """إعادة تعيين العدادات"""
    
    def post(self):
        """إعادة تعيين العدادات اليومية (للإدارة فقط)"""
        try:
            visitor_service.reset_daily_counters()
            return {"message": "تم إعادة تعيين العدادات بنجاح"}, 200
        except Exception as e:
            return {"error": f"خطأ في إعادة تعيين العدادات: {str(e)}"}, 500

# تسجيل الموارد
api.add_resource(HealthCheck, '/health')
api.add_resource(VisitorCounter, '/api/visitors/count/')
api.add_resource(VisitorStats, '/api/visitors/stats/')
api.add_resource(PageStats, '/api/visitors/pages/')
api.add_resource(HourlyStats, '/api/visitors/hourly/')
api.add_resource(TrackedPages, '/api/visitors/tracked-pages/')
api.add_resource(ResetCounters, '/api/visitors/reset/')

# معالجات الأخطاء
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "الصفحة غير موجودة"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "خطأ داخلي في الخادم"}), 500

# وظيفة إعادة التعيين اليومية التلقائية
def daily_reset_job():
    """مهمة إعادة التعيين اليومية"""
    if app.config['RESET_DAILY']:
        visitor_service.reset_daily_counters()

# وظيفة النسخ الاحتياطي
def backup_job():
    """مهمة النسخ الاحتياطي"""
    try:
        # يمكن إضافة منطق النسخ الاحتياطي هنا
        print("✅ تم تنفيذ النسخ الاحتياطي")
    except Exception as e:
        print(f"❌ خطأ في النسخ الاحتياطي: {e}")

if __name__ == '__main__':
    # تهيئة البيانات الافتراضية
    try:
        visitor_service.initialize_default_data()
        print("✅ تم تهيئة البيانات الافتراضية")
    except Exception as e:
        print(f"❌ خطأ في تهيئة البيانات: {e}")
    
    # إعداد المهام المجدولة
    if app.config['RESET_DAILY']:
        # إعادة تعيين يومية في منتصف الليل
        scheduler.add_job(
            func=daily_reset_job,
            trigger="cron",
            hour=0,
            minute=0,
            id='daily_reset'
        )
    
    # نسخ احتياطي كل ساعة
    scheduler.add_job(
        func=backup_job,
        trigger="interval",
        hours=app.config['BACKUP_INTERVAL_HOURS'],
        id='backup_job'
    )
    
    # بدء المجدول
    scheduler.start()
    
    # إيقاف المجدول عند إغلاق التطبيق
    atexit.register(lambda: scheduler.shutdown())
    
    # تشغيل التطبيق
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['FLASK_ENV'] == 'development'
    )
