@echo off
chcp 65001 >nul
echo ========================================
echo   🚀 AI Prompt Lab - Git 初始化脚本
echo ========================================
echo.

REM 检查是否已经初始化
if exist .git (
    echo ⚠️  Git 仓库已存在！
    echo.
    choice /C YN /M "是否要重新初始化？这将删除现有的 Git 历史"
    if errorlevel 2 goto :END
    if errorlevel 1 (
        echo 正在删除现有 Git 仓库...
        rmdir /s /q .git
    )
)

echo.
echo [1/6] 📝 初始化 Git 仓库...
git init
if errorlevel 1 (
    echo ❌ Git 初始化失败！请确保已安装 Git。
    goto :END
)

echo.
echo [2/6] 📋 添加所有文件...
git add .
if errorlevel 1 (
    echo ❌ 添加文件失败！
    goto :END
)

echo.
echo [3/6] 💾 创建初始提交...
git commit -m "🎉 Initial commit: AI Prompt Lab v1.0

Features:
- ✨ Prompt 管理和版本控制
- 🧪 A/B 测试对比
- 📚 模板库系统
- 🔒 安全和权限管理
- 🎨 现代化 UI 设计
- 📝 完整的部署文档
- 🧪 用户级 Prompt 收藏隔离"
if errorlevel 1 (
    echo ❌ 提交失败！
    goto :END
)

echo.
echo [4/6] 🌿 设置主分支为 main...
git branch -M main

echo.
echo [5/6] 🔗 关联远程仓库...
echo.
set /p REPO_URL="请输入你的 GitHub 仓库地址 (例如: https://github.com/username/ai-prompt-lab.git): "

if "%REPO_URL%"=="" (
    echo ⚠️  未输入仓库地址，跳过关联远程仓库
    goto :SHOW_COMMANDS
)

git remote add origin %REPO_URL%
if errorlevel 1 (
    echo ⚠️  添加远程仓库失败，可能已存在
    git remote set-url origin %REPO_URL%
)

echo.
echo [6/6] 📤 推送到 GitHub...
choice /C YN /M "是否现在推送到 GitHub"
if errorlevel 2 goto :SHOW_COMMANDS
if errorlevel 1 (
    git push -u origin main
    if errorlevel 1 (
        echo ❌ 推送失败！
        echo 💡 请检查：
        echo    1. 仓库地址是否正确
        echo    2. 是否有推送权限
        echo    3. 是否需要先登录 GitHub
        goto :SHOW_COMMANDS
    )
    echo.
    echo ✅ 推送成功！
)

:SHOW_COMMANDS
echo.
echo ========================================
echo   ✅ Git 初始化完成！
echo ========================================
echo.
echo 📚 常用 Git 命令:
echo.
echo   查看状态:     git status
echo   添加文件:     git add .
echo   提交更改:     git commit -m "描述"
echo   推送代码:     git push
echo   拉取代码:     git pull
echo   查看历史:     git log --oneline
echo   创建分支:     git checkout -b 分支名
echo.
echo 🔗 仓库地址: %REPO_URL%
echo.
echo 💡 下一步:
echo   1. 访问 GitHub 仓库查看代码
echo   2. 在 GitHub 添加 README badges
echo   3. 设置 GitHub Pages (可选)
echo   4. 添加 LICENSE 文件 (可选)
echo.

:END
pause

