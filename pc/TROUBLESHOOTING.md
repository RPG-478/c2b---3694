# 🔧 トラブルシューティングガイド

Discord Bot でよくある問題と解決方法をまとめました。

---

## 🚨 起動時のエラー

### ❌ `DISCORD_TOKEN が設定されていません`

**原因:** `.env` ファイルにトークンが書かれていない

**解決:**
1. Bot フォルダに `.env` ファイルを作成
2. 以下を記入:
   ```
   DISCORD_TOKEN=あなたのトークン
   ```
3. トークンは [Discord Developer Portal](https://discord.com/developers/applications) → Bot → Reset Token で取得

---

### ❌ `LoginFailure: Improper token has been passed`

**原因:** トークンが間違っている

**解決:**
- `.env` のトークンにスペースや改行が入っていないか確認
- Developer Portal で「Reset Token」して新しいトークンを取得
- `.env` のトークンをクォートで囲まない（`DISCORD_TOKEN=abc123` が正しい）

---

### ❌ `Privileged message content intent is required`

**原因:** Discord Developer Portal で Intent が有効になっていない

**解決:**
1. [Developer Portal](https://discord.com/developers/applications) を開く
2. アプリケーション → Bot
3. **Privileged Gateway Intents** セクションで以下をON:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ PRESENCE INTENT（必要な場合）

---

### ❌ `ModuleNotFoundError: No module named 'discord'`

**原因:** discord.py がインストールされていない

**解決:**
```bash
pip install -r requirements.txt
```

---

## 🔍 コマンドが表示されない

### 1. `/` を打ってもコマンドが出てこない

**原因①:** Bot が `applications.commands` スコープなしで招待されている

**解決:**
以下の URL で Bot を再招待（`YOUR_CLIENT_ID` を Bot の ID に置き換え）:
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot+applications.commands&permissions=8
```

**原因②:** `tree.sync()` が呼ばれていない

**解決:** `on_ready` イベントに以下があるか確認:
```python
@bot.event
async def on_ready():
    await bot.tree.sync()
```

### 2. コマンドは見えるが「アプリケーションが応答しませんでした」

**原因:** 3秒以内に応答していない

**解決:** 重い処理の前に `defer()` を呼ぶ:
```python
@app_commands.command()
async def slow_cmd(self, interaction):
    await interaction.response.defer()  # 先にこれを呼ぶ
    # 重い処理...
    await interaction.followup.send("完了！")
```

---

## ⚡ ランタイムエラー

### `InteractionResponded: This interaction has already been responded`

**原因:** `response.send_message()` や `defer()` を2回呼んでいる

**解決:**
```python
# ❌ NG
await interaction.response.send_message("1つ目")
await interaction.response.send_message("2つ目")

# ✅ OK
await interaction.response.send_message("1つ目")
await interaction.followup.send("2つ目")
```

---

### `AttributeError: 'NoneType' object has no attribute 'send'`

**原因:** チャンネルやユーザーが見つからない（`get_channel` が `None`）

**解決:**
```python
channel = bot.get_channel(チャンネルID)
if channel is None:
    # チャンネルが見つからない場合のエラーハンドリング
    return
await channel.send("メッセージ")
```

---

### `Heartbeat blocked for more than N seconds`

**原因:** 重い同期処理がイベントループをブロックしている

**解決:**
```python
# ❌ NG: time.sleep はブロッキング
import time
time.sleep(10)

# ✅ OK: asyncio.sleep はノンブロッキング
import asyncio
await asyncio.sleep(10)

# ✅ OK: 重い処理は別スレッドで
import asyncio
result = await asyncio.to_thread(重い関数, 引数)
```

---

## 🌐 デプロイ関連

### Bot を24時間動かしたい

`DEPLOY_GUIDE.txt` を参照してください。以下の無料サービスが使えます:

| サービス | 無料枠 | 難易度 |
|---------|-------|--------|
| **Koyeb** | 1 nano サービス | ⭐ 簡単 |
| **Railway** | 月$5クレジット | ⭐ 簡単 |
| **Render** | Worker 無料 | ⭐⭐ 普通 |
| **Oracle Cloud** | 永久無料 VM | ⭐⭐⭐ 上級 |

---

### `429 Too Many Requests`

**原因:** API レート制限に引っかかっている

**解決:**
- `tree.sync()` を何度も呼ばない（`on_ready` で1回だけ）
- ループ内でAPI呼び出しをしない
- `asyncio.sleep()` で適切な間隔を空ける

---

## 🏥 自動診断

問題があるときは Bot 内で `/doctor` コマンドを実行すると、
自動的に問題を検出して修正方法を教えてくれます。

---

## 📚 参考リンク

- [discord.py 公式ドキュメント](https://discordpy.readthedocs.io/)
- [discord.py FAQ](https://discordpy.readthedocs.io/en/stable/faq.html)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord API ドキュメント](https://discord.com/developers/docs)

---

## 📱 スマホだけで使っている場合

### PCを持っていない / スマホしかない

**大丈夫です！** スマホだけでも Bot を動かせます。  
→ 同梱の `MOBILE_GUIDE.md` に詳しい手順があります。

### 要約（スマホのおすすめ方法）

1. **Replit アプリ**（iOS / Android）をインストール
2. Replit でこの Bot のコードを動かす
3. Secrets にトークンを設定 → ▶ Run

### スマホ特有の問題

| 問題 | 解決策 |
|------|--------|
| ZIP が解凍できない | Android→ZArchiver / iPhone→ファイルアプリ |
| Developer Portal が見にくい | ブラウザの「PC版サイト」で表示 |
| コードのコピペがうまくいかない | Replit にGitHub経由でインポート |
| `pip install` ができない | Replit なら自動 / Termux なら `pkg install python` が先 |
| `.env` ファイルが作れない | Replit の Secrets 機能を代わりに使う |
