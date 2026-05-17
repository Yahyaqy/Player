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
        
        # استخراج الـ vid من الرابط
        vid = None
        vid_match = re.search(r'vid=([a-zA-Z0-9]+)', target_url)
        if vid_match:
            vid = vid_match.group(1)
            
        # ترويسات متطابقة تماماً مع متصفح كروم على الأندرويد
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "Referer": target_url,
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive"
        }
        
        try:
            # فتح جلسة ذكية للحفاظ على الكوكيز بين الطلبات
            session = requests.Session()
            
            # الخطوة 1: زيارة الصفحة الرئيسية للمشغل أولاً للحصول على الكوكيز وجدار الحماية
            session.get(target_url, headers={"User-Agent": headers["User-Agent"]}, timeout=10)
            
            if vid:
                # الخطوة 2: ضرب الـ API الخاص بجلب السيرفرات مع تمرير الكوكيز المكتسبة
                api_url = f"https://yam.ahwaktv.net/player/ajax_sources.php?id={vid}"
                api_response = session.get(api_url, headers=headers, timeout=10)
                res_text = api_response.text
                
                # البحث عن الرابط بصيغته العادية أو المشفرة بـ \/
                match = re.search(r'(https:[^\s"\']+\.m3u8[^\s"\']*)', res_text)
                if not match:
                    match = re.search(r'(https:\\\\/[^\s"\']+\.m3u8[^\s"\']*)', res_text)
                    
                if match:
                    video_url = match.group(0).replace('\\/', '/')
                    # تنظيف الرابط من أي علامات اقتباس متبقية
                    video_url = video_url.strip('"').strip("'")
                    
                    self.send_response(302)
                    self.send_header('Location', video_url)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    return

            # خطة احتياطية: البحث في الصفحة الأولى مباشرة
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("عذراً، لم نتمكن من تخطي حماية السيرفر الحالية برمجياً.".encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
