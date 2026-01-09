import discord
from discord.ext import commands
import requests
import datetime
import pytz
import random
import aiohttp
import asyncio
import re

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='massbreakup')
    async def nomorebabies(self, ctx, user: discord.User = None):
        if not user:
            return await ctx.send("```Mention ur non existing gf to unfriend like $massbreakup @user nigga ur a faggot````")

        try:
            relationship = await self.bot.fetch_user(user.id)
            await relationship.remove_friend()

            ansi_message = f"""
```ansi
[2;31mBreakup 💔 
[2;37mBye bitch 💔 [2;35m{user.name}#{user.discriminator}


(yes i'm retarded and black LOOOOOOOL)
```"""
            await ctx.send(ansi_message)

        except Exception as e:
            await ctx.send(f"```ansi\n[2;31m Failed to unfriend: {e}```")


    @commands.command()
    async def time(self, ctx, *, region):
        try:
            tz = pytz.timezone(region)
            time_now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            await ctx.send(f"```ansi\n[2;32m[TIME][0m {region} -> [0;36m{time_now}[0m```")
        except:
            await ctx.send("```ansi\n[2;31m[!][0m Invalid region or timezone.```")

    @commands.command()
    async def meme(self, ctx):
        try:
            res = requests.get("https://meme-api.com/gimme")
            data = res.json()
            title = data['title']
            url = data['url']
            postlink = data['postLink']
            
            msg = (
                f"```ansi\n[2;35m[Meme Drop][0m\n"
                f"[0;36mTitle:[0m {title}\n"
                f"[0;36mLink:[0m {postlink}\n```")
            await ctx.send(msg)
            await ctx.send(url)
        except:
            await ctx.send("```ansi\n[2;31m[!][0m Failed to fetch meme.```")

    @commands.command()
    async def apichanges(self, ctx):
        """Fetches the latest Discord API changelog and displays it with ANSI styling."""
        await ctx.message.delete()
        url = "https://discord.com/developers/docs/change-log"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await ctx.send("Failed to fetch API changelog.")
                    return
                html = await resp.text()

        # Extract the latest changelog entry
        match = re.search(r'<h2.*?>(.*?)<\/h2>.*?<p>(.*?)<\/p>', html, re.DOTALL)
        if not match:
            await ctx.send("Could not parse the changelog.")
            return

        title = match.group(1).strip()
        description = re.sub('<[^<]+?>', '', match.group(2)).strip()

        ansi_message = f"""```ansi
[1;34m{title}[0m

[0;37m{description}[0m
```"""

        await ctx.send(ansi_message)

    @commands.command()
    async def masscleardm(self, ctx):
        """Wipes all your open DMs (deletes private channels)."""
        await ctx.message.delete()
        wiped = 0
        failed = 0

        print("[*] Starting DM wipe...")

        for channel in self.bot.private_channels:
            try:
                if isinstance(channel, discord.DMChannel):
                    await channel.delete()
                    wiped += 1
                    await asyncio.sleep(0.5)  # be chill to avoid rate-limit
            except Exception as e:
                print(f"[!] Failed to delete DM with {channel.recipient}: {e}")
                failed += 1
                await asyncio.sleep(1)

        print(f"[+] DM wipe completed. Deleted: {wiped}, Failed: {failed}")
        await ctx.send(f"```Cleared {wiped} DMs. Failed to delete {failed}```", delete_after=5)

def setup(bot):
    bot.add_cog(Utility(bot))
