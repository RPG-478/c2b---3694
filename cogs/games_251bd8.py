from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from typing import Literal, Optional

class Games251Bd8Cog(commands.Cog):
    """Royal Casino Bot - Games Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_path = "casino_data.json"
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.balance_data = json.load(f)
        else:
            self.balance_data = {}

    def save_data(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.balance_data, f, indent=4)

    def get_balance(self, user_id: str) -> int:
        return self.balance_data.get(user_id, 1000)  # Default 1000 credits

    def update_balance(self, user_id: str, amount: int):
        current = self.get_balance(user_id)
        self.balance_data[user_id] = max(0, current + amount)
        self.save_data()

    @app_commands.command(name="blackjack", description="ディーラーとブラックジャックで対戦します。")
    @app_commands.describe(bet="賭ける金額")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        user_id = str(interaction.user.id)
        balance = self.get_balance(user_id)

        if bet <= 0:
            return await interaction.response.send_message("賭け金は1以上にしてください。", ephemeral=True)
        if balance < bet:
            return await interaction.response.send_message(f"残高が足りません。現在の残高: {balance}コイン", ephemeral=True)

        self.update_balance(user_id, -bet)

        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(deck)

        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        def calculate_score(hand):
            score = sum(hand)
            aces = hand.count(11)
            while score > 21 and aces:
                score -= 10
                aces -= 1
            return score

        class BlackjackView(discord.ui.View):
            def __init__(self, cog, user, bet, p_hand, d_hand, deck_ref):
                super().__init__(timeout=60)
                self.cog = cog
                self.user = user
                self.bet = bet
                self.p_hand = p_hand
                self.d_hand = d_hand
                self.deck = deck_ref
                self.ended = False

            def create_embed(self, show_dealer=False):
                p_score = calculate_score(self.p_hand)
                d_score = calculate_score(self.d_hand) if show_dealer else calculate_score([self.d_hand[0]])
                
                embed = discord.Embed(title="🏰 Royal Blackjack", color=0xd4af37)
                embed.add_field(name=f"{self.user.display_name}の合計: {p_score}", value=f"カード: {', '.join(map(str, self.p_hand))}", inline=False)
                dealer_val = f"カード: {', '.join(map(str, self.d_hand))}" if show_dealer else f"カード: {self.d_hand[0]}, 🎴"
                embed.add_field(name=f"ディーラーの合計: {d_score if show_dealer else '?'}", value=dealer_val, inline=False)
                return embed

            @discord.ui.button(label="ヒット", style=discord.ButtonStyle.green)
            async def hit(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != self.user.id: return
                self.p_hand.append(self.deck.pop())
                if calculate_score(self.p_hand) > 21:
                    self.ended = True
                    await self.finish_game(btn_interaction, "バースト！あなたの負けです。")
                else:
                    await btn_interaction.response.edit_message(embed=self.create_embed(), view=self)

            @discord.ui.button(label="スタンド", style=discord.ButtonStyle.red)
            async def stand(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != self.user.id: return
                self.ended = True
                while calculate_score(self.d_hand) < 17:
                    self.d_hand.append(self.deck.pop())
                
                p_score = calculate_score(self.p_hand)
                d_score = calculate_score(self.d_hand)

                if d_score > 21 or p_score > d_score:
                    payout = int(self.bet * 2)
                    if p_score == 21 and len(self.p_hand) == 2: payout = int(self.bet * 2.5)
                    self.cog.update_balance(str(self.user.id), payout)
                    await self.finish_game(btn_interaction, f"あなたの勝ちです！ {payout}コイン獲得！")
                elif p_score < d_score:
                    await self.finish_game(btn_interaction, "ディーラーの勝ちです。")
                else:
                    self.cog.update_balance(str(self.user.id), self.bet)
                    await self.finish_game(btn_interaction, "引き分け（プッシュ）です。賭け金が戻ります。")

            async def finish_game(self, btn_interaction, result_text):
                for child in self.children: child.disabled = True
                embed = self.create_embed(show_dealer=True)
                embed.description = f"**結果: {result_text}**"
                await btn_interaction.response.edit_message(embed=embed, view=self)

        view = BlackjackView(self, interaction.user, bet, player_hand, dealer_hand, deck)
        await interaction.response.send_message(embed=view.create_embed(), view=view)

    @app_commands.command(name="roulette", description="ルーレットを開始します。")
    @app_commands.describe(bet="賭ける金額", choice="red, black, even, odd, または 0-36の数字")
    async def roulette(self, interaction: discord.Interaction, bet: int, choice: str):
        user_id = str(interaction.user.id)
        balance = self.get_balance(user_id)
        choice = choice.lower()

        valid_choices = ["red", "black", "even", "odd"]
        is_num = choice.isdigit() and 0 <= int(choice) <= 36
        
        if not (choice in valid_choices or is_num):
            return await interaction.response.send_message("無効な選択です。red, black, even, odd, または 0-36の数字を入力してください。", ephemeral=True)
        if bet <= 0 or balance < bet:
            return await interaction.response.send_message("残高不足または無効な賭け金です。", ephemeral=True)

        self.update_balance(user_id, -bet)
        result_num = random.randint(0, 36)
        
        red_nums = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        result_color = "red" if result_num in red_nums else ("green" if result_num == 0 else "black")
        
        win = False
        multiplier = 0
        if is_num and int(choice) == result_num:
            win, multiplier = True, 36
        elif choice == "red" and result_color == "red":
            win, multiplier = True, 2
        elif choice == "black" and result_color == "black":
            win, multiplier = True, 2
        elif choice == "even" and result_num != 0 and result_num % 2 == 0:
            win, multiplier = True, 2
        elif choice == "odd" and result_num % 2 != 0:
            win, multiplier = True, 2

        embed = discord.Embed(title="🎡 Royal Roulette", color=0xd4af37 if win else 0x2f3136)
        color_emoji = "🔴" if result_color == "red" else ("🟢" if result_color == "green" else "⚫")
        embed.add_field(name="結果", value=f"{color_emoji} **{result_num} ({result_color.upper()})**", inline=False)
        
        if win:
            payout = bet * multiplier
            self.update_balance(user_id, payout)
            embed.description = f"おめでとうございます！ **{payout}** コイン獲得しました！"
        else:
            embed.description = "残念！また挑戦しましょう。"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slots", description="スロットマシンを回します。")
    @app_commands.describe(bet="賭ける金額")
    async def slots(self, interaction: discord.Interaction, bet: int):
        user_id = str(interaction.user.id)
        balance = self.get_balance(user_id)

        if bet <= 0 or balance < bet:
            return await interaction.response.send_message("残高不足または無効な賭け金です。", ephemeral=True)

        self.update_balance(user_id, -bet)
        symbols = ["👑", "💎", "💰", "🎰", "🍒", "🔔"]
        reels = [random.choice(symbols) for _ in range(3)]
        
        win_amount = 0
        if reels[0] == reels[1] == reels[2]:
            multipliers = {"👑": 50, "💎": 20, "💰": 10, "🎰": 5, "🍒": 3, "🔔": 2}
            win_amount = bet * multipliers[reels[0]]
        elif reels[0] == reels[1] or reels[1] == reels[2]:
            win_amount = int(bet * 1.5)

        embed = discord.Embed(title="🎰 Royal Slots", color=0xd4af37 if win_amount > 0 else 0x2f3136)
        embed.description = f"**[ {reels[0]} | {reels[1]} | {reels[2]} ]**"
        
        if win_amount > 0:
            self.update_balance(user_id, win_amount)
            embed.add_field(name="WIN!", value=f"**{win_amount}** コイン獲得！")
        else:
            embed.add_field(name="LOSS", value="残念...")

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Games251Bd8Cog(bot))
# === END FILE ===