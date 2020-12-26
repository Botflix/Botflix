
#Botflix Hackathon>명령어>건유1019(340373909339635725)
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
    game=discord.Game(".")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
	if message.content.startswith("!도움말"):
		await message.channel.send("이 디스코드봇은 \"전적\" 기능을 포함한 여러 기능을 다중 디스코드봇입니다.")


client.run("token")
