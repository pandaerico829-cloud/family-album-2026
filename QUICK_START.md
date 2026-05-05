# 🚀 快速開始指南

## ⚡ 5分鐘快速上手

### 步驟 1: 檢查配置 ✓

編輯 `config.json`，確保路徑正確：

```json
{
  "source_path": "C:\\Users\\User\\OneDrive\\Pictures\\相機膠卷\\2026",
  "output_path": "D:\\ClaudeProjects\\Album_Reorganize\\output",
  "password": "0829"
}
```

### 步驟 2: 安裝依賴

```bash
# 打開命令提示符或PowerShell，進入項目目錄
cd D:\ClaudeProjects\Album_Reorganize

# 安裝Python依賴
pip install -r requirements.txt
```

### 步驟 3: 運行整理程序

```bash
# 方式1: 使用交互菜單（推薦新手）
python run.py
# 選擇選項 4（安裝+整理+啟動一鍵完成）

# 方式2: 直接運行整理
python organize.py
```

### 步驟 4: 啟動本地預覽

```bash
# 運行後會自動啟動服務器
# 或手動啟動
python -c "from src.protected_server import ProtectedAlbumServer; s = ProtectedAlbumServer('./output/web', '0829', 5000); s.run()"
```

### 步驟 5: 訪問相冊

打開瀏覽器，訪問：
- **地址**: http://localhost:5000
- **密碼**: 0829

---

## 📋 詳細步驟

### 步驟 A: 驗證相片位置

```bash
# PowerShell/命令提示符
Get-ChildItem "C:\Users\User\OneDrive\Pictures\相機膠卷\2026\" | Measure-Object

# 應該看到 379 個項目
```

### 步驟 B: 配置API（可選）

如果需要真實AI分析而不是隨機分類，配置API密鑰：

#### 使用 OpenAI GPT-4V（推薦）

1. 獲取API密鑰: https://platform.openai.com/api-keys
2. 編輯 `config.json`:

```json
{
  "api_config": {
    "provider": "openai",
    "api_key": "sk-your-key-here",
    "model": "gpt-4-vision-preview"
  }
}
```

### 步驟 C: 運行並等待

```bash
python organize.py
```

預計耗時：
- 無API配置：2-5分鐘（模擬分析）
- 有OpenAI API：15-30分鐘（379張相片）

### 步驟 D: 查看結果

完成後會生成：

```
output/
├── web/
│   ├── index.html         ← 打開這個看相冊
│   ├── family.html
│   ├── travel.html
│   └── celebration.html
└── analysis_data.json     ← 分類詳情
```

---

## 🎯 下一步

### 部署到線上（固定網址）

#### 使用 Replit（免費，推薦）

1. 訪問 https://replit.com
2. 新建項目，上傳所有文件
3. 運行 `python run.py`
4. 選擇選項 3
5. 自動生成公開URL

#### 使用 PythonAnywhere（免費）

1. 訪問 https://www.pythonanywhere.com
2. 上傳項目
3. 配置Web app
4. 獲得固定網址 (xxxx.pythonanywhere.com)

#### 使用自己的服務器

在服務器上運行：

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行（後台）
nohup python run.py &

# 配置域名和SSL
```

---

## 🔧 常見問題

### Q: 為什麼相片分類是隨機的？

A: 沒有配置API密鑰。編輯 `config.json` 添加 OpenAI API密鑰。

### Q: 端口 5000 被佔用怎麼辦？

```bash
# 使用其他端口
python run.py
# 選擇選項 3，輸入端口號如 8000
```

### Q: 相片沒有複製怎麼辦？

確保源路徑正確：
```bash
# 驗證路徑
Get-ChildItem "C:\Users\User\OneDrive\Pictures\相機膠卷\2026\"
```

---

## 📊 流程圖

```
開始
  ↓
安裝依賴 (pip install)
  ↓
配置 config.json
  ↓
運行整理程序 (python organize.py)
  ├─ 複製相片
  ├─ 分析相片 (AI或模擬)
  ├─ 分類相片
  └─ 生成HTML
  ↓
查看結果 (output/web/)
  ↓
啟動服務器 (python -m flask...)
  ↓
訪問 http://localhost:5000
  ↓
輸入密碼: 0829
  ↓
✓ 完成！
```

---

## 💡 最佳實踐

1. **首次測試**: 先用5-10張相片測試
2. **檢查分類**: 查看 `analysis_data.json` 確認分類質量
3. **調整設置**: 如需要，修改 `config.json` 中的提示詞
4. **部署前驗**: 在本地充分測試後再部署
5. **定期備份**: 保存 `analysis_data.json` 和 `output/web/`

---

## 🎨 自定義

### 修改相冊標題

編輯 `config.json`:
```json
{
  "web_config": {
    "title": "我的家庭相冊"
  }
}
```

### 修改分類名稱

編輯 `config.json`:
```json
{
  "categories": {
    "family": "家庭照片",
    "travel": "旅遊記錄",
    "celebration": "聚會活動"
  }
}
```

### 修改密碼

編輯 `config.json`:
```json
{
  "password": "你的密碼"
}
```

---

## 🆘 需要幫助？

1. 檢查 `output/SUMMARY.txt` 查看詳細日誌
2. 閱讀 `README.md` 完整文檔
3. 查看錯誤信息的具體內容

---

**祝你使用愉快！** 💝
