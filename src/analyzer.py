"""
圖像分析模塊 - 使用Vision API分析相片內容
"""
import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Tuple
import requests
from PIL import Image
from io import BytesIO

class ImageAnalyzer:
    def __init__(self, config: Dict):
        self.config = config
        self.api_provider = config.get('api_config', {}).get('provider', 'openai')
        self.api_key = config.get('api_config', {}).get('api_key', '')
        
    def analyze_image(self, image_path: str) -> Dict:
        """
        分析單張相片
        返回：{
            'path': 相片路徑,
            'category': 分類（family/travel/celebration）,
            'family_members': [識別出的家庭成員],
            'confidence': 信心度,
            'description': 相片描述
        }
        """
        if not self.api_key:
            # 使用模擬分析（開發用）
            return self._mock_analysis(image_path)
        
        if self.api_provider == 'openai':
            return self._analyze_openai(image_path)
        elif self.api_provider == 'google':
            return self._analyze_google(image_path)
        else:
            return self._mock_analysis(image_path)
    
    def _analyze_openai(self, image_path: str) -> Dict:
        """使用OpenAI GPT-4V分析"""
        try:
            with open(image_path, 'rb') as f:
                image_data = base64.standard_b64encode(f.read()).decode('utf-8')
            
            # 確定文件類型
            ext = Path(image_path).suffix.lower()
            if ext in ['.heic', '.heif']:
                media_type = 'image/jpeg'  # HEIC需轉換
            elif ext == '.png':
                media_type = 'image/png'
            else:
                media_type = 'image/jpeg'
            
            prompt = """請分析這張家庭相片並分類。回答必須是以下JSON格式（不要添加其他內容）：
{
    "category": "family|travel|celebration",
    "family_members": ["爸爸|媽媽|哥哥|妹妹"],
    "confidence": 0-100,
    "description": "相片簡短描述",
    "reason": "分類原因"
}

分類規則：
- family: 日常生活、人物照、家庭成員照片
- travel: 旅遊地點、風景、出遊照片
- celebration: 過節聚餐、吃飯、聚會活動

只回答JSON，不要任何其他文字。"""
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': self.config.get('api_config', {}).get('model', 'gpt-4-vision-preview'),
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {'type': 'text', 'text': prompt},
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:{media_type};base64,{image_data}'
                                    }
                                }
                            ]
                        }
                    ],
                    'max_tokens': 500
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                try:
                    analysis = json.loads(result['choices'][0]['message']['content'])
                    analysis['path'] = image_path
                    return analysis
                except json.JSONDecodeError:
                    return self._mock_analysis(image_path)
            else:
                print(f"API錯誤: {response.status_code}")
                return self._mock_analysis(image_path)
                
        except Exception as e:
            print(f"分析失敗 {image_path}: {e}")
            return self._mock_analysis(image_path)
    
    def _analyze_google(self, image_path: str) -> Dict:
        """使用Google Cloud Vision分析（待實現）"""
        return self._mock_analysis(image_path)
    
    def _mock_analysis(self, image_path: str) -> Dict:
        """模擬分析（用於開發/測試）"""
        import random
        categories = ['family', 'travel', 'celebration']
        family_members = ['爸爸', '媽媽', '哥哥', '妹妹']
        
        category = random.choice(categories)
        num_members = random.randint(0, 3)
        members = random.sample(family_members, num_members)
        
        descriptions = {
            'family': '家庭成員日常照片',
            'travel': '旅遊景點照片',
            'celebration': '聚餐慶祝活動'
        }
        
        return {
            'path': image_path,
            'category': category,
            'family_members': members,
            'confidence': random.randint(75, 95),
            'description': descriptions.get(category, '相片'),
            'reason': '自動分類'
        }
    
    def batch_analyze(self, image_paths: List[str], progress_callback=None) -> List[Dict]:
        """批量分析相片"""
        results = []
        total = len(image_paths)
        
        for idx, path in enumerate(image_paths):
            result = self.analyze_image(path)
            results.append(result)
            
            if progress_callback:
                progress_callback(idx + 1, total)
        
        return results


class PhotoClassifier:
    """相片分類器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.categories = config.get('categories', {})
    
    def organize_photos(self, analysis_results: List[Dict], output_base: str) -> Dict:
        """
        根據分析結果組織相片
        返回組織結構
        """
        organized = {
            'family': [],
            'travel': [],
            'celebration': []
        }
        
        for result in analysis_results:
            category = result.get('category', 'family')
            if category not in organized:
                organized[category] = []
            organized[category].append(result)
        
        return organized
