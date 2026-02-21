# 📱 スマホだけで Discord Bot を動かすガイド

> **PCがなくても大丈夫！** このガイドはスマートフォンだけで
> Discord Bot をセットアップして24時間動かす方法を説明します。

---

## 🎯 あなたに合った方法を選ぼう

| 方法 | 難しさ | 費用 | おすすめ度 | 対応OS |
|------|--------|------|-----------|--------|
| **Replit** | ★☆☆ 超簡単 | 無料〜 | ⭐⭐⭐ | iOS/Android |
| **Koyeb** | ★★☆ 普通 | 無料 | ⭐⭐ | ブラウザ |
| **Termux** | ★★★ 上級 | 無料 | ⭐ | Android のみ |

---

## 方法1: Replit（一番おすすめ！）

### Replit って何？
スマホのアプリやブラウザ上でプログラムを書いて動かせるサービスです。  
**パソコンは一切不要です。**

### ステップ 1: Replit アカウントを作る
1. スマホで **Replit アプリ** をインストール
   - [Android (Google Play)](https://play.google.com/store/apps/details?id=com.replit.app)
   - [iOS (App Store)](https://apps.apple.com/us/app/replit-code-anything/id1614022293)
2. アプリを開いて **Sign Up**（アカウント作成）
3. メールアドレスか Google アカウントで登録

### ステップ 2: Discord Bot のトークンを取得する
1. スマホのブラウザで https://discord.com/developers/applications を開く
2. 右上の **New Application** をタップ → 名前を入力 → **Create**
3. 左メニューの **Bot** をタップ
4. **Reset Token** をタップ → 表示されたトークンを**コピー** 📋
   - ⚠️ **このトークンは絶対に他人に見せないでください！パスワードと同じです**
5. 下にスクロールして **Privileged Gateway Intents** を3つとも **ON** にする
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
6. **Save Changes** をタップ

### ステップ 3: Bot をサーバーに招待する
1. 左メニューの **OAuth2** をタップ
2. **URL Generator** の中で以下にチェック：
   - ✅ `bot`
   - ✅ `applications.commands`
3. 下の **BOT PERMISSIONS** で **Administrator** にチェック
4. 生成された URL をコピーしてブラウザで開く
5. Bot を追加したいサーバーを選んで **認証**

### ステップ 4: Replit でプロジェクトを作成
1. Replit アプリを開く
2. **+ Create Repl** をタップ
3. Template: **Python** を選択
4. 名前をつけて **Create Repl**

### ステップ 5: コードをアップロード
C2B からダウンロードした ZIP の中身を Replit にアップロードします。

**方法A: ファイルを1個ずつコピペ（簡単）**
1. ZIP を解凍アプリで開く（Android: ZArchiver、iOS: ファイルアプリ）
2. Replit の **Files** パネルで一つずつファイルを作成
3. 各ファイルの内容をコピペ

**方法B: GitHub 経由（おすすめ）**
1. C2B の `/github_connect` で GitHub 連携
2. 生成時に GitHub に自動アップロード
3. Replit で **Import from GitHub** を選択

### ステップ 6: トークンを設定する
1. Replit の左メニューで **Secrets** (🔒鍵アイコン) を開く
2. **+ New Secret** をタップ
3. Key: `DISCORD_TOKEN`
4. Value: ステップ2でコピーしたトークンを貼り付け
5. **Add Secret** をタップ

### ステップ 7: 実行！
1. 画面上部の ▶ **Run** ボタンをタップ
2. 下のコンソールに `Logged in as Botの名前` と出たら成功！ 🎉

### よくある質問（Replit）
- **Q: 「ModuleNotFoundError: No module named 'discord'」と出る**
  → Replit の Shell タブで `pip install discord.py` と入力
- **Q: 無料だと Bot が止まる？**  
  → 無料プランでは一定時間操作がないとスリープします。Replit の有料プランか、別のホスティング（Koyeb）を検討してください。
- **Q: ZIP がスマホで解凍できない**  
  → Android なら「ZArchiver」、iPhone なら標準の「ファイル」アプリで解凍できます

---

## 方法2: Koyeb（24時間無料で動かしたい人）

### Koyeb って何？
ブラウザだけで使える無料のサーバーです。  
Bot を置いておくと **24時間自動で動かしてくれます。**

### ステップ 1: 事前準備
- GitHub アカウントが必要です（無料）
- C2B で Bot 生成時に GitHub にアップロードしておく

### ステップ 2: Koyeb アカウント作成
1. スマホのブラウザで https://app.koyeb.com を開く
2. **Sign up with GitHub** をタップ
3. GitHub アカウントで認証

### ステップ 3: デプロイ
1. **Create Web Service** をタップ
2. **GitHub** を選択 → Bot のリポジトリを選択
3. 設定画面で：
   - Builder: **Dockerfile** を選択（C2B の Bot には Dockerfile が含まれています）
   - Instance type: **Free** を選択
4. **Environment Variables** セクションで：
   - Key: `DISCORD_TOKEN` / Value: あなたのトークン
5. **Deploy** をタップ！

約2〜3分でデプロイが完了し、Bot がオンラインになります。

---

## 方法3: Termux（Android 上級者向け）

> ⚠️ この方法は「ターミナル」や「コマンド」がわかる人向けです。
> 初めての方は **方法1（Replit）** をおすすめします。

### ステップ 1: Termux をインストール
- F-Droid からインストール: https://f-droid.org/packages/com.termux/
- ⚠️ Google Play 版は古いので **F-Droid 版** を使ってください

### ステップ 2: Python をインストール
```
pkg update && pkg upgrade
pkg install python
pip install discord.py
```

### ステップ 3: Bot を実行
```
cd /sdcard/Download/あなたのBotフォルダ
python main.py
```

### 注意点
- スマホがスリープすると Bot が止まります
- Termux の通知を常に表示する設定にすると止まりにくくなります
- 24時間稼働にはやはりクラウドサービス（方法1・2）がおすすめです

---

## 💡 スマホでの Tips

### ZIP ファイルの解凍
| OS | アプリ | 方法 |
|----|--------|------|
| Android | ZArchiver | ファイルマネージャーからZIPを長押し→解凍 |
| Android | 標準ファイラー | ZIPをタップ→展開 |
| iPhone | ファイル（標準） | ZIPをタップするだけ |

### Developer Portal がスマホで見にくい
- ブラウザの **「デスクトップ用サイトを表示」** を使うと操作しやすくなります
  - Chrome: 右上 ⋮ → 「PC版サイト」
  - Safari: 「ぁあ」→「デスクトップ用Webサイトを表示」

### トークンのコピーに失敗する
- Developer Portal でトークンをリセットすると新しいものが表示されます
- 表示されたら **素早くコピー**（ページを離れると再表示できません）
- メモ帳アプリに一旦貼り付けて保存しておくと安心

---

## ❓ よくある質問

**Q: Pythonって何？インストールしないといけないの？**  
A: Replit を使えばインストール不要です。Replit がすべて用意してくれます。

**Q: 「pip install」って何？**  
A: Python のライブラリ（道具箱）を自動でダウンロードするコマンドです。Replit なら自動でやってくれることが多いです。

**Q: `.env` ファイルって何？**  
A: Bot のパスワード（トークン）を安全に保存するファイルです。Replit では代わりに **Secrets** 機能を使います。

**Q: GitHub って何？必要？**  
A: プログラムを保存・共有するサービスです。Koyeb を使う場合は必要ですが、Replit だけなら不要です。

**Q: 本当にお金はかからないの？**  
A: Replit の無料プラン、Koyeb の無料枠、どちらも**クレジットカード不要**で始められます。

**Q: PC を持ってるけどプログラミングは初めて**  
A: このガイドの Replit の方法はPCのブラウザでも全く同じ手順で使えます！
