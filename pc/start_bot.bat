@echo off
chcp 65001 >nul 2>&1
title Discord Bot

echo ========================================
echo    Discord Bot 起動スクリプト
echo ========================================
echo.

:: Python の存在チェック
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python が見つかりません。
    echo    https://www.python.org/downloads/ からインストールしてください。
    echo    インストール時に「Add Python to PATH」にチェックを入れてください。
    pause
    exit /b 1
)

:: .env ファイルの存在チェック
if not exist ".env" (
    echo ⚠️  .env ファイルが見つかりません。
    echo    セットアップウィザードを実行します...
    echo.
    python setup_wizard.py
    if %ERRORLEVEL% neq 0 (
        echo セットアップに失敗しました。
        pause
        exit /b 1
    )
)

:: 依存パッケージのチェック
echo 📦 依存パッケージを確認中...
python -c "import discord" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 📦 依存パッケージをインストール中...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo ⚠️  インストールに失敗しました。
        echo    手動で pip install -r requirements.txt を実行してください。
        pause
        exit /b 1
    )
)

:: Bot 起動
echo.
echo 🚀 Bot を起動します...
echo    停止するには Ctrl+C を押してください。
echo.
python main.py

:: エラーで終了した場合
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Bot がエラーで停止しました。
    echo    エラー内容を確認して修正してください。
    echo    /doctor コマンドで診断もできます。
)

pause
