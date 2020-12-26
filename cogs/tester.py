# https://github.com/minibox24/MiniBOT 참고
import asyncio
import discord
import hPickle
import aiohttp
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
from urllib import parse


async def send(url, username=None, avatar_url=None, text=None, embed=None):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
        await webhook.send(
            username=username, avatar_url=avatar_url, content=text, embed=embed
        )


async def waitmsg(bot, ctx, cancel=False):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=120.0)
        if msg.content == "취소" and cancel:
            return await ctx.send("취소되었습니다.")
        return msg
    except asyncio.TimeoutError:
        return await ctx.send("답변을 2분 이상 안하셨습니다. 다시시도 해주세요.")


async def waityn(bot, ctx):
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg2 = await bot.wait_for("message", check=check, timeout=120.0)
        if msg2.content.lower() not in ["y", "n"]:
            await ctx.send("Y/N 중 한 가지로 골라주세요.")
            await waityn(bot, ctx)
        return msg2
    except asyncio.TimeoutError:
        return await ctx.send("답변을 2분 이상 안하셨습니다. 다시시도 해주세요.")


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = dict()
        self.webhooks = dict()
        asyncio.get_event_loop().create_task(self.on_load())

    async def on_load(self):
        await self.bot.wait_until_ready()
        try:
            self.data = hPickle.load("db.bin")
        except FileNotFoundError:
            hPickle.save("db.bin", {})
            self.data = {}
        try:
            self.webhooks = hPickle.load("webhooks.bin")
        except FileNotFoundError:
            hPickle.save("webhooks.bin", {})
            self.webhooks = {}

    def savedata(self):
        hPickle.save("db.bin", self.data)

    def botOwner(self, ctx, name):
        return name in self.data[ctx.author.id]

    @commands.command()
    async def 생성(self, ctx, name=None):
        if name is None:
            await ctx.send("봇 이름을 입력해주세요. 언제든지 `취소` 로 봇 제작을 취소할 수 있습니다.")
            msg = await waitmsg(self.bot, ctx, True)
            if msg.author == self.bot.user:
                return
            # for authDict in list(self.data.values()):
            #    if msg.content in list(authDict):
            #        return await ctx.send("이미 존재하는 봇입니다.")
            name = msg.content
        if name in self.data[ctx.author.id]:
            await ctx.send("이미 제작하신 봇입니다. 제거할까요? Y/N으로 대답해주세요")
            msg2 = await waityn(self.bot, ctx)
            if msg2.author == self.bot.user:
                return
            elif msg2.content.lower() == "n":
                return await ctx.send("취소되었습니다.")
            elif msg2.content.lower() == "y":
                del self.data[ctx.author.id][msg.content]
                self.savedata()
                return
        await ctx.send(
            "봇의 Prefix (접두사) 를 입력해주세요. 여러 개라면 `|` 으로 구분해주세요.\n예시 : `!|<@!123456789012345678>|?`"
        )
        msg3 = await waitmsg(self.bot, ctx)
        if msg3.author == self.bot.user:
            return
        prefixes = msg3.content.split("|")
        await ctx.send(
            "봇을 Private (비공개) 으로 할까요? 비공개로 하면 주인만 사용 가능하고 봇 리스트에 봇이 나오지 않습니다. `Y/N` 으로 대답해주세요."
        )
        msg2 = await waityn(self.bot, ctx)
        if msg2.author == self.bot.user:
            return
        elif msg2.content.lower() == "n":
            await ctx.send("Public (공개) 봇으로 설정하였습니다.")
            bot_public = True
        elif msg2.content.lower() == "y":
            await ctx.send("Private (비공개) 봇으로 설정하였습니다.")
            bot_public = False
        await ctx.send("봇의 상태 메세지를 입력해주세요.")
        msg4 = await waitmsg(self.bot, ctx)
        if msg4.author == self.bot.user:
            return

        playing = msg4.content
        await ctx.send("프로필 사진 링크를 보내주세요. 프로필 사진이 없을 경우 `없음`이라고 대답해주세요.")

        async def check_img():
            msg5 = await waitmsg(self.bot, ctx)
            url_Tester = parse.urlparse(msg5.content)
            if msg5.content == "없음":
                return None
            elif url_Tester.scheme == "https" or url_Tester.scheme == "http":
                return msg5.content
            await ctx.send("올바른 링크 혹은 `없음`을 적어주시기 바랍니다.")
            await check_img()

        avatar = await check_img()

        if not (ctx.author.id in self.data.keys()):
            self.data[ctx.author.id] = dict()
        self.data[ctx.author.id][name] = dict()
        self.data[ctx.author.id][name]["prefixes"] = set(prefixes)
        self.data[ctx.author.id][name]["public"] = bot_public
        self.data[ctx.author.id][name]["playing"] = playing
        self.data[ctx.author.id][name]["cmds"] = dict()
        self.data[ctx.author.id][name]["avatar"] = avatar
        self.savedata()
        await ctx.send(
            f"{name} 제작 성공!\n주인 : {ctx.author.mention}\n접두사 : {', '.join(prefixes)}\n상태메세지 : {playing}\n커맨드 : 없음\n프로필 : {avatar}"
        )

    @commands.command()
    async def 커맨드생성(self, ctx, name, *, wordandsentence=None):
        if self.botOwner(ctx, name):
            if wordandsentence is not None:
                if "&&&" not in wordandsentence:
                    return await ctx.send("꼭 `&&&`가 들어가게 보내주세요")
                sdfs = wordandsentence.split("&&&")
                self.data[ctx.author.id][name]["cmds"][sdfs[0]] = sdfs[1]
            else:
                await ctx.send("유저가 보내는 말을 보내주세요. 위 기능을 취소 하고 싶으시다면 `취소`를 적어주세요.")
                msg = await waitmsg(self.bot, ctx, True)
                if msg.author == self.bot.user:
                    return
                await ctx.send("봇이 보내는 말을 보내주세요.")
                msg2 = await waitmsg(self.bot, ctx)
                if msg2.author == self.bot.user:
                    return
                self.data[ctx.author.id][name]["cmds"][msg.content] = msg2.content
            self.savedata()
            await ctx.send("커맨드 생성 완료!")
        else:
            await ctx.send(f"당신은 {name}의 주인이 아닙니다!")

    @commands.command()
    async def 프사변경(self, ctx, name, avatar):
        if self.botOwner(ctx, name):
            url_Tester = parse.urlparse(avatar)
            if url_Tester.scheme == "https" or url_Tester.scheme == "http":
                self.data[ctx.author.id][name]["avatar"] = avatar
            else:
                await ctx.send("프로필 사진 링크를 보내주세요.")
            self.savedata()
            await ctx.send("성공!")
        else:
            await ctx.send(f"당신은 {name}의 주인이 아닙니다!")

    @commands.command()
    async def 봇정보(self, ctx, name):
        authId = None
        for rauthId in self.data:
            if name in list(self.data[rauthId]):
                if self.data[rauthId][name]["public"] or rauthId == ctx.author.id:
                    authId = rauthId
                    break

        if authId is None:
            return await ctx.send("존재하지 않는 봇입니다.")
        data = self.data[authId][name]
        embed = discord.Embed(title=name)
        embed.add_field(name="봇 주인: ", value=str(self.bot.get_user(authId)))
        embed.add_field(name="접두어: ", value=", ".join(data["prefixes"]))
        if data["cmds"] != {}:
            embed.add_field(
                name="커맨드", value=f"```{', '.join(list(data['cmds'].keys()))}```"
            )
        else:
            embed.add_field(name="커맨드", value="없음")
        if data["avatar"] is not None:
            embed.set_thumbnail(url=data["avatar"])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def 웹훅등록(self, ctx, url):
        self.webhooks[ctx.channel.id] = url
        hPickle.save("webhooks.bin", self.webhooks)
        await ctx.send("등록 성공!")

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_message(self, message):
        msg = message.content

        for authId in self.data:
            for name in self.data[authId]:
                botDict = self.data[authId][name]
                for prefix in botDict["prefixes"]:
                    if msg.startswith(prefix):
                        cmd = msg[len(prefix) :]
                        if (
                            (not botDict["public"]) and authId == message.author.id
                        ) or botDict["public"]:
                            if cmd in botDict["cmds"]:
                                dd = False
                                if message.channel.id in self.webhooks:
                                    webhookurl = self.webhooks[message.channel.id]
                                    try:
                                        await send(
                                            webhookurl,
                                            name,
                                            botDict["avatar"],
                                            botDict["cmds"][cmd],
                                        )
                                        dd = True
                                    except discord.HTTPException:
                                        del self.webhooks[message.channel.id]
                                if not dd:
                                    if message.channel.permissions_for(
                                        message.guild.me
                                    ) >= discord.Permissions(manage_webhooks=True):
                                        if len(await message.channel.webhooks()) > 0:
                                            webhookurl = (
                                                await message.channel.webhooks()
                                            )[0].url
                                            await send(
                                                webhookurl,
                                                name,
                                                botDict["avatar"],
                                                botDict["cmds"][cmd],
                                            )
                                        else:
                                            webhook = await message.channel.create_webhook(
                                                name="Botflix Webhook",
                                                reason="봇플릭스로 만든 봇을 테스트 가능하게 하는 웹훅입니다.",
                                            )
                                            await send(
                                                webhook.url,
                                                name,
                                                botDict["avatar"],
                                                botDict["cmds"][cmd],
                                            )
                                    else:
                                        await message.channel.send(
                                            "이 채널에서 웹훅 권한이 없네요. `b!웹훅등록 링크`로 등록해주세요."
                                        )
                                        break


def setup(bot):
    bot.add_cog(Tester(bot))
