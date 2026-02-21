from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime, timedelta

class Economy8Afc1FCog(commands.Cog):
    """Royal Casino Bot - Economy Management Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = "economy_data.json"
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_data(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def _get_user_data(self, user_id: int) -> Dict[str, Any]:
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {
                "balance": 0,
                "total_earnings": 0,
                "last_claimed": None,
                "games_played": 0,
                "titles": []
            }
        return self.data[uid]

    @app_commands.command(name="daily", description="1日1回のデイリーボーナスを受け取ります。")
    async def daily(self, interaction: discord.Interaction):
        user_data = self._get_user_data(interaction.user.id)
        now = datetime.utcnow()
        last_claimed_str = user_data.get("last_claimed")
        
        if last_claimed_str:
            last_claimed = datetime.fromisoformat(last_claimed_str)
            if now < last_claimed + timedelta(days=1):
                next_claim = last_claimed + timedelta(days=1)
                wait_time = next_claim - now
                hours, remainder = divmod(int(wait_time.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                return await interaction.response.send_message(
                    f"👑 まだ受け取れません！ 次回まであと {hours}時間{minutes}分 です。", 
                    ephemeral=True
                )

        reward = 1000
        user_data["balance"] += reward
        user_data["total_earnings"] += reward
        user_data["last_claimed"] = now.isoformat()
        self._save_data()

        embed = discord.Embed(
            title="🏰 王室からの配給",
            description=f"本日分のボーナスとして **{reward:,} Royal Coins** を受け取りました！",
            color=0xd4af37
        )
        embed.add_field(name="現在の所持金", value=f"💰 {user_data['balance']:,} RC")
        embed.set_footer(text="明日もまたお越しください、陛下。")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="balance", description="現在の所持金と統計情報を確認します。")
    @app_commands.describe(user="確認したいユーザー")
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        target = user or interaction.user
        user_data = self._get_user_data(target.id)
        
        # Simple rank calculation based on balance
        all_balances = sorted([u["balance"] for u in self.data.values()], reverse=True)
        rank = all_balances.index(user_data["balance"]) + 1 if user_data["balance"] > 0 else "圏外"

        embed = discord.Embed(
            title=f"💎 {target.display_name} の資産状況",
            color=0xd4af37
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="所持金", value=f"💰 {user_data['balance']:,} RC", inline=True)
        embed.add_field(name="総獲得額", value=f"📈 {user_data['total_earnings']:,} RC", inline=True)
        embed.add_field(name="ランキング", value=f"🏆 {rank} 位", inline=True)
        embed.add_field(name="プレイ回数", value=f"🎲 {user_data['games_played']} 回", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="称号（ロール）を購入できるショップを開きます。")
    async def shop(self, interaction: discord.Interaction):
        shop_items = {
            "Duke": {"price": 50000, "desc": "公爵の地位。高貴な輝きを。"},
            "Prince": {"price": 250000, "desc": "王子の地位。王位継承権を得る。"},
            "King": {"price": 1000000, "desc": "国王の地位。このカジノの支配者。"}
        }

        embed = discord.Embed(
            title="🏛️ 王立高級ショップ",
            description="所持金を消費して特別な称号（ロール）を購入できます。",
            color=0x000080
        )
        for item, info in shop_items.items():
            embed.add_field(name=f"{item} - {info['price']:,} RC", value=info['desc'], inline=False)

        class ShopView(discord.ui.View):
            def __init__(self, cog: Economy8Afc1FCog):
                super().__init__(timeout=60)
                self.cog = cog

            @discord.ui.select(
                placeholder="購入する称号を選択してください...",
                options=[
                    discord.SelectOption(label="Duke (公爵)", value="Duke", description="50,000 RC"),
                    discord.SelectOption(label="Prince (王子)", value="Prince", description="250,000 RC"),
                    discord.SelectOption(label="King (国王)", value="King", description="1,000,000 RC"),
                ]
            )
            async def select_callback(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                item_name = select.values[0]
                price = shop_items[item_name]["price"]
                user_data = self.cog._get_user_data(select_interaction.user.id)

                if user_data["balance"] < price:
                    return await select_interaction.response.send_message("資金が不足しています。", ephemeral=True)

                user_data["balance"] -= price
                user_data["titles"].append(item_name)
                self.cog._save_data()

                # Attempt to give role if it exists in the server
                role = discord.utils.get(select_interaction.guild.roles, name=item_name)
                role_msg = ""
                if role:
                    try:
                        await select_interaction.user.add_roles(role)
                        role_msg = f"ロール「{item_name}」を付与しました。"
                    except:
                        role_msg = "ロール付与に失敗しました（権限不足）。"

                await select_interaction.response.send_message(
                    f"🎉 {item_name} を購入しました！ {role_msg}\n残高: {user_data['balance']:,} RC"
                )

        await interaction.response.send_message(embed=embed, view=ShopView(self))

    @app_commands.command(name="leaderboard", description="所持金ランキングを表示します。")
    async def leaderboard(self, interaction: discord.Interaction):
        sorted_users = sorted(
            [(uid, data["balance"]) for uid, data in self.data.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        embed = discord.Embed(title="👑 王立カジノ長者番付", color=0xd4af37)
        
        description = ""
        for i, (uid, bal) in enumerate(sorted_users, 1):
            user = self.bot.get_user(int(uid))
            name = user.name if user else f"Unknown({uid})"
            
            emoji = "🔹"
            if i == 1: emoji = "👑"
            elif i == 2: emoji = "🥈"
            elif i == 3: emoji = "🥉"
            
            description += f"{emoji} **{i}位**: {name} - `{bal:,} RC`\n"

        if not description:
            description = "まだデータがありません。"

        embed.description = description

        # User's own rank
        user_data = self._get_user_data(interaction.user.id)
        all_balances = sorted([u["balance"] for u in self.data.values()], reverse=True)
        try:
            user_rank = all_balances.index(user_data["balance"]) + 1
        except ValueError:
            user_rank = "圏外"
            
        embed.set_footer(text=f"あなたの順位: {user_rank}位 | 所持金: {user_data['balance']:,} RC")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy8Afc1FCog(bot))
# === END FILE ===