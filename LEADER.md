# 🔢 LEADER - دليل خدمة عداد الزوار البسيط

**اسم الخدمة:** naebak-visitor-counter-service  
**المنفذ:** 8006  
**الإطار:** Flask 2.3  
**قاعدة البيانات:** Redis (للإعدادات البسيطة)  
**الجدولة:** APScheduler (للتحديث كل 30 ثانية)  

---

## 📋 **نظرة عامة على الخدمة**

### **🎯 الغرض الأساسي:**
خدمة عداد الزوار هي **عداد بسيط جداً** يظهر في هيدر الموقع لعرض "عدد الزوار الحاليين" كرقم ديناميكي يتغير تلقائياً كل 30 ثانية.

### **🔧 آلية العمل:**
1. **الأدمن يحدد رقمين** (حد أدنى وحد أقصى) من لوحة التحكم
2. **كل 30 ثانية** يتم اختيار رقم عشوائي بين هذين الرقمين
3. **العداد يعرض الرقم** في هيدر الموقع كـ "الزوار الحاليين: 1,247"
4. **التحديث تلقائي** بدون تدخل المستخدم

### **📊 المثال:**
- الأدمن يضع: **الحد الأدنى = 800، الحد الأقصى = 2500**
- العداد يعرض كل 30 ثانية رقم عشوائي مثل: 1,247 → 1,892 → 1,156 → 2,034

---

## 🌐 **دور الخدمة في منصة نائبك**

### **🏛️ المكانة في النظام:**
خدمة بسيطة تعمل في الخلفية لتوفير **انطباع بالحيوية والنشاط** على الموقع من خلال عرض عداد متحرك في الهيدر.

### **📡 العلاقات مع الخدمات الأخرى:**

#### **🔗 الخدمات المتفاعلة:**
- **الواجهة الأمامية (3000)** - عرض العداد في الهيدر
- **خدمة الإدارة (8002)** - تحديد الحد الأدنى والأقصى للعداد

#### **🔄 تدفق البيانات:**
```
Admin Panel (8002) → تحديد الحدود → Visitor Counter (8006)
                                            ↓
Frontend (3000) ← عرض الرقم الحالي ← تحديث كل 30 ثانية
```

---

## 📦 **البيانات والنماذج من المستودع المخزن**

### **⚙️ إعدادات العداد:**
```python
COUNTER_SETTINGS = {
    'min_visitors': 500,        # الحد الأدنى (افتراضي)
    'max_visitors': 3000,       # الحد الأقصى (افتراضي)
    'update_interval': 30,      # التحديث كل 30 ثانية
    'display_format': '{:,}',   # تنسيق العرض (1,247)
    'enabled': True             # تفعيل/إلغاء العداد
}
```

### **🎛️ إعدادات الأدمن:**
```python
ADMIN_CONTROLS = [
    {
        "setting": "min_visitors",
        "name": "الحد الأدنى للزوار",
        "type": "number",
        "min": 1,
        "max": 10000,
        "default": 500
    },
    {
        "setting": "max_visitors", 
        "name": "الحد الأقصى للزوار",
        "type": "number",
        "min": 100,
        "max": 50000,
        "default": 3000
    },
    {
        "setting": "update_interval",
        "name": "فترة التحديث (ثانية)",
        "type": "number",
        "min": 10,
        "max": 300,
        "default": 30
    },
    {
        "setting": "enabled",
        "name": "تفعيل العداد",
        "type": "boolean",
        "default": True
    }
]
```

---

## ⚙️ **إعدادات Google Cloud Run**

### **🛠️ بيئة التطوير (Development):**
```yaml
service_name: naebak-visitor-counter-service-dev
image: gcr.io/naebak-472518/visitor-counter-service:dev
cpu: 0.1
memory: 64Mi
min_instances: 0
max_instances: 1
concurrency: 100
timeout: 300s

environment_variables:
  - FLASK_ENV=development
  - DEBUG=true
  - REDIS_URL=redis://localhost:6379/6
  - DEFAULT_MIN_VISITORS=100
  - DEFAULT_MAX_VISITORS=500
  - UPDATE_INTERVAL=30
```

### **🏭 إعدادات بيئة الإنتاج:**
```yaml
service_name: naebak-visitor-counter-service
image: gcr.io/naebak-472518/visitor-counter-service:latest
cpu: 0.1
memory: 64Mi
min_instances: 1
max_instances: 2
concurrency: 500
timeout: 30s

environment_variables:
  - FLASK_ENV=production
  - DEBUG=false
  - REDIS_URL=${REDIS_URL}
  - DEFAULT_MIN_VISITORS=500
  - DEFAULT_MAX_VISITORS=3000
  - UPDATE_INTERVAL=30
```

---

## 🔗 **واجهات برمجة التطبيقات (APIs)**

### **📡 نقاط النهاية البسيطة:**
```
GET  /health                           - فحص صحة الخدمة
GET  /api/counter/current              - الرقم الحالي للعداد
GET  /api/counter/settings             - إعدادات العداد الحالية
PUT  /api/counter/settings             - تحديث إعدادات العداد (أدمن فقط)
POST /api/counter/reset                - إعادة تعيين العداد (أدمن فقط)
```

### **📤 مثال استجابة الرقم الحالي:**
```json
GET /api/counter/current

{
  "status": "success",
  "data": {
    "current_count": 1247,
    "formatted": "1,247",
    "last_updated": "2025-01-01T12:00:30Z",
    "next_update": "2025-01-01T12:01:00Z"
  }
}
```

### **📥 مثال تحديث الإعدادات:**
```json
PUT /api/counter/settings
Content-Type: application/json
Authorization: Bearer <admin_token>

{
  "min_visitors": 800,
  "max_visitors": 2500,
  "update_interval": 30,
  "enabled": true
}
```

### **📤 مثال استجابة الإعدادات:**
```json
GET /api/counter/settings

{
  "status": "success",
  "data": {
    "min_visitors": 800,
    "max_visitors": 2500,
    "update_interval": 30,
    "enabled": true,
    "last_modified": "2025-01-01T10:30:00Z",
    "modified_by": "admin@naebak.com"
  }
}
```

---

## 🔐 **الأمان والصلاحيات**

### **🛡️ مستويات الوصول:**
1. **عام** - عرض الرقم الحالي فقط
2. **أدمن** - تحديث الإعدادات وإعادة التعيين

### **🔒 آليات الحماية:**
- **JWT Authentication** لتحديث الإعدادات
- **Rate Limiting** - 100 طلب/دقيقة للعرض العام
- **Input Validation** - التحقق من صحة الأرقام المدخلة
- **CORS Protection** - حماية من الطلبات الخارجية

---

## 📊 **المتغيرات والثوابت الأساسية**

### **🔢 إعدادات Redis:**
```python
REDIS_KEYS = {
    'current_count': 'visitor_counter:current',
    'settings': 'visitor_counter:settings',
    'last_update': 'visitor_counter:last_update'
}

REDIS_SETTINGS = {
    'connection_pool_size': 5,
    'socket_timeout': 3,
    'retry_on_timeout': True
}
```

### **⏰ إعدادات الجدولة:**
```python
SCHEDULER_CONFIG = {
    'job_id': 'update_visitor_count',
    'trigger': 'interval',
    'seconds': 30,
    'max_instances': 1,
    'coalesce': True
}
```

---

## 🔄 **الفروق بين بيئات التشغيل**

### **🛠️ بيئة التطوير (Development):**
- **الحد الافتراضي:** 100-500 زائر
- **الموارد:** 0.1 CPU, 64Mi Memory (خفيف جداً)
- **التسجيل:** مفصل للتتبع

### **🏭 بيئة الإنتاج (Production):**
- **الحد الافتراضي:** 500-3000 زائر
- **الموارد:** 0.1 CPU, 64Mi Memory (محسن)
- **التسجيل:** أخطاء فقط

---

## 🚀 **خطوات التطوير المطلوبة**

### **🎯 المرحلة الأولى - الأساسيات:**
1. ✅ إعداد البنية الأساسية
2. ⏳ تطبيق مولد الأرقام العشوائية
3. ⏳ ربط Redis لحفظ الإعدادات
4. ⏳ تطبيق الجدولة التلقائية (كل 30 ثانية)
5. ⏳ إنشاء APIs البسيطة

### **🎯 المرحلة الثانية - لوحة التحكم:**
1. ⏳ ربط خدمة الإدارة
2. ⏳ تطبيق واجهة تحديث الإعدادات
3. ⏳ إضافة التحقق من الصلاحيات
4. ⏳ اختبار التكامل مع الواجهة الأمامية

### **🎯 المرحلة الثالثة - التحسين:**
1. ⏳ تحسين الأداء
2. ⏳ إضافة المراقبة
3. ⏳ نشر بيئة الإنتاج

---

## 📚 **الموارد والمراجع**

### **🔧 أدوات التطوير:**
- **Flask 2.3** - إطار العمل الأساسي
- **Redis** - حفظ الإعدادات والرقم الحالي
- **APScheduler** - الجدولة التلقائية كل 30 ثانية
- **Random** - مولد الأرقام العشوائية

---

**📝 ملاحظة:** هذا عداد بسيط جداً - مجرد رقم عشوائي يتغير كل 30 ثانية بين حدين يحددهما الأدمن.
