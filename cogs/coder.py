import os
import asyncio
import aiohttp

import discord
from discord.ext import commands
import hPickle
from pbwrap import Pastebin

import tokens

pb = Pastebin(tokens.api)


async def waitmsg(bot, ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=120.0)
        return msg
    except asyncio.TimeoutError:
        await ctx.send("답변을 2분 이상 안하셨습니다. 다시시도 해주세요.")
        return await waitmsg(bot, ctx)


class BotMaker(commands.Cog):  # 2
    """Creating Bot Code Files in discord.py and Sending Them to Your Email"""

    def __init__(self, bot):  # 3
        self.bot = bot

    @commands.command()
    async def 내보내기(self, ctx, name=None):
        """Send Your Bot Code that you created to your email!"""
        if name is None:
            await ctx.send("봇 이름을 입력해주세요.")
            msg6 = await waitmsg(self.bot, ctx)
            if msg6.content == "취소":
                return await ctx.send("취소되었습니다.")
            name = msg6.content

        if f"!{name}.py" not in os.listdir("bm"):
            return await ctx.send("존재하지 않는 봇입니다. `b!봇제작` 으로 봇을 만들어주세요.")

        try:
            await ctx.author.send(file=discord.File(f"bm/!{name}.py"))
        except discord.errors.HTTPException:
            text = open(f"bm/!{name}.py", encoding="UTF8").read()

            url = pb.create_paste(text, 1)
            await ctx.author.send(url)
        await ctx.send("DM을 체크하시기 바랍니다.")

    @commands.command()
    async def 봇제작(self, ctx, name, token='"token"'):
        self.data = hPickle.load("db.bin")
        sample_data = self.data[ctx.author.id][name]
        on_message_part = ""
        playing = sample_data["playing"]
        for i in sample_data["cmds"].keys():
            on_message_part += f"\tif"
            for j in sample_data["prefixes"]:
                on_message_part += f' message.content.startswith("{j}{i}")'
                if (
                    list(sample_data["prefixes"]).index(j)
                    != len(sample_data["prefixes"]) - 1
                ):
                    on_message_part += " or"
            answer = sample_data["cmds"][i].replace('"', '\\"')
            on_message_part += f':\n\t\tawait message.channel.send("{answer}")\n'
        with open(f"bm/!{name}.py", "w", encoding="UTF8") as f:
            f.write(
                f"""
#{str(ctx.guild.name)}>{str(ctx.channel.name)}>{ctx.author.name}({str(ctx.author.id)})
# Made by 건유1019#0001 and ! Tim23#9999
# -*- coding: utf-8 -*-

import discord

intent = discord.Intents.default()
client=discord.Client(intents=intent)

@client.event
async def on_ready():
    print("logged in")
    print(client.user.name)
    print(client.user.id)
    print("----------------------")
    game=discord.Game("{playing}")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
{on_message_part}

client.run({token})
"""
            )
        await ctx.send("성공적으로 봇제작하였습니다! 봇추출을 원하시면 `b!내보내기 <봇이름>`을 이용해주세요.")


def setup(bot):
    bot.add_cog(BotMaker(bot))
