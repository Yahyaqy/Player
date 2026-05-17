from http.server import BaseHTTPRequestHandler
import requests
import re
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. تحليل الرابط القادم لاستخراج رابط صفحة فيلم موقع أهواك
        query_components = parse_qs(urlparse(self.path).query)
        
        # إذا لم يقم المستخدم بتمرير رابط الفيلم بعد علامة ?url=
        if 'url' not in query_components:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("خطأ: يرجى إضافة رابط صفحة الفيلم. مثال:\n?url=https://yam.ahwaktv.net/...".encode('utf-8'))
            return
            
        target_url = query_components['url'][0]
        
        # إرسال ترويسة (Headers) متوافقة مع سيرفر أهواك لمنع الحظر
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Referer": "https://ahwaktv.net/"
        }
        
        try:
            # 2. قراءة كود صفحة المشغل برمجياً في الخلفية
            response = requests.get(target_url, headers=headers, timeout=10)
            html = response.text
            
            # 3. قنص رابط الـ m3u8 الحي بالتوكن الجديد (الخاص بسيرفر 1vid أو السيرفرات المشابهة)
            match = re.search(r'https://[^\s"\']+\.m3u8[^\s"\']*', html)
            
            if match:
                video_direct_url = match.group(0)
                
                # 4. توجيه المشغل الخارجي فوراً لرابط الفيديو المباشر المستخرج
                self.send_response(302)
                self.send_header('Location', video_direct_url)
                self.send_header('Access-Control-Allow-Origin', '*') # لضمان عمله على كافة التطبيقات دون قيود
                self.end_headers()
                return
            else:
                # في حال لم يجد السكريبت رابط البث داخل الصفحة
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("عذراً، لم يتم العثور على رابط m3u8 نشط في هذه الصفحة.".encode('utf-8'))
                return
        except:
            # في حال حدوث مشكلة في الاتصال بالسيرفر الأصلي
            self.send_response(500)
            self.end_headers()
            return
