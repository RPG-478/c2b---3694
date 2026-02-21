#!/usr/bin/env python3
"""
C2B Bot セットアップウィザード
==============================
初心者がBotを初めて起動する前に実行するスクリプトです。
対話形式で以下を自動設定します:
  1. .env ファイル作成（トークン設定）
  2. 依存パッケージのインストール
  3. Discord Developer Portal の設定ガイド
  4. 接続テスト

使い方: python setup_wizard.py

📱 スマホしかない方へ:
  このスクリプトはPC向けです。
  スマホで Bot を動かす場合は MOBILE_GUIDE.md を読んでください。
  Replit を使えばもっと簡単にセットアップできます！
"""
import os
import sys
import subprocess
import re

# ──────────────────────────────────────────────
# ヘルパー関数
# ──────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title: str):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)

def print_step(step: int, total: int, desc: str):
    print(f"\n{'─' * 50}")
    print(f"  📌 Step {step}/{total}: {desc}")
    print(f"{'─' * 50}")

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        ans = input(prompt + suffix).strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes", "はい"):
            return True
        if ans in ("n", "no", "いいえ"):
            return False
        print("  → 'y' または 'n' で答えてください。")

def validate_token(token: str) -> bool:
    """Discord Bot トークンの簡易バリデーション"""
    token = token.strip()
    if len(token) < 50:
        return False
    # Discord token format: base64.base64.base64 (roughly)
    parts = token.split(".")
    if len(parts) != 3:
        return False
    return True


# ──────────────────────────────────────────────
# メイン処理
# ──────────────────────────────────────────────

def main():
    clear()
    print(r"""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║    🤖 Discord Bot セットアップウィザード    ║
    ║         Created by C2B Bot Generator      ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    print("  このウィザードがBotの初期設定をお手伝いします。")
    print("  プログラミングの知識は必要ありません！\n")

    total_steps = 4

    # ──────── Step 1: Developer Portal ガイド ────────
    print_step(1, total_steps, "Discord Developer Portal の準備")
    print("""
  まだ Developer Portal で Bot を作成していない場合は、
  以下の手順で作成してください:

    1. ブラウザで https://discord.com/developers/applications を開く
    2. 「New Application」をクリック → 名前を入力
    3. 左メニューの「Bot」をクリック
    4. 「Reset Token」をクリックしてトークンをコピー

  ⚠️  重要な設定（同じ「Bot」ページで）:
    □ MESSAGE CONTENT INTENT  → ON にする
    □ SERVER MEMBERS INTENT   → ON にする
    □ PRESENCE INTENT         → ON にする（必要な場合）

  5. 左メニュー「OAuth2」→「URL Generator」
    □ Scopes: 「bot」と「applications.commands」にチェック
    □ Bot Permissions: 「Administrator」にチェック（推奨）
    □ 生成されたURLをコピーしてブラウザで開き、サーバーに招待
    """)

    input("  準備ができたら Enter を押してください... ")

    # ──────── Step 2: トークン設定 ────────
    print_step(2, total_steps, "Bot トークンの設定")

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    existing_token = ""

    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"^DISCORD_TOKEN\s*=\s*(.+)", line.strip())
                if match:
                    existing_token = match.group(1).strip().strip('"').strip("'")
                    break

    if existing_token and validate_token(existing_token):
        masked = existing_token[:8] + "..." + existing_token[-4:]
        print(f"\n  ✅ 既存のトークンが検出されました: {masked}")
        if not ask_yes_no("  トークンを変更しますか？", default=False):
            token = existing_token
        else:
            token = input("\n  新しい Discord Bot トークンを貼り付けてください:\n  > ").strip()
    else:
        print("\n  Discord Developer Portal でコピーしたトークンを貼り付けてください。")
        print("  （Bot → Reset Token でコピーできます）\n")
        token = input("  トークン: ").strip()

    if not validate_token(token):
        print("\n  ⚠️  トークンの形式が正しくないようです。")
        print("  形式: XXXXXXXX.XXXXXX.XXXXXXXXXXX (ピリオドで3つに分かれる)")
        if not ask_yes_no("  このまま続行しますか？", default=False):
            print("\n  中断しました。正しいトークンを取得してから再実行してください。")
            sys.exit(1)

    # .env ファイルの書き込み
    env_lines = []
    token_written = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DISCORD_TOKEN"):
                    env_lines.append(f"DISCORD_TOKEN={token}\n")
                    token_written = True
                else:
                    env_lines.append(line)

    if not token_written:
        env_lines.append(f"DISCORD_TOKEN={token}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(env_lines)

    print(f"\n  ✅ .env ファイルに保存しました → {env_path}")

    # ──────── Step 3: 依存パッケージ ────────
    print_step(3, total_steps, "依存パッケージのインストール")

    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if os.path.exists(req_path):
        print(f"\n  requirements.txt が見つかりました。")
        if ask_yes_no("  依存パッケージをインストールしますか？"):
            print("\n  📦 インストール中...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", req_path],
                    capture_output=True, text=True, timeout=120
                )
                if result.returncode == 0:
                    print("  ✅ インストール完了！")
                else:
                    print(f"  ⚠️  一部エラーがありました:\n  {result.stderr[:500]}")
                    print("  手動で `pip install -r requirements.txt` を実行してみてください。")
            except subprocess.TimeoutExpired:
                print("  ⚠️  タイムアウトしました。手動で実行してください。")
            except Exception as e:
                print(f"  ⚠️  エラー: {e}")
        else:
            print("  スキップしました。あとで `pip install -r requirements.txt` を実行してください。")
    else:
        print("  requirements.txt が見つかりません。")
        print("  必要なら手動で `pip install discord.py python-dotenv` を実行してください。")

    # ──────── Step 4: 接続テスト ────────
    print_step(4, total_steps, "接続テスト")

    if ask_yes_no("  Bot の接続テストを実行しますか？"):
        print("\n  🔍 接続テスト中... (5秒で自動終了)")
        test_code = f"""
import asyncio
import discord
import sys

async def test():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"CONNECT_OK:{{client.user}}")
        await client.close()
    
    try:
        await asyncio.wait_for(client.start("{token}"), timeout=10)
    except asyncio.TimeoutError:
        print("CONNECT_TIMEOUT")
    except discord.LoginFailure:
        print("CONNECT_FAIL:INVALID_TOKEN")
    except Exception as e:
        print(f"CONNECT_FAIL:{{e}}")

asyncio.run(test())
"""
        try:
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True, text=True, timeout=15
            )
            output = result.stdout.strip()
            if "CONNECT_OK:" in output:
                bot_name = output.split("CONNECT_OK:")[1].strip()
                print(f"\n  ✅ 接続成功！ Bot名: {bot_name}")
            elif "INVALID_TOKEN" in output:
                print("\n  ❌ トークンが無効です。Developer Portal で正しいトークンを確認してください。")
            elif "CONNECT_TIMEOUT" in output:
                print("\n  ⚠️  タイムアウトしました。ネットワーク接続を確認してください。")
            else:
                print(f"\n  ⚠️  接続に失敗しました: {output or result.stderr[:200]}")
        except Exception as e:
            print(f"\n  ⚠️  テスト実行エラー: {e}")
    else:
        print("  スキップしました。")

    # ──────── 完了 ────────
    print_header("🎉 セットアップ完了！")
    print(f"""
  Bot を起動するには:

    python main.py

  を実行してください。

  💡 起動後に問題があれば:
    • /doctor コマンドで自動診断
    • TROUBLESHOOTING.md を参照
    • Bot のログ出力を確認

  お疲れ様でした！ 🚀
""")


if __name__ == "__main__":
    main()
