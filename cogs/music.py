import discord
from discord.ext import commands
import youtube_dl
import asyncio
from collections import deque

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = deque()  # Hàng đợi nhạc (danh sách bài hát)

    # Tham gia kênh thoại
    @commands.command()
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("Bạn cần vào một kênh thoại trước!")
            return
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send(f"Đã tham gia {channel}")

    # Rời kênh thoại
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            self.queue.clear()  # Xóa queue khi rời
            await ctx.voice_client.disconnect()
            await ctx.send("Đã rời kênh thoại!")
        else:
            await ctx.send("Bot không ở trong kênh thoại nào!")

    # Phát nhạc
    @commands.command()
    async def play(self, ctx, url: str):
        if not ctx.message.author.voice:
            await ctx.send("Bạn cần vào một kênh thoại trước!")
            return
        if not ctx.voice_client:
            channel = ctx.message.author.voice.channel
            await channel.connect()

        async with ctx.typing():
            # Cấu hình youtube_dl (hỗ trợ nhiều nền tảng)
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                title = info['title']

            # Thêm vào queue nếu đang phát nhạc
            if ctx.voice_client.is_playing():
                self.queue.append((url2, title))
                await ctx.send(f"Đã thêm vào danh sách: **{title}**")
            else:
                # Phát ngay nếu không có gì đang phát
                await self._play_song(ctx, url2, title)

    # Hàm phụ để phát bài hát và tự động chuyển bài tiếp theo
    async def _play_song(self, ctx, url, title):
        source = discord.FFmpegPCMAudio(url, executable="ffmpeg")
        ctx.voice_client.play(source, after=lambda e: self._next_song(ctx))
        await ctx.send(f"Đang phát: **{title}**")

    # Chuyển sang bài tiếp theo trong queue
    def _next_song(self, ctx):
        if self.queue:
            url, title = self.queue.popleft()
            self.bot.loop.create_task(self._play_song(ctx, url, title))

    # Dừng nhạc
    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.queue.clear()  # Xóa queue khi dừng
            await ctx.send("Đã dừng nhạc và xóa danh sách!")
        else:
            await ctx.send("Hiện không có nhạc nào đang phát!")

    # Tạm dừng nhạc
    @commands.command(aliases=["pa"])
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Đã tạm dừng nhạc!")
        else:
            await ctx.send("Hiện không có nhạc nào đang phát để tạm dừng!")

    # Tiếp tục nhạc
    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Đã tiếp tục phát nhạc!")
        else:
            await ctx.send("Không có nhạc nào đang tạm dừng để tiếp tục!")

    # Xem danh sách phát
    @commands.command(aliases=["list"])
    async def queue(self, ctx):
        if not self.queue:
            await ctx.send("Danh sách phát hiện đang trống!")
        else:
            queue_list = "\n".join(f"{i+1}. {title}" for i, (_, title) in enumerate(self.queue))
            await ctx.send(f"**Danh sách phát hiện tại:**\n{queue_list}")

    # Xóa bài khỏi danh sách
    @commands.command()
    async def remove(self, ctx, index: int):
        if not self.queue:
            await ctx.send("Danh sách phát hiện đang trống!")
            return
        if index < 1 or index > len(self.queue):
            await ctx.send(f"Vui lòng chọn số từ 1 đến {len(self.queue)}!")
            return
        _, title = self.queue.pop(index - 1)
        await ctx.send(f"Đã xóa **{title}** khỏi danh sách!")

# Hàm setup để load cog
async def setup(bot):
    await bot.add_cog(Music(bot))
    