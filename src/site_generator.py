"""
使用已完成的 analysis_data.json 生成完整相冊網站
"""
import json
import os
import re
import shutil
import sys
import hashlib
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / 'src'))

from image_converter import ImageConverter

CATEGORY_PAGE_MAP = {
    'family': 'family.html',
    'travel': 'travel.html',
    'celebration': 'festival.html'
}

PAGE_TITLES = {
    'index': '家庭相冊 2026',
    'family': '家庭成員相冊',
    'travel': '旅遊相冊',
    'festival': '節慶聚餐相冊'
}

THEME_CONFIG = {
    'japan': {'label': '日本旅遊', 'color': '#C9A0A0', 'accent': '#F5E6E6'},
    'europe': {'label': '歐洲旅遊', 'color': '#2C3E6B', 'accent': '#C5A55A'},
    'southeast': {'label': '東南亞旅遊', 'color': '#2D6A4F', 'accent': '#A8D5BA'},
    'local': {'label': '台灣/家庭/節慶', 'color': '#D4795A', 'accent': '#F4D4C5'},
    'other': {'label': '其他地點', 'color': '#7D5A50', 'accent': '#E8D7C0'}
}

PASSWORD = '0829'
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()


def parse_claude_settings(project_root: Path) -> dict:
    claude_path = project_root / 'CLAUDE.md'
    settings = {}

    if not claude_path.exists():
        raise FileNotFoundError(f'找不到 CLAUDE.md: {claude_path}')

    with open(claude_path, 'r', encoding='utf-8') as f:
        text = f.read()

    patterns = {
        'source': r'相片來源：`([^`]+)`',
        'output': r'輸出位置：`([^`]+)`',
        'categories': r'分類：`([^`]+)`',
        'password': r'密碼：`([^`]+)`'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        settings[key] = match.group(1).strip() if match else None

    if settings['categories']:
        settings['categories'] = [item.strip() for item in settings['categories'].split('、')]
    else:
        settings['categories'] = ['家庭成員', '旅遊', '節慶聚餐']

    settings['output'] = settings['output'].replace('\\', '/') if settings['output'] else str(project_root / 'output' / 'web')
    settings['source'] = settings['source'].replace('\\', '/') if settings['source'] else str(project_root / 'photos' / 'original')
    return settings


def load_analysis_data(project_root: Path) -> dict:
    analysis_file = project_root / 'output' / 'analysis_data.json'
    if not analysis_file.exists():
        raise FileNotFoundError(f'找不到 analysis_data.json: {analysis_file}')

    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def select_top_photos(photo_list: list, limit: int = 30) -> list:
    sorted_list = sorted(photo_list, key=lambda item: item.get('confidence', 0), reverse=True)
    return sorted_list[:min(limit, len(sorted_list))]


def parse_date_from_path(photo_path: str) -> str:
    filename = Path(photo_path).stem
    match = re.match(r'(\d{8})', filename)
    if match:
        try:
            return datetime.strptime(match.group(1), '%Y%m%d').strftime('%Y/%m/%d')
        except ValueError:
            return ''
    return ''


def infer_location_label(description: str, category: str) -> tuple[str, str]:
    text = (description or '').lower()
    if category in ['family', 'celebration']:
        theme = 'local'
        return '台灣 / 家庭', theme

    if '日本' in text or 'tokyo' in text or 'kyoto' in text or 'osaka' in text:
        return '日本', 'japan'
    if '歐洲' in text or '巴黎' in text or '倫敦' in text or '法國' in text or '義大利' in text or '欧洲' in text:
        return '歐洲', 'europe'
    if '東南亞' in text or '泰國' in text or '越南' in text or '印尼' in text or '馬來西亞' in text:
        return '東南亞', 'southeast'

    return '其他地點', 'other'


def generate_caption(item: dict, category: str) -> str:
    members = item.get('family_members', [])
    description = item.get('description', '')
    date_label = parse_date_from_path(item.get('path', ''))
    if category == 'family':
        if members:
            return f"{date_label}，{','.join(members)} 的溫暖時刻，捕捉家庭的真實與親密。"
        return f"{date_label}，日常生活中的親密一瞬，溫柔記錄家庭記憶。"
    if category == 'festival':
        return f"{date_label}，節慶氛圍滿溢，歡聚的光影與美好瞬間。"
    if category == 'travel':
        if '日本' in description or 'tokyo' in description.lower():
            return f"{date_label}，在櫻花城市裡漫步，旅行記憶如夢似幻。"
        if '歐洲' in description or '巴黎' in description.lower():
            return f"{date_label}，歐風街景與午後光線，構成浪漫旅程。"
        if '東南亞' in description or '泰國' in description.lower():
            return f"{date_label}，熱帶色彩與旅程熱情交織在畫面中。"
        return f"{date_label}，旅行中的精彩瞬間，光影與場景共同講述故事。"
    return f"{date_label}，這張相片藏著珍貴的回憶與情感。"


def build_photo_records(project_root: Path, analysis_data: dict, output_web: Path) -> dict:
    selected = {}
    photos_dir = output_web / 'photos'
    photos_dir.mkdir(parents=True, exist_ok=True)

    for category, items in analysis_data.items():
        chosen = select_top_photos(items, limit=30)
        records = []
        for item in chosen:
            src_path = Path(item['path'])
            suffix = src_path.suffix.lower()
            if suffix in ['.heic', '.heif']:
                image_bytes, mime_type = ImageConverter.get_image_data(str(src_path))
                if image_bytes is None:
                    continue
                dest_name = src_path.stem + '.jpg'
                dest_path = photos_dir / dest_name
                with open(dest_path, 'wb') as f:
                    f.write(image_bytes)
            else:
                dest_name = src_path.name
                dest_path = photos_dir / dest_name
                if not dest_path.exists():
                    try:
                        shutil.copy2(str(src_path), str(dest_path))
                    except Exception:
                        continue

            location_label, theme_key = infer_location_label(item.get('description', ''), category)
            record = {
                'filename': dest_name,
                'url': f'photos/{dest_name}',
                'description': item.get('description', ''),
                'caption': generate_caption(item, category),
                'date': parse_date_from_path(item.get('path', '')),
                'location': location_label,
                'members': item.get('family_members', []),
                'confidence': item.get('confidence', 0),
                'theme': theme_key,
                'category': category
            }
            records.append(record)

        selected[category] = records
    return selected


def build_page_data(project_root: Path, selected_photos: dict) -> dict:
    hero_images = {}
    for category, records in selected_photos.items():
        hero = records[0] if records else None
        hero_images[category] = hero
    return {
        'counts': {cat: len(recs) for cat, recs in selected_photos.items()},
        'hero_images': hero_images,
        'pages': selected_photos
    }


def css_block() -> str:
    return """<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Noto+Serif+TC:wght@400;500;600&display=swap');
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Noto Serif TC', serif; background: #f8f2ed; color: #2f2f2f; }
    a { color: inherit; text-decoration: none; }
    .page-shell { min-height: 100vh; overflow-x: hidden; }
    .hero { position: relative; min-height: 60vh; display: flex; align-items: flex-end; justify-content: flex-start; padding: 40px; background-size: cover; background-position: center; background-attachment: fixed; }
    .hero::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(29, 19, 13, 0.18), rgba(29, 19, 13, 0.74)); }
    .hero-content { position: relative; max-width: 720px; z-index: 1; }
    .section-header { margin-bottom: 24px; }
    .tag { background: rgba(212, 146, 108, 0.18); color: #8c5a3f; }
    .card img { width: 100%; display: block; border-bottom: 1px solid rgba(180, 154, 129, 0.18); filter: saturate(1.04) contrast(1.03); }
    .card { animation: fadeInUp 0.8s ease both; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }
    .hero-title { font-family: 'Playfair Display', serif; font-size: clamp(3rem, 5vw, 5rem); margin: 0; letter-spacing: 0.05em; line-height: 1; color: #fff; text-shadow: 0 18px 45px rgba(0,0,0,0.35); }
    .hero-subtitle { margin-top: 16px; font-size: 1.05rem; color: rgba(255,255,255,0.88); max-width: 560px; }
    .section-intro { padding: 30px 40px 20px; max-width: 1200px; margin: 0 auto; }
    .nav-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 30px; }
    .nav-card { background: #fff; border-radius: 24px; border: 1px solid rgba(63, 63, 63, 0.08); padding: 28px; box-shadow: 0 18px 65px rgba(58, 39, 29, 0.08); transition: transform 0.35s ease, box-shadow 0.35s ease; }
    .nav-card:hover { transform: translateY(-8px); box-shadow: 0 30px 80px rgba(58, 39, 29, 0.14); }
    .nav-label { font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.2em; color: #9f7b61; margin-bottom: 10px; }
    .nav-title { font-family: 'Playfair Display', serif; font-size: 1.7rem; margin: 0 0 12px; }
    .nav-meta { color: #6f645b; font-size: 0.95rem; }
    .gallery { column-count: 3; column-gap: 22px; padding: 20px 40px 50px; max-width: 1400px; margin: 0 auto; }
    .card { break-inside: avoid; margin-bottom: 22px; position: relative; border-radius: 28px; overflow: hidden; background: #fff; box-shadow: 0 28px 70px rgba(76, 56, 46, 0.09); transform: translateY(0); transition: transform 0.35s ease, box-shadow 0.35s ease; }
    .card:hover { transform: translateY(-12px); box-shadow: 0 40px 100px rgba(76, 56, 46, 0.16); }
    .card img { width: 100%; display: block; border-bottom: 1px solid rgba(180, 154, 129, 0.18); }
    .card-meta { padding: 18px 20px 22px; }
    .tag-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
    .tag { display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; background: rgba(212, 146, 108, 0.16); color: #8c5a3f; font-size: 0.82rem; }
    .tag span { font-weight: 700; }
    .caption { margin: 0; font-size: 1rem; line-height: 1.7; color: #4e4036; }
    .meta-bar { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px; margin-top: 16px; color: #7b6b61; font-size: 0.9rem; }
    .lightbox { position: fixed; inset: 0; background: rgba(18, 18, 18, 0.9); display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; transition: opacity 0.25s ease; z-index: 50; }
    .lightbox.active { opacity: 1; visibility: visible; }
    .lightbox-content { position: relative; max-width: 95vw; max-height: 95vh; width: 100%; }
    .lightbox img { width: 100%; height: auto; display: block; border-radius: 24px; }
    .lightbox-close, .lightbox-nav button { position: absolute; border: none; background: rgba(255,255,255,0.16); color: #fff; backdrop-filter: blur(6px); border-radius: 999px; cursor: pointer; padding: 12px 16px; transition: transform 0.25s ease; }
    .lightbox-close:hover, .lightbox-nav button:hover { transform: scale(1.05); }
    .lightbox-close { top: 20px; right: 20px; }
    .lightbox-nav { bottom: 24px; left: 50%; transform: translateX(-50%); display: flex; gap: 14px; }
    .password-overlay { position: fixed; inset: 0; background: rgba(22, 22, 22, 0.95); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 20px; }
    .password-panel { max-width: 420px; width: 100%; background: #fff; border-radius: 28px; padding: 34px; box-shadow: 0 30px 80px rgba(29, 19, 14, 0.16); }
    .password-panel h2 { margin: 0 0 18px; font-family: 'Playfair Display', serif; font-size: 2rem; color: #33241f; }
    .password-panel p { margin: 0 0 24px; color: #6f5f55; line-height: 1.75; }
    .password-input { width: 100%; padding: 16px 18px; border-radius: 16px; border: 1px solid #d7ccc8; font-size: 1rem; outline: none; }
    .password-button { width: 100%; margin-top: 18px; padding: 16px; border-radius: 16px; border: none; font-size: 1rem; background: #d4795a; color: white; font-weight: 700; cursor: pointer; }
    .password-error { margin-top: 14px; color: #b74528; font-size: 0.95rem; min-height: 1.2em; }
    .footer { padding: 30px 40px 50px; max-width: 1200px; margin: 0 auto; color: #6f645b; font-size: 0.95rem; }
    @media (max-width: 1100px) { .gallery { column-count: 2; } }
    @media (max-width: 760px) { .hero { min-height: 48vh; padding: 24px; } .nav-grid { grid-template-columns: 1fr; } .gallery { column-count: 1; padding: 16px; } .password-panel { padding: 28px; } }
</style>"""


def js_block() -> str:
    script = """<script>
    const passwordHash = '{PASSWORD_HASH}';
    const passwordOverlay = document.querySelector('.password-overlay');
    const passwordInput = document.querySelector('#password-input');
    const passwordError = document.querySelector('.password-error');

    async function sha256(text) {
        const encoder = new TextEncoder();
        const data = encoder.encode(text);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        return Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, '0')).join('');
    }

    async function verifyPassword() {
        const value = passwordInput.value.trim();
        const hash = await sha256(value);
        if (hash === passwordHash) {
            passwordOverlay.style.display = 'none';
            localStorage.setItem('album-unlocked', '1');
            return;
        }
        passwordError.textContent = '密碼錯誤，請再試一次。';
    }

    async function checkPasswordState() {
        const unlocked = localStorage.getItem('album-unlocked');
        if (unlocked === '1') {
            passwordOverlay.style.display = 'none';
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        checkPasswordState();
        document.querySelector('#password-submit').addEventListener('click', async () => {
            await verifyPassword();
        });
        passwordInput.addEventListener('keydown', async (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                await verifyPassword();
            }
        });

        const cards = document.querySelectorAll('.card');
        const lightbox = document.querySelector('.lightbox');
        const lightboxImg = document.querySelector('.lightbox img');
        const closeButton = document.querySelector('.lightbox-close');
        const prevButton = document.querySelector('.lightbox-prev');
        const nextButton = document.querySelector('.lightbox-next');
        let currentIndex = 0;
        let currentList = [];

        cards.forEach((card, index) => {
            currentList.push(card.querySelector('img').src);
            card.addEventListener('click', () => {
                currentIndex = index;
                openLightbox(currentList[currentIndex]);
            });
        });

        function openLightbox(src) {
            lightbox.classList.add('active');
            lightboxImg.src = src;
            document.body.style.overflow = 'hidden';
        }

        function closeLightbox() {
            lightbox.classList.remove('active');
            document.body.style.overflow = 'auto';
        }

        function nextPhoto() {
            currentIndex = (currentIndex + 1) % currentList.length;
            openLightbox(currentList[currentIndex]);
        }

        function prevPhoto() {
            currentIndex = (currentIndex - 1 + currentList.length) % currentList.length;
            openLightbox(currentList[currentIndex]);
        }

        closeButton.addEventListener('click', closeLightbox);
        nextButton.addEventListener('click', nextPhoto);
        prevButton.addEventListener('click', prevPhoto);
        lightbox.addEventListener('click', (event) => {
            if (event.target === lightbox) closeLightbox();
        });

        document.addEventListener('keydown', (event) => {
            if (!lightbox.classList.contains('active')) return;
            if (event.key === 'ArrowRight') nextPhoto();
            if (event.key === 'ArrowLeft') prevPhoto();
            if (event.key === 'Escape') closeLightbox();
        });
    });
</script>"""
    return script.replace('{PASSWORD_HASH}', PASSWORD_HASH)


def generate_index_page(data: dict, output_web: Path) -> str:
    cards = []
    for category, page_name in CATEGORY_PAGE_MAP.items():
        title = PAGE_TITLES['family'] if category == 'family' else PAGE_TITLES['travel'] if category == 'travel' else PAGE_TITLES['festival']
        hero = data['hero_images'].get(category)
        theme_key = hero['theme'] if hero else 'local'
        theme = THEME_CONFIG[theme_key]
        cards.append(f"""
        <a class='nav-card' href='{page_name}'>
            <div class='nav-label'>{theme['label']}</div>
            <h2 class='nav-title'>{title}</h2>
            <p class='nav-meta'>{data['counts'][category]} 張精選相片</p>
        </a>
        """)

    return f"""<!DOCTYPE html>
<html lang='zh-TW'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{PAGE_TITLES['index']}</title>
{css_block()}
</head>
<body>
<div class='page-shell'>
    <div class='hero' style='background-image:url("{data['hero_images']['family']['url'] if data['hero_images']['family'] else ""}");'>
        <div class='hero-content'>
            <p class='nav-label'>2026 精選相冊</p>
            <h1 class='hero-title'>溫暖旅誌 · 家庭相冊</h1>
            <p class='hero-subtitle'>從家庭、旅遊到節慶，每一張都是 Claude 為你挑選的最佳故事畫面。</p>
        </div>
    </div>
    <section class='section-intro'>
        <div class='section-header'>
            <p class='tag'>精緻旅遊雜誌風</p>
            <h2 class='hero-title' style='font-size:2.4rem;'>三大主題 · 專屬故事</h2>
        </div>
        <div class='nav-grid'>{''.join(cards)}</div>
    </section>
    <footer class='footer'>
        本站使用 SHA-256 密碼保護（密碼：0829），並採用 Masonry 瀑布流、視差封面與燈箱展示。
    </footer>
</div>
<div class='password-overlay'>
    <div class='password-panel'>
        <h2>輸入密碼查看相冊</h2>
        <p>這是您專屬的家庭與旅遊相冊，請輸入一次性訪問密碼。</p>
        <input id='password-input' class='password-input' type='password' placeholder='請輸入密碼'>
        <button id='password-submit' class='password-button'>解鎖相冊</button>
        <div class='password-error'></div>
    </div>
</div>
{js_block()}
</body>
</html>"""


def generate_category_page(category: str, records: list, output_web: Path) -> str:
    page_key = 'festival' if category == 'celebration' else category
    title = PAGE_TITLES[page_key]
    hero = records[0] if records else None
    theme = THEME_CONFIG[hero['theme'] if hero else 'local']

    cards_html = []
    for record in records:
        member_label = ' / '.join(record['members']) if record['members'] else record['location']
        cards_html.append(f"""
        <div class='card'>
            <img src='{record['url']}' alt='{record['caption']}' loading='lazy'>
            <div class='card-meta'>
                <div class='tag-row'>
                    <div class='tag'><span>{record['date']}</span></div>
                    <div class='tag'><span>{record['location']}</span></div>
                </div>
                <p class='caption'>{record['caption']}</p>
                <div class='meta-bar'>
                    <span>{member_label}</span>
                    <span>信心度 {record['confidence']}%</span>
                </div>
            </div>
        </div>
        """)

    return f"""<!DOCTYPE html>
<html lang='zh-TW'>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{title}</title>
{css_block()}
</head>
<body>
<div class='page-shell'>
    <div class='hero' style='background-image:url("{hero['url'] if hero else ''}");'>
        <div class='hero-content'>
            <p class='nav-label'>{theme['label']}</p>
            <h1 class='hero-title'>{title}</h1>
            <p class='hero-subtitle'>精選 {len(records)} 張最佳相片，呈現最美的光影與故事。</p>
        </div>
    </div>
    <section class='section-intro'>
        <div class='section-header'>
            <p class='tag'>風格：精緻旅遊雜誌 · 溫暖色調</p>
            <h2 class='hero-title' style='font-size:2.4rem;'>每張相片皆為 Claude 精選</h2>
        </div>
    </section>
    <div class='gallery'>
        {''.join(cards_html)}
    </div>
    <footer class='footer'>
        點擊相片即可放大預覽，使用方向鍵切換上下張，並支援鍵盤關閉。
    </footer>
</div>
<div class='lightbox'>
    <div class='lightbox-content'>
        <img src='' alt=''>
        <button class='lightbox-close'>&times;</button>
        <div class='lightbox-nav'>
            <button class='lightbox-prev'>上一張</button>
            <button class='lightbox-next'>下一張</button>
        </div>
    </div>
</div>
<div class='password-overlay'>
    <div class='password-panel'>
        <h2>輸入密碼查看相冊</h2>
        <p>這是您專屬的家庭與旅遊相冊，請輸入一次性訪問密碼。</p>
        <input id='password-input' class='password-input' type='password' placeholder='請輸入密碼'>
        <button id='password-submit' class='password-button'>解鎖相冊</button>
        <div class='password-error'></div>
    </div>
</div>
{js_block()}
</body>
</html>"""


def save_page(html: str, filename: str, output_web: Path):
    path = output_web / filename
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    project_root = Path(__file__).resolve().parent.parent
    settings = parse_claude_settings(project_root)
    output_web = Path(settings['output'].replace('\\', '/'))
    output_web.mkdir(parents=True, exist_ok=True)

    analysis_data = load_analysis_data(project_root)
    selected_photos = build_photo_records(project_root, analysis_data, output_web)
    page_data = build_page_data(project_root, selected_photos)

    save_page(generate_index_page(page_data, output_web), 'index.html', output_web)
    save_page(generate_category_page('family', selected_photos['family'], output_web), 'family.html', output_web)
    save_page(generate_category_page('travel', selected_photos['travel'], output_web), 'travel.html', output_web)
    save_page(generate_category_page('celebration', selected_photos['celebration'], output_web), 'festival.html', output_web)

    print('✓ 已生成完整相冊網站：', output_web)
    print('  - index.html')
    print('  - family.html')
    print('  - travel.html')
    print('  - festival.html')
    print('  - photos/  已匯出選定相片')


if __name__ == '__main__':
    main()
