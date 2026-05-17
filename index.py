from http.server import BaseHTTPRequestHandler
import requests
import re
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        
        if 'url' not in query_components:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("خطأ: يرجى إضافة رابط صفحة الفيلم من موقع أهواك.".encode('utf-8'))
            return
            
        target_url = query_components['url'][0]
        
        # استخراج الـ vid من الرابط المرسل
        vid = None
        vid_match = re.search(r'vid=([a-zA-Z0-9]+)', target_url)
        if vid_match:
            vid = vid_match.group(1)
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Referer": "https://ahwaktv.net/",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            session = requests.Session()
            
            # الخطوة 1: إذا نجحنا في استخراج الـ vid، نضرب الـ API المباشر للسيرفر لتوليد الروابط
            if vid:
                # محاكاة الطلب الخلفي الذي يطلبه المتصفح لجلب ملف الـ m3u8
                api_url = f"https://yam.ahwaktv.net/player/ajax_sources.php?id={vid}"
                api_response = session.get(api_url, headers=headers, timeout=8)
                
                # البحث عن رابط m3u8 داخل رد الـ API
                match = re.search(r'(https:[^\s"\']+\.m3u8[^\s"\']*)', api_response.text)
                if not match:
                    match = re.search(r'(https:\\\\/[^\s"\']+\.m3u8[^\s"\']*)', api_response.text)
                    
                if match:
                    video_url = match.group(0).replace('\\/', '/')
                    self.redirect_to(video_url)
                    return

            # الخطوة 2: كخطة بديلة (Fallback) إذا لم نجد الـ vid، نقرأ الصفحة كاملة ونفتش فيها
            response = session.get(target_url, headers=headers, timeout=10)
            html = response.text
            
            match = re.search(r'(https:[^\s"\']+\.m3u8[^\s"\']*)', html)
            if not match:
                match = re.search(r'(https:\\\\/[^\s"\']+\.m3u8[^\s"\']*)', html)
                
            if match:
                video_url = match.group(0).replace('\\/', '/')
                self.redirect_to(video_url)
                return
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("عذراً، لم نتمكن من قنص الرابط المتغير. قد تكون الحماية قد حدثت.".encode('utf-8'))
                
        except:
            self.send_response(500)
            self.end_headers()

    def redirect_to(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
