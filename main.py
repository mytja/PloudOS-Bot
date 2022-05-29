import discord
import discord.ext.commands as commands
import traceback
import os

from ploudos import PloudOS

bot = discord.Bot()

ploudos = PloudOS(os.getenv("PLOUDOS_USERNAME"), os.getenv("PLOUDOS_PASSWORD"))

guild_ids = None

async def send_info_embed(ctx):
    info = await ploudos.get_server_info()
    embed = discord.Embed(
        title=info["serverName"],
        description=info["serverIP"],
    )
    embed.set_thumbnail(url="https://ploudos.com/favicon.png")
    embed.add_field(
        name="Server version",
        value=f'`{info["serverVersion"]}`',
    )
    embed.add_field(
        name="Status",
        value=f'`{info["status"]}`',
    )
    embed.add_field(
        name="Is running",
        value=f'`{"Yes" if info.get("isRunning") else "No"}`',
    )
    embed.add_field(
        name="RAM usage",
        value=f'`{info.get("serverUsedRAM")}/{info.get("serverMaxRam")}`',
    )
    embed.add_field(
        name="CPU usage",
        value=f'`{info.get("serverUsedCPU")}/100%`',
    )
    embed.add_field(
        name="Disk usage",
        value=f'`{info.get("serverUsedSpace")}/{info.get("serverTotalSpace")}`',
    )
    embed.add_field(
        name="Players",
        value=f'`{info["onlineCount"] if info["onlineCount"] else 0}/{info["onlineMax"]}`',
    )
    if info.get("queueTimeFormatted"):
        embed.add_field(
            name="Queue",
            value=f'`{info["queuePos"]}/{info["queueSize"]}`',
        )
    if info.get("serverTimeoutFormatted"):
        embed.add_field(
            name="Offline in",
            value=f'`{info["serverTimeoutFormatted"]}`',
        )
    await ctx.respond(embed=embed)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}. Now logging into PloudOS")
    await ploudos.login()
    print("PloudOS login done.")

@bot.slash_command(guild_ids=guild_ids)
async def info(ctx):
    await send_info_embed(ctx)

@bot.slash_command(guild_ids=guild_ids)
@commands.has_permissions(administrator=True)
async def login(ctx):
    await ploudos.login()
    await ctx.respond("Successfully logged in!")

@bot.slash_command(guild_ids=guild_ids)
@commands.has_permissions(administrator=True)
async def stop(ctx):
    await ctx.respond("Please wait...")
    await ploudos.stop()
    await ctx.respond("Successfully stopped the server.")

@bot.slash_command(guild_ids=guild_ids)
@commands.has_permissions(administrator=True)
async def exit_queue(ctx):
    await ctx.respond("Please wait...")
    await ploudos.exit_queue()
    await ctx.respond("Successfully exited the queue.")

@bot.slash_command(guild_ids=guild_ids)
async def start(ctx):
    info = await ploudos.get_server_info()
    if info.get("isRunning") is True and info.get("isStarted") is True:
        await ctx.respond("Server is already running")
        return
    if await ploudos.can_restart():
        await ctx.respond("Restarting the server. Please wait.")
        try:
            await ploudos.restart()
        except Exception as e:
            print("[ERROR] Failed at restarting the server. Retrying.")
            try:
                await ploudos.restart()
            except:
                await ctx.respond("Server restart failed.")
                return
    else:
        await ctx.respond("Queueing the server. Please wait.")
        try:
            q = await ploudos.queue()
            await ctx.respond("Queue done.")
            if q:
                await ctx.respond("Server confirmation is necessary. Please wait...")
                try:
                    await ploudos.accept_server()
                except:
                    await ctx.respond(f"""
There was an error within the accept_server function.
Please contact the developers and give them the following piece of information (stacktrace).
This stacktrace does not contain any personal information, but if it does, please censor it.
If it says, there has been a timeout error, this is most likely a PloudOS problem. You should try to rerun the command or wait a little bit longer. If this is repetetive, try to increase the timeout or contact the developers.
```
{traceback.format_exc()}
```
                    """)
                    return
        except:
            await ctx.respond(f"""
There was an error within the queue function.
Please contact the developers and give them the following piece of information (stacktrace).
This stacktrace does not contain any personal information, but if it does, please censor it.
If it says, there has been a timeout error, this is most likely a PloudOS problem. You should try to rerun the command or wait a little bit longer. If this is repetetive, try to increase the timeout or contact the developers.
```
{traceback.format_exc()}
```
            """)
            return
    await ctx.respond("Successfully started the server")
    await send_info_embed(ctx)

bot.run(os.getenv("DISCORD_TOKEN"))
