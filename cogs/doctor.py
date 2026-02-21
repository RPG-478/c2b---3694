# === C2B Bot Doctor: 自動診断 Cog ===
# このファイルは C2B が生成したBot に自動的に組み込まれます。
# 起動時にBot の健全性を自動チェックし、問題があれば修正方法を提示します。
# /doctor コマンドで手動診断も可能です。

import discord
from discord.ext import commands, tasks
from discord import app_commands
import sys
import os
import asyncio
import logging
import importlib
from datetime import datetime, timezone
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DiagnosticResult:
    """診断結果を格納するデータクラス"""
    def __init__(self, name: str, status: str, message: str, fix: str = ""):
        self.name = name
        self.status = status  # "ok", "warn", "error"
        self.message = message
        self.fix = fix

    @property
    def emoji(self) -> str:
        return {"ok": "✅", "warn": "⚠️", "error": "❌"}.get(self.status, "❓")


class BotDoctorCog(commands.Cog, name="Bot Doctor"):
    """Bot の健全性を自動診断する Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._startup_report_sent = False

    # ──────────────────────────────────────────────
    # 診断チェック群
    # ──────────────────────────────────────────────

    def _check_python_version(self) -> DiagnosticResult:
        """Python バージョンの互換性チェック"""
        v = sys.version_info
        ver_str = f"{v.major}.{v.minor}.{v.micro}"
        if v < (3, 9):
            return DiagnosticResult(
                "Python バージョン", "error",
                f"Python {ver_str} は discord.py v2 に非対応です。",
                "Python 3.9 以上をインストールしてください: https://www.python.org/downloads/"
            )
        if v >= (3, 13):
            # audioop 問題の警告
            try:
                import audioop  # noqa: F401
            except (ImportError, ModuleNotFoundError):
                return DiagnosticResult(
                    "Python バージョン", "warn",
                    f"Python {ver_str} では audioop が削除されました。音声機能が動作しない可能性があります。",
                    "音声機能が必要な場合は Python 3.12 以下を使用するか、audioop-lts パッケージをインストールしてください:\n"
                    "`pip install audioop-lts`"
                )
        return DiagnosticResult("Python バージョン", "ok", f"Python {ver_str} ✓")

    def _check_token(self) -> DiagnosticResult:
        """トークンの設定チェック"""
        token = os.getenv("DISCORD_TOKEN", "")
        if not token:
            return DiagnosticResult(
                "Discord トークン", "error",
                "DISCORD_TOKEN 環境変数が設定されていません。",
                "**修正方法:**\n"
                "1. [Discord Developer Portal](https://discord.com/developers/applications) を開く\n"
                "2. アプリケーション → Bot → 「Reset Token」でトークンをコピー\n"
                "3. `.env` ファイルに `DISCORD_TOKEN=コピーしたトークン` と書く\n"
                "4. Bot を再起動"
            )
        if len(token) < 50:
            return DiagnosticResult(
                "Discord トークン", "warn",
                "トークンが短すぎます。正しいトークンか確認してください。",
                "Discord Developer Portal で新しいトークンを発行してください。"
            )
        return DiagnosticResult("Discord トークン", "ok", "トークン設定済み ✓")

    def _check_intents(self) -> DiagnosticResult:
        """Intent の設定チェック"""
        intents = self.bot.intents
        issues = []

        if not intents.message_content:
            issues.append(
                "- `message_content` が無効です → メッセージ内容を読めません\n"
                "  Developer Portal → Bot → 「MESSAGE CONTENT INTENT」を ON にしてください"
            )
        if not intents.guilds:
            issues.append("- `guilds` が無効です → サーバー情報を取得できません")
        if not intents.members:
            issues.append(
                "- `members` が無効です → メンバー情報を取得できません\n"
                "  Developer Portal → Bot → 「SERVER MEMBERS INTENT」を ON にしてください"
            )

        if issues:
            return DiagnosticResult(
                "Intents 設定", "warn",
                "一部の Intent が無効です:\n" + "\n".join(issues),
                "Discord Developer Portal で Privileged Gateway Intents を有効にしてください:\n"
                "https://discord.com/developers/applications → Bot → Privileged Gateway Intents"
            )
        return DiagnosticResult("Intents 設定", "ok", "必要な Intent がすべて有効 ✓")

    def _check_permissions(self) -> DiagnosticResult:
        """Bot の権限チェック（招待URL関連）"""
        app_info = getattr(self.bot, "application", None) or getattr(self.bot, "user", None)
        bot_id = getattr(app_info, "id", None) or (self.bot.user.id if self.bot.user else None)
        if not bot_id:
            return DiagnosticResult("Bot 権限", "warn", "Bot ID を取得できません。")

        # applications.commands スコープ確認
        guild_count = len(self.bot.guilds)
        if guild_count == 0:
            return DiagnosticResult(
                "Bot 権限", "error",
                "Bot がどのサーバーにも参加していません。",
                f"以下のURLでBotを招待してください:\n"
                f"https://discord.com/oauth2/authorize?client_id={bot_id}"
                f"&scope=bot+applications.commands&permissions=8"
            )
        return DiagnosticResult("Bot 権限", "ok", f"{guild_count} サーバーに接続中 ✓")

    def _check_slash_commands(self) -> DiagnosticResult:
        """スラッシュコマンドの同期状態チェック"""
        try:
            cmds = self.bot.tree.get_commands()
            if not cmds:
                return DiagnosticResult(
                    "スラッシュコマンド", "error",
                    "スラッシュコマンドが登録されていません。",
                    "**修正方法:** `on_ready` イベントで `await bot.tree.sync()` を呼んでください。\n"
                    "また、Bot を `applications.commands` スコープ付きで招待していることを確認してください。"
                )
            return DiagnosticResult(
                "スラッシュコマンド", "ok",
                f"{len(cmds)} 個のコマンドが登録済み ✓"
            )
        except Exception as e:
            return DiagnosticResult("スラッシュコマンド", "warn", f"チェック中にエラー: {e}")

    def _check_dependencies(self) -> DiagnosticResult:
        """依存パッケージのチェック"""
        missing = []
        for pkg in ["discord", "dotenv", "aiohttp"]:
            actual_import = "discord" if pkg == "discord" else ("dotenv" if pkg == "dotenv" else "aiohttp")
            try:
                importlib.import_module(actual_import)
            except ImportError:
                pip_name = "discord.py" if pkg == "discord" else ("python-dotenv" if pkg == "dotenv" else "aiohttp")
                missing.append(f"- `{pip_name}`")

        if missing:
            return DiagnosticResult(
                "依存パッケージ", "error",
                "以下のパッケージが未インストールです:\n" + "\n".join(missing),
                "`pip install -r requirements.txt` を実行してください。"
            )
        return DiagnosticResult("依存パッケージ", "ok", "必要なパッケージがすべてインストール済み ✓")

    def _check_env_file(self) -> DiagnosticResult:
        """`.env` ファイルの存在チェック"""
        env_path = os.path.join(os.getcwd(), ".env")
        if not os.path.exists(env_path):
            return DiagnosticResult(
                ".env ファイル", "warn",
                ".env ファイルが見つかりません。",
                "**修正方法:**\n"
                "1. Bot のフォルダに `.env` ファイルを新規作成\n"
                "2. 以下を書き込む:\n"
                "```\nDISCORD_TOKEN=あなたのトークン\n```\n"
                "3. Bot を再起動"
            )
        return DiagnosticResult(".env ファイル", "ok", ".env ファイル検出 ✓")

    def _check_event_loop_health(self) -> DiagnosticResult:
        """イベントループの健全性チェック"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                return DiagnosticResult(
                    "イベントループ", "error",
                    "イベントループが閉じています。",
                    "Bot の起動コードを確認してください。`asyncio.run()` が正しく使われていますか？"
                )
            return DiagnosticResult("イベントループ", "ok", "イベントループ正常 ✓")
        except Exception as e:
            return DiagnosticResult("イベントループ", "warn", f"チェック中にエラー: {e}")

    # ──────────────────────────────────────────────
    # 全診断実行
    # ──────────────────────────────────────────────

    def run_all_checks(self) -> List[DiagnosticResult]:
        """すべての診断チェックを実行"""
        checks = [
            self._check_python_version,
            self._check_token,
            self._check_env_file,
            self._check_intents,
            self._check_dependencies,
            self._check_permissions,
            self._check_slash_commands,
            self._check_event_loop_health,
        ]
        results = []
        for check in checks:
            try:
                results.append(check())
            except Exception as e:
                results.append(DiagnosticResult(check.__name__, "warn", f"チェック失敗: {e}"))
        return results

    def build_report_embed(self, results: List[DiagnosticResult]) -> discord.Embed:
        """診断結果をDiscord Embedに変換"""
        errors = [r for r in results if r.status == "error"]
        warns = [r for r in results if r.status == "warn"]
        oks = [r for r in results if r.status == "ok"]

        if errors:
            color = discord.Color.red()
            title = "🏥 Bot Doctor: 問題が見つかりました"
        elif warns:
            color = discord.Color.yellow()
            title = "🏥 Bot Doctor: 注意事項があります"
        else:
            color = discord.Color.green()
            title = "🏥 Bot Doctor: 全チェック合格！"

        embed = discord.Embed(
            title=title,
            description=f"**{len(oks)}** 合格 / **{len(warns)}** 注意 / **{len(errors)}** エラー",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )

        # エラーを先に表示
        for r in errors + warns:
            value = r.message
            if r.fix:
                value += f"\n\n💡 **修正方法:**\n{r.fix}"
            # Embed field value は 1024文字制限
            embed.add_field(name=f"{r.emoji} {r.name}", value=value[:1024], inline=False)

        # 合格はまとめて表示
        if oks:
            ok_summary = "\n".join(f"{r.emoji} {r.name}: {r.message}" for r in oks)
            embed.add_field(name="合格項目", value=ok_summary[:1024], inline=False)

        embed.set_footer(text="💡 /doctor でいつでも診断を実行できます")
        return embed

    # ──────────────────────────────────────────────
    # イベント: 起動時の自動診断
    # ──────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot起動時に自動診断を実行してログに出力"""
        if self._startup_report_sent:
            return
        self._startup_report_sent = True

        results = self.run_all_checks()
        errors = [r for r in results if r.status == "error"]
        warns = [r for r in results if r.status == "warn"]

        logger.info("🏥 Bot Doctor: 起動時診断 - %d合格 / %d注意 / %d エラー",
                     len(results) - len(errors) - len(warns), len(warns), len(errors))

        for r in errors:
            logger.error("❌ %s: %s", r.name, r.message)
            if r.fix:
                logger.error("   💡 修正: %s", r.fix.replace("\n", " "))
        for r in warns:
            logger.warning("⚠️ %s: %s", r.name, r.message)

    # ──────────────────────────────────────────────
    # コマンド: /doctor
    # ──────────────────────────────────────────────

    @app_commands.command(name="doctor", description="🏥 Bot の健全性を診断します")
    async def doctor(self, interaction: discord.Interaction):
        """Bot の健全性を診断し、問題があれば修正方法を提示"""
        await interaction.response.defer(thinking=True)

        results = self.run_all_checks()
        embed = self.build_report_embed(results)
        await interaction.followup.send(embed=embed)

    # ──────────────────────────────────────────────
    # コマンド: /setup_guide
    # ──────────────────────────────────────────────

    @app_commands.command(name="setup_guide", description="📖 Bot のセットアップ手順を表示します")
    async def setup_guide(self, interaction: discord.Interaction):
        """初心者向けのセットアップガイドを表示"""
        embed = discord.Embed(
            title="📖 Bot セットアップガイド",
            description="このBotを動かすための手順です。",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Step 1: Discord Developer Portal で Bot を作成",
            value=(
                "1. [Developer Portal](https://discord.com/developers/applications) を開く\n"
                "2. 「New Application」→ 名前を入力して作成\n"
                "3. 左メニュー「Bot」→ 「Add Bot」\n"
                "4. 「Reset Token」でトークンをコピー\n"
                "5. **Privileged Gateway Intents** をすべて ON にする"
            ),
            inline=False
        )

        embed.add_field(
            name="Step 2: Bot をサーバーに招待",
            value=(
                "1. 左メニュー「OAuth2」→「URL Generator」\n"
                "2. Scopes: `bot` と `applications.commands` にチェック\n"
                "3. Bot Permissions: `Administrator`（初心者向け推奨）\n"
                "4. 生成されたURLをブラウザで開いてサーバーを選択"
            ),
            inline=False
        )

        embed.add_field(
            name="Step 3: 環境設定",
            value=(
                "1. Bot のフォルダに `.env` ファイルを作成\n"
                "2. 中に `DISCORD_TOKEN=あなたのトークン` と書く\n"
                "3. ターミナルで `pip install -r requirements.txt`\n"
                "4. `python main.py` で起動！"
            ),
            inline=False
        )

        embed.add_field(
            name="💡 よくあるトラブル",
            value=(
                "• **コマンドが表示されない** → `applications.commands` スコープ付きで再招待\n"
                "• **Intents エラー** → Developer Portal で Intents を ON にする\n"
                "• **トークンエラー** → `.env` のトークンが正しいか確認\n"
                "• **権限エラー** → Bot のロールがコマンド実行に必要な権限を持っているか確認\n"
                "• **起動時にエラー** → `/doctor` で自動診断を実行"
            ),
            inline=False
        )

        embed.set_footer(text="🏥 問題がある場合は /doctor で自動診断できます")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotDoctorCog(bot))
