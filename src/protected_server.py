"""
密碼保護和部署模塊
"""
import os
import json
import io
from flask import Flask, render_template_string, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

class ProtectedAlbumServer:
    """密碼保護的相冊服務器"""
    
    def __init__(self, album_path: str, password: str, port: int = 5000):
        self.app = Flask(__name__)
        self.app.secret_key = 'family-album-secret-2026'
        self.album_path = Path(album_path)
        self.photos_path = self.album_path.parent.parent / 'photos' / 'original'
        self.password = password
        self.port = port
        
        self._setup_routes()
    
    def _setup_routes(self):
        """設置路由"""
        
        @self.app.route('/')
        def login():
            """登錄頁面"""
            if 'authenticated' in session:
                return redirect('/album')
            
            return render_template_string(self.get_login_template())
        
        @self.app.route('/authenticate', methods=['POST'])
        def authenticate():
            """驗證密碼"""
            password = request.form.get('password', '')
            
            if password == self.password:
                session['authenticated'] = True
                return redirect('/album')
            else:
                return render_template_string(
                    self.get_login_template(error='密碼錯誤！')
                )
        
        @self.app.route('/album')
        def album_index():
            """相冊主頁"""
            if 'authenticated' not in session:
                return redirect('/')
            
            # 讀取index.html
            index_file = self.album_path / 'index.html'
            if index_file.exists():
                with open(str(index_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 修改連結以適應路由
                    content = content.replace('href="family.html"', 'href="/album/family"')
                    content = content.replace('href="travel.html"', 'href="/album/travel"')
                    content = content.replace('href="celebration.html"', 'href="/album/celebration"')
                    return content
            return "相冊不存在"
        
        @self.app.route('/album/<category>')
        def album_category(category):
            """分類相冊"""
            if 'authenticated' not in session:
                return redirect('/')
            
            # 只接受有效的分類
            if category not in ['family', 'travel', 'celebration']:
                return "分類不存在", 404
            
            category_file = self.album_path / f'{category}.html'
            if category_file.exists():
                with open(str(category_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 修改相冊中的返回連結
                    content = content.replace('href="index.html"', 'href="/album"')
                    # 修改photo路徑（相片可能需要直接訪問）
                    return content
            return "相冊不存在", 404
        
        @self.app.route('/logout')
        def logout():
            """登出"""
            session.clear()
            return redirect('/')
        
        # 相片服務
        @self.app.route('/photo/<path:filename>')
        def serve_photo(filename):
            """提供相片文件"""
            if 'authenticated' not in session:
                return "未授權", 401
            
            # 安全檢查：防止路徑遍歷
            if '..' in filename or filename.startswith('/'):
                return "禁止訪問", 403
            
            photo_path = self.photos_path / filename
            if photo_path.exists() and photo_path.is_file():
                from flask import send_file
                from src.image_converter import ImageConverter
                
                # 獲取圖像數據和MIME類型
                image_data, mime_type = ImageConverter.get_image_data(str(photo_path))
                
                if image_data:
                    output = io.BytesIO(image_data)
                    output.seek(0)
                    return send_file(output, mimetype=mime_type, conditional=True)
                else:
                    return "圖像轉換失敗", 500
            return "文件不存在", 404
        
        # 靜態文件服務
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return self._serve_file(filename)
    
    def get_login_template(self, error: str = None) -> str:
        """獲取登錄頁面HTML"""
        error_html = ''
        if error:
            error_html = f'<div class="error-message">{error}</div>'
        
        return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>家庭相冊 - 密碼保護</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .login-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            width: 100%;
            max-width: 400px;
            animation: slideUp 0.5s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .logo {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 48px;
        }}
        
        h1 {{
            text-align: center;
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            text-align: center;
            color: #999;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        
        .form-group {{
            margin-bottom: 20px;
        }}
        
        label {{
            display: block;
            color: #333;
            font-size: 14px;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        input[type="password"] {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        input[type="password"]:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .submit-btn {{
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .submit-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
        
        .submit-btn:active {{
            transform: translateY(0);
        }}
        
        .error-message {{
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
            border-left: 4px solid #c62828;
        }}
        
        .hint {{
            text-align: center;
            color: #ccc;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #f0f0f0;
        }}
        
        @media (max-width: 480px) {{
            .login-container {{
                padding: 30px 20px;
            }}
            
            h1 {{
                font-size: 20px;
            }}
            
            .logo {{
                font-size: 40px;
                margin-bottom: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">📸</div>
        <h1>家庭相冊</h1>
        <p class="subtitle">2026 精選集</p>
        
        {error_html}
        
        <form method="POST" action="/authenticate">
            <div class="form-group">
                <label for="password">輸入密碼查看相冊</label>
                <input 
                    type="password" 
                    id="password" 
                    name="password" 
                    placeholder="請輸入密碼" 
                    autofocus
                    required
                >
            </div>
            <button type="submit" class="submit-btn">進入相冊</button>
        </form>
        
        <div class="hint">
            💡 只允許合家庭成員訪問
        </div>
    </div>
</body>
</html>'''
    
    def _serve_file(self, filename: str):
        """提供靜態文件"""
        file_path = self.album_path / filename
        if file_path.exists():
            with open(str(file_path), 'rb') as f:
                return f.read()
        return "文件不存在", 404
    
    def run(self, debug: bool = False):
        """運行服務器"""
        import sys
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print("""
┌─────────────────────────────────────┐
│  相冊服務器已啟動                     │
└─────────────────────────────────────┘

訪問地址: http://localhost:""" + str(self.port) + """
密碼: """ + self.password + """

按 Ctrl+C 停止服務器
        """)
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)

# 用於快速測試
if __name__ == '__main__':
    album_path = './output/web'
    password = '0829'
    
    server = ProtectedAlbumServer(album_path, password, port=5000)
    server.run(debug=True)
