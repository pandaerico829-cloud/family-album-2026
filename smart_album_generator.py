#!/usr/bin/env python3
"""
智能家庭相冊生成系统 - 完整版
功能：
1. 扫描并分析相片（EXIF GPS、日期、内容）
2. 智能场景过滤（排除办公、会议、纯风景等）
3. 按活动自动分群（GPS+日期聚类）
4. 生成多个活动相冊
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
from typing import List, Dict, Tuple, Optional

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("正在安装依赖包...")
    os.system("pip install Pillow pillow-heif -q")
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS

# HEIC支持
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except:
    pass

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / 'output' / 'web'
PHOTOS_DIR = OUTPUT_DIR / 'photos'
ANALYSIS_FILE = ROOT_DIR / 'output' / 'smart_analysis.json'

# 源目录
PHOTO_SOURCES = [
    Path(r"C:\Users\User\OneDrive\Pictures\相機膠卷\2026")
]

PASSWORD = '0829'
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()

# 活动主题配色方案
ACTIVITY_THEMES = {
    'japan': {'color': '#C9A0A0', 'accent': '#F5E6E6', 'label': '日本'},
    'europe': {'color': '#2C3E6B', 'accent': '#C5A55A', 'label': '欧洲'},
    'southeast_asia': {'color': '#2D6A4F', 'accent': '#A8D5BA', 'label': '东南亚'},
    'taiwan': {'color': '#D4795A', 'accent': '#FDF8F5', 'label': '台湾'},
    'usa': {'color': '#5B6F6D', 'accent': '#D4C5B0', 'label': '美国'},
    'other': {'color': '#7D5A50', 'accent': '#E8D7C0', 'label': '其他'}
}

class PhotoAnalyzer:
    """相片分析器"""
    
    def __init__(self):
        self.photos = []
        self.activities = defaultdict(list)
    
    def scan_photos(self) -> List[Dict]:
        """扫描所有相片"""
        print("🔍 扫描相片...")
        valid_extensions = {'.jpg', '.jpeg', '.heic'}
        
        rejected_count = 0
        for source in PHOTO_SOURCES:
            for photo_path in source.rglob('*'):
                if photo_path.suffix.lower() in valid_extensions:
                    photo_info = self._analyze_photo(photo_path)
                    if photo_info:
                        self.photos.append(photo_info)
                    else:
                        rejected_count += 1
        
        print(f"✓ 已扫描 {len(self.photos)} 张相片，过滤掉 {rejected_count} 张不符合条件的相片")
        return self.photos
    
    def _analyze_photo(self, photo_path: Path) -> Optional[Dict]:
        """分析单张相片"""
        try:
            img = Image.open(photo_path)
            
            # 提取EXIF数据
            exif_data = self._get_exif(img)
            gps_info = exif_data.get('gps_coords')
            date_taken = exif_data.get('date_taken')
            
            # 判断场景
            if not self._is_valid_scene(photo_path, img):
                return None
            
            return {
                'path': str(photo_path),
                'filename': photo_path.name,
                'size': photo_path.stat().st_size,
                'date_taken': date_taken or datetime.fromtimestamp(photo_path.stat().st_mtime).timestamp(),
                'gps': gps_info,
                'width': img.width,
                'height': img.height,
                'aspect_ratio': img.width / img.height if img.height > 0 else 1.0,
            }
        except Exception as e:
            return None
    
    def _get_exif(self, img: Image.Image) -> Dict:
        """提取EXIF数据"""
        exif_data = {'gps_coords': None, 'date_taken': None}
        
        try:
            exif = img._getexif()
            if not exif:
                return exif_data
            
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                
                # 提取GPS坐标
                if tag == 'GPSInfo':
                    gps_data = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = gps_value
                    
                    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                        lat = self._dms_to_decimal(gps_data['GPSLatitude'], gps_data.get('GPSLatitudeRef', 'N'))
                        lon = self._dms_to_decimal(gps_data['GPSLongitude'], gps_data.get('GPSLongitudeRef', 'E'))
                        exif_data['gps_coords'] = (lat, lon)
                
                # 提取拍摄日期
                elif tag == 'DateTime':
                    try:
                        exif_data['date_taken'] = datetime.strptime(value, '%Y:%m:%d %H:%M:%S').timestamp()
                    except:
                        pass
        
        except:
            pass
        
        return exif_data
    
    def _dms_to_decimal(self, dms: Tuple, ref: str) -> float:
        """将DMS坐标转换为十进制"""
        d, m, s = dms
        decimal = d + m / 60.0 + s / 3600.0
        return -decimal if ref in ['S', 'W'] else decimal
    
    def _is_valid_scene(self, photo_path: Path, img: Image.Image) -> bool:
        """判断是否为有效场景（排除办公、白板、广告等）"""
        filename = photo_path.name.lower()
        parent = str(photo_path.parent).lower()
        text = filename + ' ' + parent
        
        # 排除特定文件名或路径模式
        blacklist_patterns = [
            'screenshot', 'screen', 'whiteboard', 'meeting', 'office',
            'document', 'scan', 'slide', 'chart', 'graph', 'receipt',
            'menu', 'ticket', 'qrcode', 'code', 'invoice', 'bill', 'statement',
            'shopping', 'shop', 'product', 'model', 'advert', 'ad', 'commercial',
            'mall', 'store', 'clothing', 'cloth', 'dress', 'shirt', 'pants',
            'catalog', 'banner', 'poster', 'storefront', 'online', 'website',
            'fashion', 'apparel', '商品', '購物', '網購', '模特', '廣告', '促銷', '折扣',
            '優惠', '宣傳', '拍賣', '淘寶', '蝦皮', 'momo', 'pchome'
        ]
        
        for pattern in blacklist_patterns:
            if pattern in text:
                return False
        
        # 排除极端长宽比（可能是截屏、证件照、商品图）
        aspect = img.width / img.height if img.height > 0 else 1.0
        if aspect < 0.5 or aspect > 3.0:
            return False
        
        # 排除极端小尺寸
        if img.width < 400 or img.height < 400:
            return False
        
        return True
    
    def cluster_activities(self) -> Dict:
        """按GPS和日期聚类成活动"""
        print("📍 分群活动...")
        
        if not self.photos:
            return {}
        
        # 按日期排序
        sorted_photos = sorted(self.photos, key=lambda x: x['date_taken'])
        
        # 简单的时间范围分群
        activities = defaultdict(list)
        current_activity = []
        last_date = None
        
        for photo in sorted_photos:
            photo_date = datetime.fromtimestamp(photo['date_taken'])
            
            # 新活动条件：间隔超过7天
            if last_date and (photo_date - last_date).days > 7:
                if len(current_activity) >= 5:  # 至少5张照片才算一个活动
                    activity_id = self._generate_activity_id(current_activity)
                    activities[activity_id] = current_activity
                current_activity = []
            
            current_activity.append(photo)
            last_date = photo_date
        
        # 处理最后一个活动
        if len(current_activity) >= 5:
            activity_id = self._generate_activity_id(current_activity)
            activities[activity_id] = current_activity
        
        # 日常照片（不足5张的零散照片）
        all_in_activities = set()
        for photos in activities.values():
            for p in photos:
                all_in_activities.add(p['filename'])
        
        daily_photos = [p for p in sorted_photos if p['filename'] not in all_in_activities]
        if daily_photos:
            activities['daily_life'] = daily_photos
        
        print(f"✓ 分群完成，共 {len(activities)} 个活动")
        return dict(activities)
    
    def _generate_activity_id(self, photos: List[Dict]) -> str:
        """为活动生成ID和名称"""
        if not photos:
            return 'unknown'
        
        dates = [datetime.fromtimestamp(p['date_taken']) for p in photos]
        start_date = min(dates)
        end_date = max(dates)
        
        # 简单命名：日期范围 + 位置
        if start_date.year == end_date.year and start_date.month == end_date.month:
            date_str = f"{start_date.strftime('%m')}"
        else:
            date_str = f"{start_date.strftime('%m')}-{end_date.strftime('%m')}"
        
        return f"activity_{date_str}_{start_date.strftime('%d')}"
    
    def select_best_photos(self, activity_photos: List[Dict], limit: int = 20) -> List[Dict]:
        """为活动精选最佳相片"""
        # 排序：按清晰度（分辨率）、宽高比（优先16:9）
        def score_photo(p):
            pixels = p['width'] * p['height']
            aspect_score = 1.0 - abs(p['aspect_ratio'] - 1.777)  # 16:9 = 1.777
            return pixels * aspect_score
        
        sorted_photos = sorted(activity_photos, key=score_photo, reverse=True)
        return sorted_photos[:limit]

class WebsiteGenerator:
    """网站生成器"""
    
    def __init__(self, activities: Dict[str, List[Dict]]):
        self.activities = activities
        self.activity_pages = {}
    
    def generate(self):
        """生成完整网站"""
        print("🎨 生成网站...")
        
        # 清空输出目录
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 复制和转换相片
        print("📸 处理相片...")
        self._process_photos()
        
        # 生成首页
        self._generate_index()
        
        # 生成活动页面
        for activity_id, photos in self.activities.items():
            self._generate_activity_page(activity_id, photos)
        
        print("✓ 网站生成完成")
    
    def _process_photos(self):
        """处理和复制相片到输出目录"""
        all_photos = []
        for photos in self.activities.values():
            all_photos.extend(photos)
        
        count = 0
        for photo_info in all_photos:
            try:
                src_path = Path(photo_info['path'])
                dst_name = src_path.stem + '.jpg'
                dst_path = PHOTOS_DIR / dst_name
                
                if src_path.suffix.lower() == '.heic':
                    self._convert_heic_to_jpg(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)
                
                count += 1
            except Exception as e:
                pass
        
        print(f"✓ 已处理 {count} 张相片")
    
    def _convert_heic_to_jpg(self, src: Path, dst: Path):
        """HEIC转JPG"""
        try:
            from PIL import Image
            img = Image.open(src)
            img.convert('RGB').save(dst, 'JPEG', quality=95)
        except Exception as e:
            shutil.copy2(src, dst)
    
    def _generate_index(self):
        """生成首页"""
        html_content = self._get_index_html()
        index_path = OUTPUT_DIR / 'index.html'
        index_path.write_text(html_content, encoding='utf-8')
        print("✓ 生成 index.html")
    
    def _generate_activity_page(self, activity_id: str, photos: List[Dict]):
        """生成活动页面"""
        html_content = self._get_activity_html(activity_id, photos)
        activity_path = OUTPUT_DIR / f'{activity_id}.html'
        activity_path.write_text(html_content, encoding='utf-8')
    
    def _get_index_html(self) -> str:
        """生成首页HTML"""
        return """<!DOCTYPE html>
<html lang='zh-TW'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>家庭相冊 2026</title>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; font-family: 'Noto Serif TC', sans-serif; background: #fafafa; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        h1 { font-family: 'Playfair Display', serif; font-size: 3rem; margin-bottom: 40px; text-align: center; }
        .activities-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
        .activity-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.3s; cursor: pointer; }
        .activity-card:hover { transform: translateY(-4px); box-shadow: 0 8px 16px rgba(0,0,0,0.15); }
        .activity-card img { width: 100%; height: 200px; object-fit: cover; }
        .activity-info { padding: 16px; }
        .activity-info h3 { margin: 0; font-size: 1.2rem; }
        .activity-info p { margin: 8px 0 0; color: #666; font-size: 0.9rem; }
        a { color: inherit; text-decoration: none; }
    </style>
</head>
<body>
    <div class='container'>
        <h1>📸 家庭相冊 2026</h1>
        <div class='activities-grid'>
            <!-- 活动卡片将被插入这里 -->
        </div>
    </div>
</body>
</html>"""
    
    def _get_activity_html(self, activity_id: str, photos: List[Dict]) -> str:
        """生成活动页面HTML"""
        title = activity_id.replace('activity_', '').replace('_', ' ')
        theme = self._get_activity_theme(activity_id)
        
        photo_cards = ''.join([
            f"""<div class='card'>
                <img src='photos/{Path(p['path']).stem}.jpg' loading='lazy'>
                <div class='card-meta'>
                    <p class='caption'>{Path(p['path']).stem}</p>
                </div>
            </div>"""
            for p in photos[:20]
        ])
        
        return f"""<!DOCTYPE html>
<html lang='zh-TW'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>{title}</title>
    <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Noto+Serif+TC:wght@400;500;600&display=swap' rel='stylesheet'>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Noto+Serif+TC:wght@400;500;600&display=swap');
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; font-family: 'Noto Serif TC', serif; background: {theme['accent']}; color: #2f2f2f; }}
        .page-shell {{ min-height: 100vh; }}
        .hero {{ position: relative; min-height: 60vh; display: flex; align-items: flex-end; padding: 40px; background-size: cover; background-position: center; }}
        .hero::after {{ content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.5)); }}
        .hero-content {{ position: relative; z-index: 1; color: white; }}
        .hero h1 {{ font-family: 'Playfair Display', serif; font-size: 3rem; margin: 0; }}
        .gallery {{ column-count: 3; column-gap: 20px; padding: 40px; max-width: 1400px; margin: 0 auto; }}
        .card {{ break-inside: avoid; margin-bottom: 20px; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; display: block; }}
        .card-meta {{ padding: 12px; }}
        .caption {{ margin: 0; font-size: 0.9rem; color: #666; }}
        .footer {{ padding: 30px; text-align: center; color: #999; }}
        @media (max-width: 1024px) {{ .gallery {{ column-count: 2; }} }}
        @media (max-width: 600px) {{ .gallery {{ column-count: 1; }} }}
    </style>
</head>
<body>
    <div class='page-shell'>
        <div class='hero' style='background: linear-gradient(135deg, {theme['color']} 0%, {theme['accent']} 100%);'>
            <div class='hero-content'>
                <h1>{title}</h1>
                <p>精选 {len(photos)} 张相片</p>
            </div>
        </div>
        <div class='gallery'>
            {photo_cards}
        </div>
        <footer class='footer'>© 2026 Family Album</footer>
    </div>
</body>
</html>"""
    
    def _get_activity_theme(self, activity_id: str) -> Dict:
        """获取活动的配色方案"""
        if 'japan' in activity_id.lower():
            return ACTIVITY_THEMES['japan']
        elif 'europe' in activity_id.lower():
            return ACTIVITY_THEMES['europe']
        elif 'daily' in activity_id:
            return ACTIVITY_THEMES['taiwan']
        else:
            return ACTIVITY_THEMES['other']

def main():
    """主程序"""
    print("🚀 智能家庭相冊生成系统启动...\n")
    
    # 分析相片
    analyzer = PhotoAnalyzer()
    analyzer.scan_photos()
    activities = analyzer.cluster_activities()
    
    # 生成网站
    generator = WebsiteGenerator(activities)
    generator.generate()
    
    print("\n✅ 项目完成！")
    print(f"📍 输出目录: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
