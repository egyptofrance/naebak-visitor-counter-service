# -*- coding: utf-8 -*-
"""ثوابت وبيانات أساسية لخدمة عداد الزوار"""

# مفاتيح Redis للعدادات
REDIS_KEYS = {
    'TOTAL_VISITORS': 'visitors:total',
    'DAILY_VISITORS': 'visitors:daily',
    'UNIQUE_IPS': 'visitors:unique_ips',
    'HOURLY_VISITORS': 'visitors:hourly',
    'PAGE_VIEWS': 'visitors:page_views',
    'LAST_RESET': 'visitors:last_reset',
    'VISITOR_IPS_SET': 'visitors:ips_set',
    'RATE_LIMIT_PREFIX': 'visitors:rate_limit:'
}

# أنواع الصفحات المتتبعة
TRACKED_PAGES = [
    {
        'page': 'home',
        'name': 'الصفحة الرئيسية',
        'name_en': 'Home Page',
        'path': '/',
        'description': 'الصفحة الرئيسية للمنصة'
    },
    {
        'page': 'candidates',
        'name': 'صفحة المرشحين',
        'name_en': 'Candidates Page',
        'path': '/candidates',
        'description': 'صفحة عرض المرشحين'
    },
    {
        'page': 'members',
        'name': 'صفحة الأعضاء',
        'name_en': 'Members Page',
        'path': '/members',
        'description': 'صفحة عرض أعضاء المجالس'
    },
    {
        'page': 'complaints',
        'name': 'صفحة الشكاوى',
        'name_en': 'Complaints Page',
        'path': '/complaints',
        'description': 'صفحة تقديم الشكاوى'
    },
    {
        'page': 'messages',
        'name': 'صفحة الرسائل',
        'name_en': 'Messages Page',
        'path': '/messages',
        'description': 'صفحة الرسائل'
    },
    {
        'page': 'about',
        'name': 'صفحة حول المنصة',
        'name_en': 'About Page',
        'path': '/about',
        'description': 'صفحة التعريف بالمنصة'
    },
    {
        'page': 'contact',
        'name': 'صفحة اتصل بنا',
        'name_en': 'Contact Page',
        'path': '/contact',
        'description': 'صفحة التواصل'
    }
]

# المحافظات المصرية (للإحصائيات الجغرافية)
GOVERNORATES = [
    {"name": "القاهرة", "name_en": "Cairo", "code": "CAI"},
    {"name": "الجيزة", "name_en": "Giza", "code": "GIZ"},
    {"name": "الإسكندرية", "name_en": "Alexandria", "code": "ALX"},
    {"name": "الدقهلية", "name_en": "Dakahlia", "code": "DAK"},
    {"name": "البحر الأحمر", "name_en": "Red Sea", "code": "RSS"},
    {"name": "البحيرة", "name_en": "Beheira", "code": "BEH"},
    {"name": "الفيوم", "name_en": "Fayoum", "code": "FAY"},
    {"name": "الغربية", "name_en": "Gharbia", "code": "GHR"},
    {"name": "الإسماعيلية", "name_en": "Ismailia", "code": "ISM"},
    {"name": "المنوفية", "name_en": "Monufia", "code": "MNF"},
    {"name": "المنيا", "name_en": "Minya", "code": "MNY"},
    {"name": "القليوبية", "name_en": "Qalyubia", "code": "QLY"},
    {"name": "الوادي الجديد", "name_en": "New Valley", "code": "WAD"},
    {"name": "شمال سيناء", "name_en": "North Sinai", "code": "NSI"},
    {"name": "جنوب سيناء", "name_en": "South Sinai", "code": "SSI"},
    {"name": "الشرقية", "name_en": "Sharqia", "code": "SHR"},
    {"name": "سوهاج", "name_en": "Sohag", "code": "SOH"},
    {"name": "السويس", "name_en": "Suez", "code": "SUZ"},
    {"name": "أسوان", "name_en": "Aswan", "code": "ASW"},
    {"name": "أسيوط", "name_en": "Asyut", "code": "ASY"},
    {"name": "بني سويف", "name_en": "Beni Suef", "code": "BNS"},
    {"name": "بورسعيد", "name_en": "Port Said", "code": "PTS"},
    {"name": "دمياط", "name_en": "Damietta", "code": "DAM"},
    {"name": "كفر الشيخ", "name_en": "Kafr El Sheikh", "code": "KFS"},
    {"name": "مطروح", "name_en": "Matrouh", "code": "MAT"},
    {"name": "الأقصر", "name_en": "Luxor", "code": "LUX"},
    {"name": "قنا", "name_en": "Qena", "code": "QEN"}
]

# أنواع الأجهزة (للإحصائيات)
DEVICE_TYPES = [
    {'type': 'desktop', 'name': 'حاسوب مكتبي', 'name_en': 'Desktop'},
    {'type': 'mobile', 'name': 'هاتف محمول', 'name_en': 'Mobile'},
    {'type': 'tablet', 'name': 'جهاز لوحي', 'name_en': 'Tablet'},
    {'type': 'unknown', 'name': 'غير محدد', 'name_en': 'Unknown'}
]

# المتصفحات الشائعة
BROWSERS = [
    {'browser': 'chrome', 'name': 'جوجل كروم', 'name_en': 'Google Chrome'},
    {'browser': 'firefox', 'name': 'فايرفوكس', 'name_en': 'Firefox'},
    {'browser': 'safari', 'name': 'سفاري', 'name_en': 'Safari'},
    {'browser': 'edge', 'name': 'مايكروسوفت إيدج', 'name_en': 'Microsoft Edge'},
    {'browser': 'opera', 'name': 'أوبرا', 'name_en': 'Opera'},
    {'browser': 'other', 'name': 'أخرى', 'name_en': 'Other'}
]

# أوقات الذروة (بالساعات)
PEAK_HOURS = [
    {'hour': 9, 'name': 'صباحاً', 'period': 'morning'},
    {'hour': 12, 'name': 'ظهراً', 'period': 'noon'},
    {'hour': 15, 'name': 'بعد الظهر', 'period': 'afternoon'},
    {'hour': 18, 'name': 'مساءً', 'period': 'evening'},
    {'hour': 21, 'name': 'ليلاً', 'period': 'night'}
]
