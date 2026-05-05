"""
家庭相冊整理主程序
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from src.analyzer import ImageAnalyzer, PhotoClassifier
from src.html_generator import AlbumHTMLGenerator

class AlbumOrganizer:
    """整理和生成家庭相冊的主類"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.source_path = Path(self.config['source_path'])
        self.output_path = Path(self.config['output_path'])
        self.photos_path = Path(self.config['photos_path'])
        
        # 確保輸出目錄存在
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.photos_path.mkdir(parents=True, exist_ok=True)
    
    def copy_photos_to_local(self) -> list:
        """將相片複製到本地目錄"""
        print(f"📋 掃描相片... 源目錄: {self.source_path}")
        
        photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.heic', '.heif'}
        all_photos = []
        
        for ext in photo_extensions:
            all_photos.extend(self.source_path.rglob(f'*{ext}'))
            all_photos.extend(self.source_path.rglob(f'*{ext.upper()}'))
        
        # 去重
        all_photos = list(set(all_photos))
        all_photos.sort()
        
        print(f"✓ 找到 {len(all_photos)} 張相片")
        
        # 複製到本地
        copied_photos = []
        original_dir = self.photos_path / 'original'
        original_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, photo_path in enumerate(all_photos):
            try:
                dest = original_dir / photo_path.name
                # 如果文件已存在，跳過
                if not dest.exists():
                    shutil.copy2(str(photo_path), str(dest))
                copied_photos.append(str(dest))
                
                if (idx + 1) % 50 == 0:
                    print(f"✓ 已複製 {idx + 1}/{len(all_photos)} 張相片")
            except Exception as e:
                print(f"✗ 複製失敗 {photo_path.name}: {e}")
        
        print(f"✓ 複製完成！共 {len(copied_photos)} 張相片")
        return copied_photos
    
    def analyze_and_classify(self, photo_paths: list) -> dict:
        """分析和分類相片"""
        print(f"\n🔍 分析相片中...")
        
        analyzer = ImageAnalyzer(self.config)
        
        # 檢查API密鑰
        if not self.config.get('api_config', {}).get('api_key'):
            print("""
⚠️  未檢測到API密鑰！
有以下選項：
1. 使用模擬分析（開發用，隨機分類）
2. 配置OpenAI API密鑰

當前使用模擬分析模式...
            """)
        
        # 分析所有相片
        results = []
        for idx, path in enumerate(photo_paths):
            result = analyzer.analyze_image(path)
            results.append(result)
            
            if (idx + 1) % 50 == 0:
                print(f"✓ 已分析 {idx + 1}/{len(photo_paths)} 張")
        
        # 分類相片
        classifier = PhotoClassifier(self.config)
        organized = classifier.organize_photos(results, str(self.output_path))
        
        print(f"\n✓ 分類完成：")
        for category, photos in organized.items():
            category_names = {
                'family': '家庭成員',
                'travel': '旅遊',
                'celebration': '節慶聚餐'
            }
            print(f"  - {category_names.get(category, category)}: {len(photos)} 張")
        
        return organized
    
    def generate_html_albums(self, organized_photos: dict):
        """生成HTML相冊"""
        print(f"\n🎨 生成HTML相冊...")
        
        html_output = self.output_path / 'web'
        html_output.mkdir(parents=True, exist_ok=True)
        
        generator = AlbumHTMLGenerator(self.config)
        generator.generate_albums(organized_photos, str(html_output))
        
        print(f"✓ HTML相冊已生成到: {html_output}")
        return html_output
    
    def save_analysis_data(self, organized_photos: dict):
        """保存分析數據"""
        data_file = self.output_path / 'analysis_data.json'
        
        # 轉換為可序列化格式
        serializable_data = {}
        for category, photos in organized_photos.items():
            serializable_data[category] = [
                {
                    'path': photo.get('path'),
                    'description': photo.get('description', ''),
                    'family_members': photo.get('family_members', []),
                    'confidence': photo.get('confidence', 0),
                    'reason': photo.get('reason', '')
                }
                for photo in photos
            ]
        
        with open(str(data_file), 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 分析數據已保存到: {data_file}")
    
    def generate_summary(self, organized_photos: dict, html_output_path: str):
        """生成摘要報告"""
        summary = f"""
┌─────────────────────────────────────┐
│   📸 家庭相冊整理 - 完成摘要         │
└─────────────────────────────────────┘

📊 統計信息：
  - 總相片數: {sum(len(v) for v in organized_photos.values())} 張
  - 家庭成員照: {len(organized_photos.get('family', []))} 張
  - 旅遊景點: {len(organized_photos.get('travel', []))} 張
  - 節慶聚餐: {len(organized_photos.get('celebration', []))} 張

🌐 網頁位置：
  - 主頁: {html_output_path}/index.html
  - 家庭相冊: {html_output_path}/family.html
  - 旅遊相冊: {html_output_path}/travel.html
  - 節慶相冊: {html_output_path}/celebration.html

📁 相片存儲：
  - 原始相片: {self.photos_path}/original/
  - 分析數據: {self.output_path}/analysis_data.json

🔐 密碼保護：
  - 密碼: {self.config.get('password', '0829')}
  - 狀態: 待部署時激活

⏰ 完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 後續步驟：
  1. ✓ 審查生成的相冊
  2. ⏳ 配置密碼保護
  3. ⏳ 部署到網路
  4. ⏳ 測試密碼訪問
"""
        
        # 保存摘要
        summary_file = self.output_path / 'SUMMARY.txt'
        with open(str(summary_file), 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(summary)
        return summary

def main():
    """主程序入口"""
    print("""
╔════════════════════════════════════════╗
║   🏠 家庭相冊智能整理系統              ║
║   Family Album Organization System    ║
╚════════════════════════════════════════╝
    """)
    
    # 加載配置
    config_path = Path(__file__).parent / 'config.json'
    if not config_path.exists():
        print(f"❌ 找不到配置文件: {config_path}")
        return
    
    organizer = AlbumOrganizer(str(config_path))
    
    try:
        # 步驟1: 複製相片
        print("\n[步驟 1/4] 複製相片到本地目錄")
        print("=" * 40)
        photo_paths = organizer.copy_photos_to_local()
        
        if not photo_paths:
            print("❌ 沒有找到相片！")
            return
        
        # 步驟2: 分析和分類
        print("\n[步驟 2/4] 分析和分類相片")
        print("=" * 40)
        organized_photos = organizer.analyze_and_classify(photo_paths)
        
        # 步驟3: 生成HTML相冊
        print("\n[步驟 3/4] 生成HTML相冊")
        print("=" * 40)
        html_path = organizer.generate_html_albums(organized_photos)
        
        # 步驟4: 保存數據和生成摘要
        print("\n[步驟 4/4] 保存數據和生成報告")
        print("=" * 40)
        organizer.save_analysis_data(organized_photos)
        organizer.generate_summary(organized_photos, str(html_path))
        
        print("\n✅ 所有步驟完成！")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
