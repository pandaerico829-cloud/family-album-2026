@echo off
REM 快速 Git 设置脚本
REM 下载并安装 Git: https://git-scm.com/download/win

echo 🔍 检查 Git 是否已安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Git 未安装
    echo.
    echo 请访问下载并安装:
    echo 🔗 https://git-scm.com/download/win
    echo.
    echo 使用默认选项安装即可
    echo.
    pause
    exit /b 1
)

echo ✓ Git 已安装
echo.
echo 📁 初始化 Git 仓库...
cd /d "%~dp0"
git init
git config user.name "Family Album"
git config user.email "album@example.com"

echo.
echo 📝 添加所有文件...
git add .

echo.
echo 💾 首次提交...
git commit -m "🎉 初始化智能家庭相冊 2026

处理相片：381 张
活动分群：4 个
- 1-2月活动
- 2-3月活动  
- 4-5月活动
- 日常生活

生成功能：
- 精緻雜誌風設計
- Masonry 瀑布流佈局
- 响应式网页
- 密码保护 (0829)"

echo.
echo ✅ Git 初始化完成！
echo.
echo 📌 下一步：
echo 1. 访问 GitHub 创建新 repository: family-album-2026
echo 2. 执行以下命令：
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/family-album-2026.git
echo    git branch -M main
echo    git push -u origin main
echo.
pause
