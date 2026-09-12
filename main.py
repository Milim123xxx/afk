import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from myserver import server_on


TOKEN = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
GUILD_ID_TEXT = os.getenv("GUILD_ID")

if not TOKEN:
    raise RuntimeError("ไม่พบ TOKEN หรือ DISCORD_TOKEN ใน Environment Variables")
if not GUILD_ID_TEXT:
    raise RuntimeError("ไม่พบ GUILD_ID ใน Environment Variables")
try:
    GUILD_ID = int(GUILD_ID_TEXT)
except ValueError as exc:
    raise RuntimeError("GUILD_ID ต้องเป็นตัวเลข Server ID ของ Discord") from exc

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("afk-bot")

# AFK bot does not need privileged intents.
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# guild_id -> configured voice channel id
afk_channels: dict[int, int] = {}
voice_clients: dict[int, discord.VoiceClient] = {}
reconnect_tasks: dict[int, asyncio.Task] = {}
synced = False


async def disconnect_voice(guild_id: int) -> None:
    vc = voice_clients.pop(guild_id, None)
    if vc is not None:
        try:
            await vc.disconnect(force=True)
        except discord.DiscordException:
            logger.debug("Voice disconnect failed", exc_info=True)


async def connect_afk(guild: discord.Guild, channel: discord.VoiceChannel) -> None:
    await disconnect_voice(guild.id)
    vc = await channel.connect(reconnect=True, self_deaf=True, self_mute=True)
    voice_clients[guild.id] = vc
    afk_channels[guild.id] = channel.id
    logger.info("AFK enabled: guild=%s channel=%s", guild.id, channel.id)


async def reconnect_afk(guild_id: int) -> None:
    if guild_id in reconnect_tasks:
        return

    async def retry() -> None:
        delay = 5
        try:
            while guild_id in afk_channels:
                guild = bot.get_guild(guild_id)
                if guild is None:
                    await asyncio.sleep(delay)
                    continue

                channel = guild.get_channel(afk_channels[guild_id])
                if not isinstance(channel, discord.VoiceChannel):
                    logger.warning("Configured voice channel was not found: %s", afk_channels[guild_id])
                    await asyncio.sleep(30)
                    continue

                current = voice_clients.get(guild_id)
                if current and current.is_connected():
                    return

                try:
                    vc = await channel.connect(reconnect=True, self_deaf=True, self_mute=True)
                    voice_clients[guild_id] = vc
                    logger.info("AFK reconnected: guild=%s channel=%s", guild_id, channel.id)
                    return
                except (discord.ClientException, discord.DiscordException, OSError) as exc:
                    logger.warning("Reconnect failed: %s; retrying in %ss", exc, delay)
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 60)
        except asyncio.CancelledError:
            raise
        finally:
            reconnect_tasks.pop(guild_id, None)

    reconnect_tasks[guild_id] = asyncio.create_task(retry())


@bot.event
async def on_ready() -> None:
    global synced
    logger.info("ออนไลน์แล้ว: %s | servers=%s", bot.user, len(bot.guilds))
    if synced:
        return
    guild = discord.Object(id=GUILD_ID)
    try:
        bot.tree.copy_global_to(guild=guild)
        commands_synced = await bot.tree.sync(guild=guild)
        synced = True
        logger.info("ซิงก์คำสั่งสำเร็จ: %s คำสั่ง", len(commands_synced))
    except discord.DiscordException:
        logger.exception("ซิงก์ Slash Commands ไม่สำเร็จ")


@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
) -> None:
    if bot.user and member.id == bot.user.id and after.channel is None:
        if member.guild.id in afk_channels:
            logger.warning("บอตหลุดจากห้องโทร กำลังเชื่อมต่อกลับ")
            await reconnect_afk(member.guild.id)


@bot.tree.command(name="afk", description="ให้บอตเข้าไปอยู่ในห้องโทรแบบ AFK")
@app_commands.describe(channel="เลือกห้องโทรที่ต้องการให้บอตเข้า")
async def afk_command(interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("คำสั่งนี้ใช้ในเซิร์ฟเวอร์เท่านั้น", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    me = interaction.guild.me
    if me is not None:
        permissions = channel.permissions_for(me)
        if not permissions.view_channel or not permissions.connect:
            await interaction.followup.send(
                "บอตไม่มีสิทธิ์ View Channel หรือ Connect ในห้องนี้", ephemeral=True
            )
            return

    try:
        await connect_afk(interaction.guild, channel)
        await interaction.followup.send(
            f"เปิด AFK แล้ว: {channel.mention}\nบอตจะปิดไมค์ ปิดเสียง และพยายามเชื่อมต่อกลับเมื่อหลุด",
            ephemeral=True,
        )
    except (discord.ClientException, discord.DiscordException, OSError):
        logger.exception("เข้า Voice Channel ไม่สำเร็จ")
        await interaction.followup.send(
            "เข้า Voice ไม่สำเร็จ โปรดตรวจสิทธิ์ View Channel และ Connect", ephemeral=True
        )


@bot.tree.command(name="off", description="ให้บอตออกจากห้องโทรและปิด AFK")
async def off_command(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message("คำสั่งนี้ใช้ในเซิร์ฟเวอร์เท่านั้น", ephemeral=True)
        return

    guild_id = interaction.guild.id
    if guild_id not in afk_channels:
        await interaction.response.send_message("บอตไม่ได้เปิด AFK อยู่", ephemeral=True)
        return

    afk_channels.pop(guild_id, None)
    task = reconnect_tasks.pop(guild_id, None)
    if task is not None:
        task.cancel()
    await disconnect_voice(guild_id)
    await interaction.response.send_message("ปิด AFK และออกจากห้องโทรแล้ว", ephemeral=True)
    logger.info("AFK disabled: guild=%s", guild_id)


server_on()
bot.run(TOKEN)
