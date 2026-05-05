@echo off
REM Windows 自動化腳本 - 初始化 Git 和推送到 GitHub

echo.
echo ===== 家庭相冊 2026 - Git 初始化 =====
echo.

REM 檢查 git 是否安裝
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git 未安裝
    echo.
    echo 請下載並安裝 Git:
    echo 🔗 https://git-scm.com/download/win
    echo.
    echo 安裝後請重新執行此腳本
    echo.
    pause
    exit /b 1
)

echo ✓ Git 已安裝
echo.

REM 初始化倉庫
echo 📁 初始化 Git 倉庫...
git init
git config user.name "Claude"
git config user.email "claude@album-2026.local"
echo ✓ Git 倉庫已初始化
echo.

REM 添加檔案
echo 📝 添加所有檔案...
git add .
echo ✓ 檔案已添加
echo.

REM 首次提交
echo 💾 首次提交...
git commit -m "🎉 初始化家庭相冊 2026 項目

- 家庭相冊: 30 張精選相片
- 雜誌風設計，溫暖色調
- 密碼保護，SHA-256 加密
- 響應式 Masonry 佈局"
echo ✓ 首次提交完成
echo.

REM 後續步驟
echo ===== 📌 後續步驟 =====
echo.
echo 1️⃣  在 GitHub 上建立新 repository
echo    - 名稱: family-album-2026
echo    - 隱私: Private (推薦)
echo.
echo 2️⃣  將遠程倉庫連結到此專案
echo    git remote add origin https://github.com/YOUR_USERNAME/family-album-2026.git
echo.
echo 3️⃣  推送到 GitHub
echo    git branch -M main
echo    git push -u origin main
echo.
echo ✓ 所有步驟完成！
echo.
pause
