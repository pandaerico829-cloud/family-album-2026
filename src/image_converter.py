"""
圖像格式轉換模塊
"""
import os
from pathlib import Path
from PIL import Image
import io

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pillow_heif = None

class ImageConverter:
    """圖像格式轉換器"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    CONVERTIBLE_FORMATS = {'.heic', '.heif'}
    
    @staticmethod
    def convert_heic_to_jpeg(heic_path: str, quality: int = 85) -> bytes:
        """將HEIC轉換為JPEG"""
        if pillow_heif is None:
            print(f"HEIC轉換失敗，缺少 pillow_heif: {heic_path}")
            return None
        try:
            with Image.open(heic_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                return output.getvalue()
        except Exception as e:
            print(f"轉換失敗 {heic_path}: {e}")
            return None
    
    @staticmethod
    def get_image_data(image_path: str) -> tuple:
        """獲取圖像數據和MIME類型"""
        path = Path(image_path)
        ext = path.suffix.lower()
        
        try:
            if ext in {'.heic', '.heif'}:
                image_data = ImageConverter.convert_heic_to_jpeg(image_path)
                mime_type = 'image/jpeg'
            else:
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                mime_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp'
                }
                mime_type = mime_type_map.get(ext, 'image/jpeg')
            return image_data, mime_type
        except Exception as e:
            print(f"讀取圖像失敗 {image_path}: {e}")
            return None, None
