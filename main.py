import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from myserver import server_on

# ============================================================
# Configuration
# ============================================================
TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not TOKEN:
    raise RuntimeError(
        "ไม่พบ TOKEN หรือ DISCORD_TOKEN ใน Environment Variables"
    )

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# guild_id -> AFK information
# {"channel_id": int, "channel_name": str}
afk_rooms = {}

# guild_id -> discord.VoiceClient
voice_clients = {}


# ============================================================
# Helpers
# ============================================================
async def connect_afk(guild: discord.Guild, channel: discord.VoiceChannel):
    """Connect/reconnect the bot to the selected voice channel."""
    old = voice_clients.get(guild.id)

    if old:
        try:
            await old.disconnect(force=True)
        except Exception:
            pass
        voice_clients.pop(guild.id, None)

    vc = await channel.connect(
        reconnect=True,
        self_deaf=True,
        self_mute=True
    )

    voice_clients[guild.id] = vc
    afk_rooms[guild.id] = {
        "channel_id": channel.id,
        "channel_name": channel.name,
    }

    print(f"[AFK] {guild.name} -> {channel.name}")
    return vc


async def reconnect_afk(guild_id: int):
    """Keep trying to reconnect while AFK is enabled."""
    while guild_id in afk_rooms:
        data = afk_rooms[guild_id]
        guild = bot.get_guild(guild_id)

        if guild is None:
            await asyncio.sleep(10)
            continue

        channel = guild.get_channel(data["channel_id"])

        if channel is None:
            print(f"[AFK] Channel {data['channel_id']} no longer exists.")
            await asyncio.sleep(30)
            continue

        current = voice_clients.get(guild_id)

        if current and current.is_connected():
            return

        try:
            vc = await channel.connect(
                reconnect=True,
                self_deaf=True,
                self_mute=True
            )
            voice_clients[guild_id] = vc
            print(f"[AFK] Reconnected -> {channel.name}")
            return
        except Exception as e:
            print(f"[AFK] Reconnect failed: {e}")
            await asyncio.sleep(10)


# ============================================================
# Bot Events
# ============================================================
@bot.event
async def on_ready():
    print("================================")
    print(" Discord AFK Bot")
    print("================================")
    print(f"Bot Online: {bot.user}")
    print(f"Servers: {len(bot.guilds)}")

    try:
        if GUILD_ID:
            guild_obj = discord.Object(id=int(GUILD_ID))
            bot.tree.copy_global_to(guild=guild_obj)
            synced = await bot.tree.sync(guild=guild_obj)
            print(f"Slash Commands synced to server: {len(synced)}")
        else:
            synced = await bot.tree.sync()
            print(f"Global Slash Commands synced: {len(synced)}")
    except Exception as e:
        print(f"Slash sync error: {e}")

    print("🟢 Bot พร้อมใช้งาน")
    print("================================")


@bot.event
async def on_voice_state_update(member, before, after):
    # Only react to the bot itself.
    if not bot.user or member.id != bot.user.id:
        return

    guild_id = member.guild.id

    # If /afk is enabled and the bot gets disconnected, reconnect.
    if guild_id in afk_rooms and after.channel is None:
        print("[AFK] Bot disconnected from Voice. Reconnecting...")
        await asyncio.sleep(3)

        if guild_id in afk_rooms:
            await reconnect_afk(guild_id)


# ============================================================
# Original bot features
# ============================================================
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1140633489520205934)
    if channel:
        text = f"Welcome to the server, {member.mention}!"
        embed = discord.Embed(
            title="Welcome to the server!",
            description=text,
            color=0x66FFFF
        )
        await channel.send(text)
        await channel.send(embed=embed)

        try:
            await member.send(text)
        except discord.Forbidden:
            pass


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(1140633489520205934)
    if channel:
        await channel.send(f"{member.name} has left the server!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    mes = message.content

    if mes == "hello":
        await message.channel.send("Hello It's me")
    elif mes == "hi bot":
        await message.channel.send("Hello, " + str(message.author.name))

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f"hello {ctx.author.name}!")


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.tree.command(name="hellobot", description="Replies with Hello")
async def hellocommand(interaction: discord.Interaction):
    await interaction.response.send_message("Hello It's me BOT DISCORD")


@bot.tree.command(name="name")
@app_commands.describe(name="What's your name?")
async def namecommand(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello {name}")


@bot.tree.command(name="help", description="Bot Commands")
async def helpcommand(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help Me! - Bot Commands",
        description="Bot Commands",
        color=0x66FFFF,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="/afk", value="เลือกห้อง Voice ให้บอท AFK", inline=False)
    embed.add_field(name="/off", value="ปิด AFK และให้บอทออกจากห้อง", inline=False)
    embed.add_field(name="/hellobot", value="ทดสอบบอท", inline=True)
    embed.add_field(name="/name", value="ทักทายด้วยชื่อ", inline=True)
    await interaction.response.send_message(embed=embed)


# ============================================================
# AFK Slash Commands
# ============================================================
@bot.tree.command(
    name="afk",
    description="ให้บอทเข้า Voice Channel แบบ AFK ต่อเนื่อง"
)
@app_commands.describe(channel="เลือกห้อง Voice ที่ต้องการให้บอทเข้า")
async def afk_command(
    interaction: discord.Interaction,
    channel: discord.VoiceChannel
):
    await interaction.response.defer()

    if interaction.guild is None:
        await interaction.followup.send("❌ คำสั่งนี้ใช้ในเซิร์ฟเวอร์เท่านั้น")
        return

    # Check the bot's permissions in the selected channel.
    me = interaction.guild.me
    if me:
        perms = channel.permissions_for(me)
        if not perms.view_channel or not perms.connect:
            await interaction.followup.send(
                "❌ บอทไม่มีสิทธิ์ในห้องนี้\n"
                "ต้องมี `View Channel` และ `Connect`"
            )
            return

    try:
        await connect_afk(interaction.guild, channel)

        await interaction.followup.send(
            f"✅ **เปิด AFK สำเร็จ**\n\n"
            f"🔊 ห้อง: {channel.mention}\n"
            f"🟢 สถานะ: ออนไลน์\n"
            f"♾️ บอทจะพยายามอยู่ในห้องต่อเนื่อง\n\n"
            f"ใช้ `/off` เพื่อปิด AFK"
        )
    except Exception as e:
        print(f"[AFK ERROR] {e}")
        await interaction.followup.send(
            "❌ บอทเข้า Voice ไม่สำเร็จ\n"
            "ตรวจสอบสิทธิ์ `View Channel` และ `Connect`"
        )


@bot.tree.command(
    name="off",
    description="ปิด AFK และให้บอทออกจาก Voice Channel"
)
async def off_command(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ คำสั่งนี้ใช้ในเซิร์ฟเวอร์เท่านั้น",
            ephemeral=True
        )
        return

    guild_id = interaction.guild.id

    if guild_id not in afk_rooms:
        await interaction.response.send_message(
            "ℹ️ ตอนนี้บอทไม่ได้เปิด AFK ในเซิร์ฟเวอร์นี้",
            ephemeral=True
        )
        return

    afk_rooms.pop(guild_id, None)

    vc = voice_clients.pop(guild_id, None)

    if vc:
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass

    await interaction.response.send_message(
        "🔴 **ปิด AFK แล้ว**\n"
        "บอทออกจากห้อง Voice เรียบร้อย"
    )

    print(f"[AFK OFF] {interaction.guild.name}")


# ============================================================
# Start
# ============================================================
server_on()

bot.run(os.getenv('TOKEN'))
