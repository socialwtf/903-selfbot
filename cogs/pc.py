# Selfbot PC Utilities Cog

from discord.ext import commands
import discord
import pyautogui
import tempfile
import os
import webbrowser
import platform
import subprocess
import asyncio
import psutil
import datetime
import pyperclip

class PCUtilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def pc(self, ctx):
        """Top-level PC utilities group. Use $pc <subcommand>"""
        help_text = """```ascii
Windows Control Center
>-----------------------------------<
pc screenshot        - Take a screenshot and upload it
pc shutdown confirm  - Shutdown the machine (requires 'confirm')
pc restart confirm   - Restart the machine (requires 'confirm')
pc open <url>        - Open URL in the default browser
pc openfile <path>   - Open a file or folder on the host
pc uptime            - Show system uptime
pc clipboard         - Get current clipboard text (if available)
pc processes         - Show top CPU processes
>-----------------------------------<
```"""
        await ctx.send(help_text)

    @pc.command()
    async def ss(self, ctx):
        """Take a screenshot and send it. Requires pyautogui installed and a graphical environment."""
        try:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            pyautogui.screenshot(tmp.name)
            await ctx.send("```ascii\n📸 Screenshot captured. Uploading...```", file=discord.File(tmp.name))
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Screenshot failed: {e}\n```")
        finally:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

    @pc.command()
    async def open(self, ctx, url: str):
        """Open a URL in the host machine's default browser."""
        try:
            webbrowser.open(url)
            await ctx.send(f"```ascii\n🌐 Opening URL: {url}\n```")
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Failed to open URL: {e}\n```")

    @pc.command(name="openfile")
    async def open_file(self, ctx, *, path: str):
        """Open a file or folder on the host machine. Provide absolute or relative path."""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            await ctx.send(f"```ascii\n📂 Opening: {path}\n```")
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Cannot open {path}: {e}\n```")

    @pc.command()
    async def shutdown(self, ctx, confirm: str = None):
        """Shutdown the host. Dangerous: requires the word 'confirm' as argument."""
        if confirm != "confirm":
            return await ctx.send("```ascii\n⚠️ To shutdown the machine run: $pc shutdown confirm\n(This extra step prevents accidental shutdowns)\n```")
        await ctx.send("```ascii\n⏱️ Shutting down in 3 seconds... (type CANCEL to abort in chat)\n```")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            done, pending = await asyncio.wait_for(self.bot.wait_for('message', check=check), timeout=3.0)
        except asyncio.TimeoutError:
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(["shutdown", "/s", "/t", "0"])
                elif platform.system() == "Darwin":
                    subprocess.Popen(["sudo", "shutdown", "-h", "now"])
                else:
                    subprocess.Popen(["sudo", "shutdown", "now"])
                await ctx.send("```ascii\n✅ Shutdown command issued.\n```")
            except Exception as e:
                await ctx.send(f"```ascii\n❌ Failed to issue shutdown: {e}\n```")

    @pc.command()
    async def restart(self, ctx, confirm: str = None):
        """Restart the host. Requires 'confirm' argument."""
        if confirm != "confirm":
            return await ctx.send("```ascii\n⚠️ To restart the machine run: $pc restart confirm\n```")
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["shutdown", "/r", "/t", "0"])
            elif platform.system() == "Darwin":
                subprocess.Popen(["sudo", "shutdown", "-r", "now"])
            else:
                subprocess.Popen(["sudo", "reboot"])
            await ctx.send("```ascii\n🔁 Restart command issued.\n```")
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Failed to restart: {e}\n```")

    @pc.command()
    async def uptime(self, ctx):
        """Show system uptime (best-effort)."""
        try:
            if psutil:
                uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
                m, s = divmod(int(uptime_seconds), 60)
                h, m = divmod(m, 60)
                d, h = divmod(h, 24)
                await ctx.send(f"```ascii\n⏱️ UPTIME: {d}d {h}h {m}m {s}s\n```")
            else:
                await ctx.send("```ascii\n⚠️ psutil not installed — cannot determine uptime. Install with: pip install psutil\n```")
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Failed to get uptime: {e}\n```")

    @pc.command()
    async def clipboard(self, ctx):
        """Get text from the system clipboard (if pyperclip is installed)."""
        try:
            text = pyperclip.paste()
            if not text:
                text = "<empty clipboard>"
            if len(text) > 1500:
                text = text[:1500] + "\n... (truncated)"
            await ctx.send(f"```ascii\n📋 Clipboard:\n{text}\n```")
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Clipboard read failed: {e}\n```")

    @pc.command()
    async def processes(self, ctx, top: int = 5):
        """Show top N CPU-using processes. Requires psutil."""
        try:
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                procs.append(p.info)
            procs_sorted = sorted(procs, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:top]
            out = "```ascii\nTOP PROCESSES (by CPU):\n"
            for p in procs_sorted:
                out += f"PID {p['pid']:>5}  CPU {p['cpu_percent']:>5}%  {p['name']}\n"
            out += "```"
            await ctx.send(out)
        except Exception as e:
            await ctx.send(f"```ascii\n❌ Failed to list processes: {e}\n```")

    @pc.command()
    async def ping(self, ctx):
        """Simple latency check."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"```ascii\n🏓 Pong! Latency: {latency} ms\n```")

def setup(bot):
    bot.add_cog(PCUtilities(bot))
