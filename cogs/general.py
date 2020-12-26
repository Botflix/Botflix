import difflib
import traceback
import discord
from discord.ext import commands
from discord.ext.commands import errors
import hPickle as pickled
import ast
import datetime

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.normal_color = 0x00FA6C
        self.error_color = 0xFF4A4A

    @commands.command()
    async def 가입(self, ctx):
        data = pickled.load("db.bin")
        if ctx.author.id in data:
            return await ctx.send("이미 가입하셨어요")

        data[ctx.author.id] = dict()
        pickled.save("db.bin", data)
        await ctx.send("성공!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        missing_param_errors = (
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.TooManyArguments,
            commands.UserInputError,
        )
        if isinstance(err, missing_param_errors):
            helper = (
                str(ctx.invoked_subcommand)
                if ctx.invoked_subcommand
                else str(ctx.command)
            )
            cmd = self.bot.get_command(helper)
            # await ctx.send_help(helper)
            # return
            em = discord.Embed(title="Incorrect!")
            em.description = f"Make sure you followed this format:\n**b!{cmd.name} {cmd.signature}**"
            return await ctx.send(embed=em)

        # elif isinstance(err, RuntimeError):
        #     self.bot.session = aiohttp.ClientSession()
        #     await self.bot.process_commands(ctx.message)
        #     return

        elif isinstance(err, (errors.CheckFailure, commands.NotOwner)):
            await ctx.send(
                "개발자가 아닙니다"
            )

        elif isinstance(err, commands.MissingPermissions):
            if ctx.author == self.bot.owner:
                return await ctx.reinvoke()
            missing = ""
            for x in err.missing_perms:
                missing += f"{format.capitalize(x)} \n"

            return await ctx.send(
                f"You don't have the **{missing}** permission to run this command!",
                edit=False,
            )

        elif isinstance(err, errors.CommandOnCooldown):
            if ctx.author == self.bot.owner:
                return await ctx.reinvoke()
            await ctx.send(
                f"This command is on cooldown... try again in {err.retry_after:.2f} seconds."
            )

        elif isinstance(err, errors.CommandNotFound):
            msg = ctx.message
            matches = difflib.get_close_matches(
                msg.content[2:],
                [x.name for x in self.bot.commands],
            )
            response = f"**The command you ran does not exist!**"
            if len(matches):
                response += f"\n\nDid you mean: b!{matches[0]}"
            if response != f"**The command you ran does not exist!**":
                await ctx.send(response)
            return
        await ctx.send(traceback.format_exc())
        raise err

    @commands.command()
    @commands.is_owner()
    async def db(self, ctx):
        await ctx.send(f"```json\n{pickled.load('db.bin')}\n```")

    @commands.command(name='eval')
    @commands.is_owner()
    async def eval_fn(self, ctx, *, cmd):
        if cmd.startswith("```") and cmd.endswith("```"):
            cmd = cmd[3:-3]
            if cmd.startswith("py"):
                cmd = cmd[2:]
        oldcmd = cmd
        embed = discord.Embed(title="EVAL", description="evaling...")
        embed.add_field(
            name="📥INPUT📥",
            value=f"""```py
{oldcmd}
```""",
            inline=False,
        )
        embed.add_field(
            name="📤OUTPUT📤",
            value="""```py
evaling...
```""",
            inline=False,
        )
        embed.add_field(
            name="🔧 Type 🔧",
            value="""```py
evaling...
```""",
            inline=False,
        )
        embed.add_field(
            name="🏓 Latency 🏓",
            value=f"""```py
{str((datetime.datetime.now()-ctx.message.created_at)*1000).split(":")[2]}
```""",
            inline=False,
        )

        try:
            msg = await ctx.send(embed=embed)
        except discord.HTTPException:
            msg = await ctx.send("evaling...")

        try:
            fn_name = "_eval_expr"
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            insert_returns(body)
            env = {
                "self": self,
                "bot": self.bot,
                "discord": discord,
                "commands": commands,
                "ctx": ctx,
                "channel": ctx.channel,
                "author": ctx.author,
                "server": ctx.guild,
                "message": ctx.message,
                "_": self._last_result,
                "__import__": __import__,
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)
            result = await eval(f"{fn_name}()", env)

            try:

                embed = discord.Embed(title="EVAL", description="Done!")
                embed.add_field(
                    name="📥INPUT📥",
                    value=f"""```py
{oldcmd}
```""",
                    inline=False,
                )
                embed.add_field(
                    name="📤OUTPUT📤",
                    value=f"""```py
{result}
```""",
                    inline=False,
                )
                embed.add_field(
                    name="🔧 Type 🔧",
                    value=f"""```py
{type(result)}
```""",
                    inline=False,
                )
                embed.add_field(
                    name="🏓 Latency 🏓",
                    value=f"""```py
{str((datetime.datetime.now()-ctx.message.created_at)*1000).split(":")[2]}
```""",
                    inline=False,
                )

                try:
                    await msg.edit(embed=embed)
                except discord.HTTPException:
                    await ctx.send(result)

            except discord.errors.HTTPException:
                with open("eval_result.txt", "w") as pf:
                    pf.write("eval : \n" + cmd + "\r\n-----\r\n" + str(result))
                await msg.edit(
                    content="length of result is over 1000. here is text file of result"
                )
                await ctx.send(file=discord.File("eval_result.txt"))

        except Exception as e:
            try:
                embed = discord.Embed(title="EVAL", description="Done!")
                embed.add_field(
                    name="📥INPUT📥",
                    value=f"""```py
{oldcmd}
```""",
                    inline=False,
                )
                embed.add_field(
                    name="📤OUTPUT📤",
                    value=f"""```py
{str(traceback.format_exc())}
```""",
                    inline=False,
                )
                embed.add_field(
                    name="🔧 Type 🔧",
                    value=f"""```py
{type(e)}
```""",
                    inline=False,
                )
                embed.add_field(
                    name="🏓 Latency 🏓",
                    value=f"""```py
{str((datetime.datetime.now()-ctx.message.created_at)*1000).split(":")[2]}
```""",
                    inline=False,
                )
                try:
                    await msg.edit(embed=embed)
                except discord.HTTPException:
                    await ctx.send(traceback.format_exc())
            except discord.errors.HTTPException:
                with open("eval_result.txt", "w") as pf:
                    pf.write(
                        "eval : \n"
                        + cmd
                        + "\r\n-----\r\n"
                        + str(traceback.format_exc())
                    )
                await msg.edit(
                    content="length of result is over 1000. here is text file of result"
                )
                await ctx.send(file=discord.File("eval_result.txt"))

def setup(bot):
    bot.add_cog(General(bot))