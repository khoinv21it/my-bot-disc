import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Tải biến môi trường từ .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX")

# Cấu hình bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Sự kiện khi bot sẵn sàng
@bot.event
async def on_ready():
    print(f"Bot đã sẵn sàng với tên: {bot.user}")
    await load_cogs()

# Hàm load cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Đã load {filename}")

# Chạy bot
if __name__ == "__main__":
    bot.run(TOKEN)
    