
#Botflix Hackathon>명령어>! Tim23(674813875291422720)
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
    game=discord.Game("Playing")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):


client.run("token")
