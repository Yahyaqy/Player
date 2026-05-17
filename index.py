from http.server import BaseHTTPRequestHandler
import requests
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. رابط صفحة البث الأصلية لقناة MBC 1
        source_url = "https://play.arab-stream.live/p/mbc-1-ksa.html?m=1"
        
        # إرسال مستخدم وهمي (User-Agent) متوافق لجعل السيرفر يظن أنه متصفح حقيقي
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://play.arab-stream.live/"
        }
        
        try:
            # 2. طلب محتوى الصفحة برمجياً
            response = requests.get(source_url, headers=headers, timeout=7)
            html = response.text
            
            # 3. استخدام الـ Regex للبحث عن رابط الـ m3u8 الذي يحتوي على التوكن المتغير
            # الكود يبحث عن أي رابط يبدأ بـ https وينتهي بـ index.m3u8
            match = re.search(r'https://[^\s"\']+/index\.m3u8', html)
            
            if match:
                real_stream_url = match.group(0)
                
                # 4. إعادة توجيه ذكية (302 Redirect) للمشغل نحو الرابط الحي بالتوكن الجديد
                self.send_response(302)
                self.send_header('Location', real_stream_url)
                # السماح لجميع المشغلات بالوصول بدون قيود حماية المتصفح (CORS)
                self.send_header('Access-Control-Allow-Origin', '*') 
                self.end_headers()
            else:
                # في حال فشل القنص لأي سبب، يتم تحويله للرابط الثابت الذي أرسلته كاحتياط مؤقت
                self.send_response(302)
                self.send_header('Location', 'https://shd-gcp-live-orng.shahid.net/live/bitmovin-mbc-1-na/eec141533c90dd34722c503a296dd0d8/index.m3u8')
                self.end_headers()
                
        except Exception as e:
            # في حال حدوث خطأ في الاتصال بالسيرفر
            self.send_response(500)
            self.end_headers()
