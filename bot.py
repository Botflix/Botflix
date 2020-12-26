import traceback
import os
import discord
import hPickle
from discord.ext import commands

import tokens

intent = discord.Intents.default()
intent.members = True
bot = commands.Bot(
    command_prefix='b!',
    intents=intent,
    owner_ids=[674813875291422720, 340373909339635725]
)

exts = ["cogs." + file[:-3] for file in os.listdir("cogs") if file.endswith(".py")]

@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)
    
    activity=discord.Game("Botflix | 투표해주세요! | 봇 제작봇!")
    await bot.change_presence(activity=activity)

    for ext in exts:
        try:
            bot.load_extension(ext)
        except:
            traceback.print_exc()

@bot.command()
@commands.is_owner()
async def reload(ctx):
    for ext in exts:
        try:
            bot.reload_extension(ext)
        except:
            await ctx.send(traceback.format_exc())

    await ctx.send("Done") # 다시실행좀

@bot.event
async def on_message(msg):
    data = hPickle.load("db.bin")
    if not msg.author.bot and msg.content.startswith(bot.command_prefix):
        if msg.author.id not in data:
            if msg.content != "b!가입":
                return await msg.channel.send("`b!가입` 명령어로 가입하세요!")
        await bot.process_commands(msg)

bot.run(tokens.bottoken)
