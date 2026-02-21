#!/bin/bash
# Discord Bot 起動スクリプト (Mac/Linux)

echo "========================================"
echo "   Discord Bot 起動スクリプト"
echo "========================================"
echo ""

# Python の存在チェック
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 が見つかりません。"
    echo "   sudo apt install python3 python3-pip  (Ubuntu/Debian)"
    echo "   brew install python                   (macOS)"
    exit 1
fi

# .env ファイルの存在チェック
if [ ! -f ".env" ]; then
    echo "⚠️  .env ファイルが見つかりません。"
    echo "   セットアップウィザードを実行します..."
    echo ""
    python3 setup_wizard.py
    if [ $? -ne 0 ]; then
        echo "セットアップに失敗しました。"
        exit 1
    fi
fi

# 依存パッケージの確認
echo "📦 依存パッケージを確認中..."
python3 -c "import discord" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 依存パッケージをインストール中..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "⚠️  インストールに失敗しました。"
        echo "   手動で pip3 install -r requirements.txt を実行してください。"
        exit 1
    fi
fi

# Bot 起動
echo ""
echo "🚀 Bot を起動します..."
echo "   停止するには Ctrl+C を押してください。"
echo ""
python3 main.py
