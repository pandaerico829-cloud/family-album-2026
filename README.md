# 🏠 家庭相冊 2026

精緻的家庭相冊網站，包含密碼保護、雜誌風設計和自動組織功能。

**Repository**: family-album-2026 | **狀態**: 開發中 (家庭相冊已完成 ✅)

## ✨ 功能特性

- 🤖 **AI視覺分析**: 使用GPT-4V、Google Vision等自動識別相片內容
- 📂 **自動分類**: 智能分類為家庭成員、旅遊和節慶三大類
- 🎨 **漂亮展示**: 響應式HTML相冊，手機和桌面完美適配
- 🔐 **密碼保護**: 一次登錄即可訪問所有相冊
- 📱 **移動優化**: 完美支持手機、平板、電腦
- 🌐 **一鍵部署**: 支持本地和雲端部署

## 📋 系統要求

- Python 3.8+
- 網際網路連接（用於API調用）
- 相冊原始相片（支持HEIC、JPG、PNG等格式）

## 🚀 快速開始

### 1. 初始化配置

編輯 `config.json` 配置文件：

```json
{
  "source_path": "C:\\Users\\育源\\OneDrive\\Pictures\\相機膠卷\\2026",
  "output_path": "D:\\ClaudeProjects\\Album_Reorganize\\output",
  "api_config": {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "model": "gpt-4-vision-preview"
  },
  "password": "0829"
}
```

### 2. 安裝依賴

```bash
# 方式1: 使用菜單
python run.py
# 選擇選項 1

# 方式2: 直接安裝
pip install -r requirements.txt
```

### 3. 整理相冊

```bash
# 方式1: 使用菜單
python run.py
# 選擇選項 2

# 方式2: 直接運行
python organize.py
```

這將執行以下步驟：
- ✓ 掃描並複製相片
- ✓ 用AI分析每張相片
- ✓ 自動分類到三個分類
- ✓ 生成HTML相冊網頁

### 4. 啟動本地服務器

```bash
# 方式1: 使用菜單
python run.py
# 選擇選項 3，輸入端口號（默認5000）

# 方式2: 直接運行
python -c "from src.protected_server import ProtectedAlbumServer; s = ProtectedAlbumServer('./output/web', '0829', 5000); s.run()"
```

訪問 http://localhost:5000，輸入密碼 `0829` 即可查看相冊。

## 🔑 API 配置指南

### 使用 OpenAI GPT-4V

1. 獲取API密鑰: https://platform.openai.com/api-keys

2. 編輯 `config.json`:
```json
{
  "api_config": {
    "provider": "openai",
    "api_key": "sk-...",
    "model": "gpt-4-vision-preview"
  }
}
```

### 使用 Google Vision API

1. 設置Google Cloud: https://cloud.google.com/vision/docs/setup

2. 編輯 `config.json`:
```json
{
  "api_config": {
    "provider": "google",
    "api_key": "your-google-api-key"
  }
}
```

### 模擬分析（測試用）

如果不配置API密鑰，系統將使用模擬分析進行隨機分類（用於開發和測試）。

## 📁 項目結構

```
Album_Reorganize/
├── organize.py              # 主程序入口
├── run.py                   # 啟動腳本
├── config.json              # 配置文件
├── requirements.txt         # Python依賴
├── README.md                # 說明文檔
├── src/
│   ├── analyzer.py          # 圖像分析模塊
│   ├── html_generator.py    # HTML生成器
│   └── protected_server.py  # 密碼保護服務器
├── photos/
│   ├── original/            # 複製的原始相片
│   └── classified/          # 分類後的相片（可選）
├── output/
│   ├── web/                 # 生成的HTML相冊
│   │   ├── index.html       # 主頁面
│   │   ├── family.html      # 家庭成員相冊
│   │   ├── travel.html      # 旅遊相冊
│   │   └── celebration.html # 節慶相冊
│   └── analysis_data.json   # 分析結果數據
└── SUMMARY.txt              # 整理摘要報告
```

## 🎨 相冊分類說明

### 📸 家庭成員 (Family)
- 日常生活照
- 人物照片
- 家庭成員合照
- 室內活動

### ✈️ 旅遊 (Travel)
- 風景名勝
- 旅遊地點
- 出遊活動
- 景點照片

### 🎉 節慶聚餐 (Celebration)
- 節日慶祝
- 聚餐活動
- 吃飯聚會
- 特殊活動

## 🔐 密碼保護

### 本地訪問
1. 啟動服務器: `python run.py` → 選項3
2. 訪問 http://localhost:5000
3. 輸入密碼: `0829`

### 遠程訪問/部署

#### 方式1: Vercel 部署

1. 將相冊推送到GitHub
2. 連接Vercel: https://vercel.com
3. 部署Flask應用
4. 自動生成固定URL

#### 方式2: Heroku 部署

```bash
# 安裝Heroku CLI
heroku login
heroku create your-album-name
git push heroku main
heroku open
```

#### 方式3: 自建服務器

在個人服務器上運行：
```bash
python run.py
# 選擇選項 3，啟動服務器
# 配置域名和SSL證書
```

## 💡 高級用法

### 批量処理多年份相冊

編輯 `config.json` 中的 `source_path`:

```json
{
  "source_path": "C:\\Users\\育源\\OneDrive\\Pictures\\相機膠卷"
}
```

### 自定義分類

編輯 `config.json`:

```json
{
  "categories": {
    "family": "家庭成員（日常、人物）",
    "travel": "旅遊（出遊、景點）",
    "celebration": "節慶聚餐（過節、吃飯、聚會）"
  }
}
```

### 修改密碼

編輯 `config.json`:

```json
{
  "password": "new-password-here"
}
```

## 🐛 故障排除

### 相片無法識別

- 確認相片格式受支持（JPG、PNG、HEIC等）
- 檢查API密鑰配置
- 查看 `SUMMARY.txt` 中的詳細日誌

### 服務器無法啟動

```bash
# 檢查端口是否被佔用
netstat -ano | findstr :5000

# 使用不同端口
python run.py
# 選擇選項 3，輸入新端口如 8000
```

### API 調用失敗

- 驗證API密鑰有效性
- 檢查網際網路連接
- 確認API額度未超出

## 📊 分析結果

整理完成後，查看 `output/analysis_data.json` 了解每張相片的分類結果：

```json
{
  "family": [
    {
      "path": "photos/original/photo_001.jpg",
      "description": "家庭合照",
      "family_members": ["爸爸", "媽媽"],
      "confidence": 92,
      "reason": "多人合照，室內環境"
    }
  ]
}
```

## 🎯 工作流程

```
相機相片
    ↓
[步驟1] 複製到本地
    ↓
[步驟2] AI視覺分析
    ↓
[步驟3] 自動分類
    ↓
[步驟4] 生成HTML相冊
    ↓
[步驟5] 密碼保護
    ↓
[步驟6] 部署到網路
    ↓
✓ 完成！可供訪問
```

## 📈 性能指標

- **分析速度**: ~1-2秒/張相片（取決於API）
- **生成速度**: ~5秒（所有相冊）
- **存儲空間**: 原始相片 + ~5MB HTML
- **加載時間**: <2秒（10Mbps網速）

## 🤝 貢獻

歡迎提出建議和改進！

## 📄 許可證

MIT License - 個人和商業使用均可

## 📞 支持

如有問題，請：
1. 查看 `SUMMARY.txt` 日誌
2. 檢查 `config.json` 配置
3. 查看本文檔故障排除部分

---

**最後更新**: 2026年5月4日

💝 珍貴的家庭回憶值得精心保存！
