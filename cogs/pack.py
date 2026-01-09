from typing import List, Optional
import logging
import discord
from discord.ext import commands
from colorama import Fore
import asyncio

def get_sentences() -> List[str]:
    """Read sentences from a file and return them as a list of strings."""
    try:
        with open("pack_sentences.txt", "r", encoding='utf-8') as file:
            sentences = file.readlines()
            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
            return sentences
    except FileNotFoundError:
        print(f"[{Fore.RED}-{Fore.RESET}] Error: File 'pack_sentences.txt' not found.")
        return []
    except UnicodeDecodeError as e:
        print(f"[{Fore.RED}-{Fore.RESET}] Error: Unable to decode file. {e}")
        return []
    except Exception as e:
        print(f"[{Fore.RED}-{Fore.RESET}] Error: {e}")
        return []

def get_sentences2() -> List[str]:
    """Read sentences from a file and return them as a list of strings."""
    try:
        with open("pack_sentences2.txt", "r", encoding='utf-8') as file:
            sentences = file.readlines()
            sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
            return sentences
    except FileNotFoundError:
        print(f"[{Fore.RED}-{Fore.RESET}] Error: File 'pack_sentences2.txt' not found.")
        return []
    except UnicodeDecodeError as e:
        print(f"[{Fore.RED}-{Fore.RESET}] Error: Unable to decode file. {e}")
        return []
    except Exception as e:
        print(f"[{Fore.RED}-{Fore.RESET}] Error: {e}")
        return []


class PackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stop_pack_flag: bool = False
        self.delay: float = 0.0
        self.packed_messages: List[discord.Message] = []
        self.message_count: int = 0  # Initialize message counter

    @commands.command()
    async def replybeef(self, ctx, users: commands.Greedy[discord.User] = None) -> None:
        """Start packing messages and replying to previous ones."""
        await ctx.message.delete()
        self.packed_messages = []
        self.message_count = 0
        sentences = get_sentences()
        sentences2 = get_sentences2()

        if not sentences or not sentences2:
            await ctx.send("No sentences available to send.")
            return

        user_mentions = [user.mention for user in users] if users else []

        while not self.stop_pack_flag:
            for sentence, sentence2 in zip(sentences, sentences2):
                if self.stop_pack_flag:
                    self.stop_pack_flag = False
                    return

                try:
                    mention_string = " ".join(user_mentions)
                    message_content = f"> ```✞ {self.message_count + 1} {sentence2.strip()} {self.message_count + 1} ✞```\n# > {mention_string} {sentence.strip()} (x{self.message_count + 1})"

                    if self.packed_messages:
                        last_message = self.packed_messages[-1]
                        message = await last_message.reply(message_content)
                    else:
                        message = await ctx.send(message_content)

                    self.message_count += 1
                    self.packed_messages.append(message)
                    print(f"Message Sent: ♰ {sentence.strip()} {sentence2.strip()} (x{self.message_count})")

                except discord.HTTPException as e:
                    print(f"An error occurred while sending message: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

                await asyncio.sleep(self.delay)
            
    @commands.command()
    async def replybeefoff(self, ctx) -> None:
        """Stop the packing process."""
        try:
            await ctx.message.delete()
            self.stop_pack_flag = True
            print("Stopped packing")
            temp_message = await ctx.send("```Stopped reply beef```")
            await asyncio.sleep(1)
            await temp_message.delete()
        except Exception as e:
            print(f"An error occurred: {e}")

    @commands.command()
    async def replybeefdelay(self, ctx, new_delay: float) -> None:
        """Set the delay between each message in the pack."""
        try:
            await ctx.message.delete()
            self.delay = new_delay
            print(f"Delay set to: {new_delay}")
            temp_message = await ctx.send(f"```Delay set to {new_delay}```")
            await asyncio.sleep(3)
            await temp_message.delete()
        except Exception as e:
            print(f"An error occurred: {e}")

def setup(bot):
    bot.add_cog(PackCog(bot))
