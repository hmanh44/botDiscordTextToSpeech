import discord
from discord.ext import commands, tasks
import asyncio
from gtts import gTTS
import os
from itertools import cycle

# Khởi tạo bot với prefix !
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

bot_statuses = cycle (["vscode ","vscode ",])

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

    # Kiểm tra xem người dùng có ở trong kênh thoại không
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        # Bot tham gia vào kênh thoại của người dùng
        voice_client = await channel.connect()
    else:
        await ctx.send(f"{ctx.author.mention} không vào kênh voice thì nói được cứt.")
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

        # Đợi 5 giây sau khi phát âm thanh xong rồi bot tự rời khỏi kênh
        await asyncio.sleep(1)
        if voice_client.is_connected():
            await voice_client.disconnect()
    
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {e}")

# Token của bot (đặt token của bạn ở đây)
TOKEN = "#"

# Chạy bot
bot.run(TOKEN)
