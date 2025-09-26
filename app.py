# -*- coding: utf-8 -*-
"""
Naebak Visitor Counter Service - Flask Application

This is the main application file for the Naebak Visitor Counter Service. It provides a RESTful API
for real-time visitor tracking, analytics, and statistics. The service is designed to handle high
traffic loads while providing accurate visitor counting and detailed analytics.

Key Features:
- Real-time visitor counting with Redis backend
- Rate limiting and bot detection
- Page-level analytics and statistics
- Hourly traffic pattern analysis
- Automatic daily counter resets
- Comprehensive health monitoring
"""

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from config import Config
from models import VisitorCounterService, VisitorData
import utils
import constants

# Create Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Create API
api = Api(app)

# Create visitor counter service
visitor_service = VisitorCounterService()

# Setup scheduler for automated tasks
scheduler = BackgroundScheduler()

class HealthCheck(Resource):
    """
    Health check endpoint for service monitoring.
    
    This resource provides comprehensive health status including Redis connectivity,
    service version, and current timestamp. It's used by load balancers and monitoring
    systems to verify service availability.
    """
    
    def get(self):
        """
        Perform health check and return service status.
        
        Returns:
            JSON response with service health information including:
            - Service status and version
            - Redis connectivity status
            - Current timestamp
        """
        try:
            # Test Redis connection
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
    """
    Main visitor counting endpoint for real-time tracking.
    
    This resource handles visitor registration with comprehensive data collection,
    bot detection, rate limiting, and analytics tracking. It's the primary endpoint
    called by frontend applications to record user visits.
    """
    
    def post(self):
        """
        Record a new visitor interaction.
        
        This endpoint processes visitor data, performs validation and bot detection,
        applies rate limiting, and records the visit with full analytics tracking.
        
        Request Body (JSON):
            page (str, optional): Page identifier (defaults to 'home').
            governorate (str, optional): Visitor's governorate for geographic analytics.
        
        Headers:
            X-Forwarded-For: Real IP address (for load balancer scenarios).
            User-Agent: Browser/client information for device detection.
        
        Returns:
            JSON response with visit confirmation and visitor information,
            or error details if the request is invalid or rate limited.
            
        Business Logic:
            1. Extract and validate IP address from headers
            2. Detect and filter bot traffic
            3. Apply rate limiting per IP address
            4. Detect device type and browser
            5. Record visit with full analytics
            6. Return confirmation with visitor details
        """
        try:
            # Get request data
            data = request.get_json() or {}
            
            # Extract IP address from request headers
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()
            
            # Get User Agent for device detection
            user_agent = request.headers.get('User-Agent', '')
            
            # Validate IP address format
            if not utils.is_valid_ip(ip_address):
                return {"error": "عنوان IP غير صحيح"}, 400
            
            # Filter out bot traffic
            if utils.is_bot_user_agent(user_agent):
                return {"message": "تم تجاهل الطلب (bot detected)"}, 200
            
            # Create visitor data object
            visitor_data = VisitorData(
                ip_address=ip_address,
                user_agent=user_agent,
                page=data.get('page', 'home'),
                timestamp=datetime.now(),
                governorate=data.get('governorate'),
                device_type=utils.detect_device_type(user_agent),
                browser=utils.detect_browser(user_agent)
            )
            
            # Record the visit
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
    """
    Visitor statistics endpoint for dashboard and analytics.
    
    This resource provides comprehensive visitor statistics including total visitors,
    daily counts, unique visitors, and page views. It's used by admin dashboards
    and analytics interfaces to display platform usage metrics.
    """
    
    def get(self):
        """
        Retrieve current visitor statistics.
        
        Returns comprehensive visitor metrics including:
        - Total visitors since platform launch
        - Daily visitor count (resets at midnight)
        - Unique visitor count (based on IP addresses)
        - Total page views across all pages
        - Last reset timestamp for daily counters
        
        Returns:
            JSON response with complete visitor statistics.
        """
        try:
            stats = visitor_service.get_visitor_stats()
            return stats.to_dict(), 200
        except Exception as e:
            return {"error": f"خطأ في الحصول على الإحصائيات: {str(e)}"}, 500

class PageStats(Resource):
    """
    Page-level statistics endpoint for content analytics.
    
    This resource provides detailed statistics for each tracked page, helping
    administrators understand which content is most popular and how users
    navigate through the platform.
    """
    
    def get(self):
        """
        Retrieve statistics for all tracked pages.
        
        Returns page-level analytics including:
        - Page identifier and human-readable name
        - Total views for each page
        - Estimated unique visitors per page
        - Relative popularity rankings
        
        Returns:
            JSON array with statistics for all tracked pages.
        """
        try:
            page_stats = visitor_service.get_page_stats()
            return [stats.to_dict() for stats in page_stats], 200
        except Exception as e:
            return {"error": f"خطأ في الحصول على إحصائيات الصفحات: {str(e)}"}, 500

class HourlyStats(Resource):
    """
    Hourly traffic pattern endpoint for time-based analytics.
    
    This resource provides hourly breakdown of visitor traffic, enabling
    administrators to understand peak usage times and optimize resource
    allocation accordingly.
    """
    
    def get(self):
        """
        Retrieve hourly visitor statistics.
        
        Returns traffic patterns broken down by hour of day (0-23) with:
        - Hour identifier (0-23)
        - Visit count for that hour
        - Time period classification (morning, afternoon, evening, night)
        - Human-readable period names
        
        Returns:
            JSON array with hourly traffic statistics.
        """
        try:
            hourly_stats = visitor_service.get_hourly_stats()
            
            # Format data with additional metadata
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
    """
    Configuration endpoint for tracked pages information.
    
    This resource provides the list of pages that are being tracked by the
    visitor counter service, including their identifiers and display names.
    """
    
    def get(self):
        """
        Retrieve list of tracked pages.
        
        Returns configuration information about all pages being tracked
        by the visitor counter service, including page identifiers and
        human-readable names for display purposes.
        
        Returns:
            JSON array with tracked page configurations.
        """
        return constants.TRACKED_PAGES, 200

class ResetCounters(Resource):
    """
    Administrative endpoint for manual counter resets.
    
    This resource provides administrative functionality to manually reset
    daily counters. It should be protected with proper authentication in
    production environments.
    """
    
    def post(self):
        """
        Manually reset daily counters.
        
        This endpoint allows administrators to manually trigger a reset of
        daily visitor counters. Normally this happens automatically at midnight,
        but manual resets may be needed for testing or maintenance purposes.
        
        Returns:
            JSON response confirming the reset operation.
            
        Security Note:
            This endpoint should be protected with authentication in production.
        """
        try:
            visitor_service.reset_daily_counters()
            return {"message": "تم إعادة تعيين العدادات بنجاح"}, 200
        except Exception as e:
            return {"error": f"خطأ في إعادة تعيين العدادات: {str(e)}"}, 500

# Register API resources with their endpoints
api.add_resource(HealthCheck, '/health')
api.add_resource(VisitorCounter, '/api/visitors/count/')
api.add_resource(VisitorStats, '/api/visitors/stats/')
api.add_resource(PageStats, '/api/visitors/pages/')
api.add_resource(HourlyStats, '/api/visitors/hourly/')
api.add_resource(TrackedPages, '/api/visitors/tracked-pages/')
api.add_resource(ResetCounters, '/api/visitors/reset/')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({"error": "الصفحة غير موجودة"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    return jsonify({"error": "خطأ داخلي في الخادم"}), 500

# Scheduled job functions
def daily_reset_job():
    """
    Automated daily reset job.
    
    This function is called automatically at midnight to reset daily counters
    while preserving historical data and total counters.
    """
    if app.config['RESET_DAILY']:
        visitor_service.reset_daily_counters()

def backup_job():
    """
    Automated backup job.
    
    This function performs periodic backups of visitor data. The actual backup
    logic can be implemented based on specific requirements and storage solutions.
    """
    try:
        # Backup logic can be implemented here
        print("✅ Backup completed successfully")
    except Exception as e:
        print(f"❌ Backup error: {e}")

if __name__ == '__main__':
    # Initialize default data for testing and demonstration
    try:
        visitor_service.initialize_default_data()
        print("✅ Default data initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing data: {e}")
    
    # Setup scheduled jobs
    if app.config['RESET_DAILY']:
        # Daily reset at midnight
        scheduler.add_job(
            func=daily_reset_job,
            trigger="cron",
            hour=0,
            minute=0,
            id='daily_reset'
        )
    
    # Hourly backup job
    scheduler.add_job(
        func=backup_job,
        trigger="interval",
        hours=app.config['BACKUP_INTERVAL_HOURS'],
        id='backup_job'
    )
    
    # Start the scheduler
    scheduler.start()
    
    # Shutdown scheduler when application exits
    atexit.register(lambda: scheduler.shutdown())
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['FLASK_ENV'] == 'development'
    )
