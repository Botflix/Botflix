import os
import asyncio
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import discord
from discord.ext import commands
import tokens
import hPickle


async def waitmsg(bot, ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=120.0)
        return msg
    except asyncio.TimeoutError:
        await ctx.send("답변을 2분 이상 안하셨습니다. 다시시도 해주세요.")
        return await waitmsg(bot, ctx)

def sendMail(target, filename):
    # 제목 입력
    subject = "Botflix 봇으로 제작됨"

    msg = MIMEMultipart()
    msg["From"] = tokens.sendEmail
    msg["To"] = target
    msg["Subject"] = subject

    # 본문 내용 입력
    body = "https://botflix.github.io/botflix/howto.html 에서 사용법을 자세히 알아보세요."
    msg.attach(MIMEText(body, "plain"))

    ############### ↓ 첨부파일이 없다면 삭제 가능  ↓ ########################
    # 첨부파일 경로/이름 지정하기
    attachment = open(filename, "rb")

    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=filename)
    part.add_header("Content-Disposition", "attachment; filename= " + filename)
    msg.attach(part)
    ############### ↑ 첨부파일이 없다면 삭제 가능  ↑ ########################

    text = msg.as_string()
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(tokens.sendEmail, tokens.emailpw)

    server.sendmail(tokens.sendEmail, target, text)
    server.quit()

    # msg = MIMEText(read+'\nclient.run("'+token+'")')
    #
    # msg['Subject'] = "Botflix로 만든 봇입니다. 파이썬으로 복붙하시면 됩니다."
    # msg['From'] = sendEmail
    # msg['To'] = mail  # recvEmail
    #
    # s = smtplib.SMTP("smtp.gmail.com", 587)
    # s.starttls()
    # s.login(sendEmail, password)
    # s.sendmail(sendEmail, mail, msg.as_string())
    # s.close()

def validemail(link):
    if not ("@" in link and "." in link): return False
    for i in link.split("@"):
        if i == '': return False
    return True

class BotMaker(commands.Cog):  # 2
    """Creating Bot Code Files in discord.py and Sending Them to Your Email"""

    def __init__(self, bot):  # 3
        self.bot = bot
        try: self.data = hPickle.load("db.bin")
        except FileNotFoundError:
            hPickle.save("db.bin", {})
            self.data = {}

        
    @commands.command()
    async def 내보내기(self, ctx, name=None):
        """Send Your Bot Code that you created to your email!"""
        if name == None:
            await ctx.send("봇 이름을 입력해주세요.")
            msg6 = await waitmsg(self.bot, ctx)
            if msg6.content == "취소":
                return await ctx.send("취소되었습니다.")
            name = msg6.content

        if f"!{name}.py" not in os.listdir("bm"):
            return await ctx.send("존재하지 않는 봇입니다. `b!봇제작` 으로 봇을 만들어주세요.")

        try:
            await ctx.author.send(file=discord.File(f"bm/!{name}.py"))
            await ctx.send("DM을 체크하시기 바랍니다.")
        except discord.errors.HTTPException:
            await ctx.author.send("메일을 디엠으로 보내주세요")
            async def dsf(bot, ctx):
                def check(msg):
                    return msg.author == ctx.author and msg.channel == ctx.author.channel

                try:
                    msg = await bot.wait_for("message", check=check, timeout=120.0)
                    if validemail(msg.content):
                        await ctx.send("유효한 이메일를 작성해주시기 바랍니다.")
                        return await dsf(bot, ctx)
                except asyncio.TimeoutError:
                    await ctx.send("답변을 2분 이상 안하셨습니다. 다시시도 해주세요.")
                    return await dsf(bot, ctx)
                return msg

            msg2 = await dsf(self.bot, ctx)
            if msg2.content == "취소": return await ctx.send("취소되었습니다.")

            sendMail(msg2.content, f"bm/!{name}.py")
            await ctx.send("Sent Successfully!")

    @commands.command()
    async def 봇제작(self, ctx, name, token="\"token\""):
        sample_data = self.data[ctx.author.id][name]
        on_message_part = ""
        playing = sample_data['playing']
        for i in sample_data['cmds'].keys():
            on_message_part += f"\tif"
            for j in sample_data['prefixes']:
                on_message_part += f" message.content.startswith(\"{j}{i}\")"
                if list(sample_data['prefixes']).index(j) != len(sample_data['prefixes'])-1:
                    on_message_part += " or"
            answer = sample_data['cmds'][i].replace('"','\\\"')
            on_message_part += f":\n\t\tawait message.channel.send(\"{answer}\")\n"
        with open(f"bm/!{name}.py", "w", encoding="UTF8") as f:
            f.write(f"""
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
""")
        await ctx.send("성공적으로 봇제작하였습니다! 봇추출을 원하시면 `b!내보내기 <봇이름>`을 이용해주세요.")

def setup(bot):
    bot.add_cog(BotMaker(bot))
