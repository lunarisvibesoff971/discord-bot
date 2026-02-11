import discord
from discord.ext import commands, tasks
import yt_dlp
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")
ANNOUNCE_CHANNEL_ID = int(os.getenv("1259974469393318000"))

# ======================
# READY
# ======================

@bot.event
async def on_ready():
    print(f"✅ {bot.user} connecté")
    auto_announce.start()

# ======================
# ANNONCES AUTO
# ======================

@tasks.loop(minutes=60)
async def auto_announce():
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel:
        await channel.send("📢 Event ce soir ! Soyez prêts 🔥")

# ======================
# MODERATION
# ======================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member} kick : {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banni : {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount+1)

# ======================
# MUSIQUE
# ======================

ytdl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

music_queue = []

async def play_next(ctx):
    if music_queue:
        url = music_queue.pop(0)
        source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_opts)
        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    info = ytdl.extract_info(url, download=False)
    audio = info["url"]

    music_queue.append(audio)
    await ctx.send("🎵 Ajouté à la file")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skippé")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        music_queue.clear()
        await ctx.send("⏹️ Arrêté")

# ======================
# START
# ======================

bot.run(MTQ3MTE2MjE1NjgyODU5MDI2Nw.GpVfgg.wKFdUs-QoXbEX30EvjbnvDba5-Wt7D09XaFv3E)
