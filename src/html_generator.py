"""
HTML相冊生成器 - 創建響應式、手機優化的相冊網頁
"""
import json
import os
from pathlib import Path
from typing import Dict, List

class AlbumHTMLGenerator:
    """生成漂亮的HTML相冊"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.password = config.get('password', '0829')
    
    def generate_albums(self, organized_photos: Dict, output_path: str):
        """生成所有分類的相冊"""
        categories = {
            'family': '家庭成員',
            'travel': '旅遊',
            'celebration': '節慶聚餐'
        }
        
        # 創建主索引頁面
        index_html = self._generate_index_page(categories, organized_photos)
        with open(os.path.join(output_path, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # 為每個分類創建相冊頁面
        for category, title in categories.items():
            if category in organized_photos:
                album_html = self._generate_category_album(
                    category, 
                    title, 
                    organized_photos[category]
                )
                filename = f'{category}.html'
                with open(os.path.join(output_path, filename), 'w', encoding='utf-8') as f:
                    f.write(album_html)
    
    def _generate_index_page(self, categories: Dict, organized_photos: Dict) -> str:
        """生成主索引頁面"""
        stats = {cat: len(organized_photos.get(cat, [])) for cat in categories}
        
        category_cards = '\n'.join([
            f'''
            <div class="category-card">
                <h3>{title}</h3>
                <p class="photo-count">{stats.get(cat, 0)} 張相片</p>
                <a href="{cat}.html" class="btn-view">查看</a>
            </div>
            '''
            for cat, title in categories.items()
        ])
        
        return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>家庭相冊 2026</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            width: 100%;
            max-width: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px 30px;
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
        
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        
        .subtitle {{
            text-align: center;
            color: #999;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        
        .categories {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .category-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .category-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .category-card h3 {{
            color: #333;
            margin-bottom: 8px;
            font-size: 18px;
        }}
        
        .photo-count {{
            color: #666;
            font-size: 14px;
            margin-bottom: 12px;
        }}
        
        .btn-view {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.3s ease;
        }}
        
        .btn-view:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 12px;
        }}
        
        @media (max-width: 600px) {{
            .container {{
                padding: 20px;
                border-radius: 15px;
            }}
            
            h1 {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 家庭相冊</h1>
        <p class="subtitle">2026 年精選集</p>
        
        <div class="categories">
            {category_cards}
        </div>
        
        <div class="footer">
            <p>💝 珍貴的家庭回憶 | {sum(stats.values())} 張相片</p>
        </div>
    </div>
    
    <script>
        // 隱藏右鍵菜單（防止下載）
        document.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // 禁用開發者工具快捷鍵
        document.addEventListener('keydown', (e) => {{
            if (e.ctrlKey && (e.key === 'c' || e.key === 's')) {{
                e.preventDefault();
            }}
        }});
    </script>
</body>
</html>'''
    
    def _generate_category_album(self, category: str, title: str, photos: List[Dict]) -> str:
        """生成分類相冊頁面"""
        # 提取相片檔案名並構建相片URL
        gallery_items = []
        for photo in photos:
            photo_path = photo.get('path', '')
            # 從完整路徑中提取檔案名
            photo_filename = photo_path.split('\\')[-1] if '\\' in photo_path else photo_path.split('/')[-1]
            # 使用 /photo/ 路由
            photo_url = f"/photo/{photo_filename}"
            
            family_members_html = ""
            if photo.get('family_members'):
                members = ', '.join(photo.get('family_members', []))
                family_members_html = f"<span class='family-members'>{members}</span>"
            
            item = f'''
            <div class="gallery-item" data-src="{photo_url}">
                <img src="{photo_url}" alt="{photo.get('description', '')}">
                <div class="photo-info">
                    <p>{photo.get('description', '相片')}</p>
                    {family_members_html}
                </div>
            </div>
            '''
            gallery_items.append(item)
        
        gallery_items_html = '\n'.join(gallery_items)
        
        return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 家庭相冊</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 10px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 24px;
        }}
        
        .back-btn {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
        }}
        
        .back-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            padding: 0;
        }}
        
        .gallery-item {{
            position: relative;
            overflow: hidden;
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .gallery-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .gallery-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
        }}
        
        .photo-info {{
            padding: 8px;
            background: white;
            font-size: 12px;
        }}
        
        .photo-info p {{
            color: #333;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .family-members {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
        }}
        
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        }}
        
        .lightbox.active {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        .lightbox-content {{
            position: relative;
            max-width: 90%;
            max-height: 90%;
        }}
        
        .lightbox img {{
            width: 100%;
            height: auto;
            max-height: 80vh;
            object-fit: contain;
        }}
        
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 30px;
            cursor: pointer;
            background: rgba(0, 0, 0, 0.5);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .lightbox-close:hover {{
            background: rgba(0, 0, 0, 0.7);
        }}
        
        .lightbox-nav {{
            position: absolute;
            width: 100%;
            bottom: 20px;
            display: flex;
            justify-content: center;
            gap: 10px;
        }}
        
        .lightbox-nav button {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid white;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .lightbox-nav button:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        @media (max-width: 768px) {{
            .gallery {{
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                gap: 8px;
            }}
            
            .gallery-item img {{
                height: 150px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .gallery {{
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 5px;
            }}
            
            .gallery-item img {{
                height: 120px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <a href="index.html" class="back-btn">← 返回</a>
    </div>
    
    <div class="gallery">
        {gallery_items_html}
    </div>
    
    <div class="lightbox">
        <div class="lightbox-content">
            <img id="lightbox-img" src="" alt="">
            <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
            <div class="lightbox-nav">
                <button onclick="previousPhoto()">上一張</button>
                <button onclick="nextPhoto()">下一張</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentIndex = 0;
        const items = document.querySelectorAll('.gallery-item');
        const lightbox = document.querySelector('.lightbox');
        const lightboxImg = document.getElementById('lightbox-img');
        
        items.forEach((item, index) => {{
            item.addEventListener('click', () => {{
                currentIndex = index;
                openLightbox(item.querySelector('img').src);
            }});
        }});
        
        function openLightbox(src) {{
            lightboxImg.src = src;
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function closeLightbox() {{
            lightbox.classList.remove('active');
            document.body.style.overflow = 'auto';
        }}
        
        function nextPhoto() {{
            currentIndex = (currentIndex + 1) % items.length;
            lightboxImg.src = items[currentIndex].querySelector('img').src;
        }}
        
        function previousPhoto() {{
            currentIndex = (currentIndex - 1 + items.length) % items.length;
            lightboxImg.src = items[currentIndex].querySelector('img').src;
        }}
        
        // 鍵盤控制
        document.addEventListener('keydown', (e) => {{
            if (lightbox.classList.contains('active')) {{
                if (e.key === 'ArrowRight') nextPhoto();
                if (e.key === 'ArrowLeft') previousPhoto();
                if (e.key === 'Escape') closeLightbox();
            }}
        }});
        
        // 防止下載
        document.addEventListener('contextmenu', (e) => e.preventDefault());
    </script>
</body>
</html>'''
