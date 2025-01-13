import discord
from discord.ext import commands, tasks
import asyncio
from gtts import gTTS
import os
from itertools import cycle

# Khởi tạo bot với prefix !
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

bot_statuses = cycle(["vscode ", "vscode ",])

@tasks.loop(seconds=60)
async def change_bot_status():
    await bot.change_presence(activity=discord.Game(next(bot_statuses)))

@bot.event
async def on_ready():
    print("BOT ĐÃ CHẠY!")
    change_bot_status.start()

# Lệnh để bot đọc văn bản
@bot.command()
async def noi(ctx, *, text: str):
    await ctx.message.delete()  # Xóa tin nhắn của người dùng

    # Kiểm tra xem bot có đang ở trong kênh thoại không
    voice_client = ctx.voice_client
    if voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()
        else:
            await ctx.send(f"{ctx.author.mention} bot không ở trong kênh thoại và bạn không ở trong kênh thoại nào để bot tham gia.")
            return

    # Phản hồi lại tin nhắn, tag người dùng
    await ctx.send(f"{ctx.author.mention} nói: ```{text}```")
    
    try:
        # Tạo file âm thanh từ văn bản
        tts = gTTS(text=text, lang="vi")
        filename = "tts_audio.mp3"
        tts.save(filename)

        # Phát âm thanh
        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: print("Hoàn tất phát âm thanh."))
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # Xóa file sau khi phát
            os.remove(filename)
    
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {e}")

# Lệnh để bot tham gia kênh thoại bất kỳ
@bot.command()
async def join(ctx, *, channel_name: str = None):
    guild = ctx.guild
    channel = None

    if channel_name:
        for ch in guild.voice_channels:
            if ch.name == channel_name:
                channel = ch
                break
        if channel is None:
            await ctx.send(f"Không tìm thấy kênh thoại có tên: {channel_name}")
            return
    elif ctx.author.voice:
        channel = ctx.author.voice.channel
    else:
        await ctx.send(f"{ctx.author.mention} bạn cần chỉ định tên kênh hoặc vào một kênh thoại trước.")
        return

    if ctx.voice_client is None:
        await channel.connect()
        await ctx.send(f"Bot đã tham gia kênh {channel.name}!")
    else:
        await ctx.send("Bot đã ở trong kênh thoại rồi.")

# Lệnh để bot thoát khỏi kênh thoại
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bot đã thoát khỏi kênh thoại.")
    else:
        await ctx.send("Bot không ở trong kênh thoại nào.")

# Token của bot (đặt token của bạn ở đây)
TOKEN = "#"

# Chạy bot
bot.run(TOKEN)
