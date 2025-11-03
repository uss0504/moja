import random
import discord
from discord.ext import commands

import dotenv, os
dotenv.load_dotenv()

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ────────────────────────────────────────────────────────────────────────
# 1️⃣ 제어 메시지의 ID를 저장할 전역 변수
CONTROL_MESSAGE_ID = None          # 초기값: 아직 없음

# ────────────────────────────────────────────────────────────────────────
# 2️⃣ 제어 메시지 보낼 채널 ID (예시: 123456789012345678)
CONTROL_CHANNEL_ID = 762314435867574277  # <-- 실제 채널 ID로 바꿔주세요

# ────────────────────────────────────────────────────────────────────────
# 3️⃣ 리모컨 이모지 → 명령 매핑
EMOJI_CMD_MAP = {
    '🎲': 'roll',      # 주사위 굴리기
    '🔒': 'lock',      # 채널 잠그기
    '🔓': 'unlock',    # 채널 잠금 해제
    '✏️': 'rename',    # 채널 이름 바꾸기
}

# ────────────────────────────────────────────────────────────────────────
# 4️⃣ 일반 명령어(기존 코드 그대로)
@bot.command(name='roll')
async def roll(ctx, times: int = 1):
    if times < 1 or times > 10:
        await ctx.send('⚠️ 1~10 사이 정수만 입력해 주세요.')
        return
    nums = [random.randint(1, 20) for _ in range(times)]
    await ctx.send(f'🎲 {ctx.author.mention} 님의 결과: {" | ".join(map(str, nums))}')

@bot.command(name='lock')
async def lock(ctx):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await ctx.send(f'🔒 {ctx.channel.mention} 채널을 잠그았습니다.')
    else:
        await ctx.send('❌ 잠그려면 **Manage Channels** 권한이 필요해요.')

@bot.command(name='unlock')
async def unlock(ctx):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.set_permissions(ctx.guild.default_role, read_messages=True)
        await ctx.send(f'🔓 {ctx.channel.mention} 채널의 잠금을 해제했습니다.')
    else:
        await ctx.send('❌ 잠금을 해제하려면 **Manage Channels** 권한이 필요해요.')

@bot.command(name='rename')
async def rename(ctx, *, new_name: str):
    if ctx.author.guild_permissions.manage_channels:
        await ctx.channel.edit(name=new_name)
        await ctx.send(f'✏️ 채널명을 **{new_name}** 으로 바꿨습니다.')
    else:
        await ctx.send('❌ 채널명을 바꾸려면 **Manage Channels** 권한이 필요해요.')

# ────────────────────────────────────────────────────────────────────────
# 5️⃣ 제어 메시지 전송(봇이 준비됐을 때 한 번만)
@bot.event
async def on_ready():
    global CONTROL_MESSAGE_ID
    if CONTROL_MESSAGE_ID is None:
        channel = bot.get_channel(CONTROL_CHANNEL_ID)
        if channel:
            msg = await channel.send(
                "🔢 **리모컨**\n"
                "🎲 – 주사위 굴리기\n"
                "🔒 – 채널 잠그기\n"
                "🔓 – 채널 잠금 해제\n"
                "✏️ – 채널 이름 바꾸기"
            )
            CONTROL_MESSAGE_ID = msg.id

            # 6️⃣ 미리 이모지 추가
            for emoji in EMOJI_CMD_MAP.keys():
                await msg.add_reaction(emoji)
    print(f'Bot ready – Control message id: {CONTROL_MESSAGE_ID}')

# ────────────────────────────────────────────────────────────────────────
# 6️⃣ 반응을 받아서 명령 실행
@bot.event
async def on_raw_reaction_add(payload):
    # 1️⃣ 제어 메시지인지 확인
    if payload.message_id != CONTROL_MESSAGE_ID:
        return

    # 2️⃣ **봇 자신의 반응은 무시** (버그 방지)
    if payload.user_id == bot.user.id:
        return

    # 3️⃣ 이모지 매핑
    emoji = str(payload.emoji)
    cmd_name = EMOJI_CMD_MAP.get(emoji)
    if not cmd_name:
        return

    # 4️⃣ Context & 명령 가져오기
    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        return
    try:
        message = await channel.fetch_message(payload.message_id)
    except discord.NotFound:
        return

    ctx = await bot.get_context(message)
    cmd = bot.get_command(cmd_name)
    if cmd is None:
        return

    # 5️⃣ 명령 실행
    await cmd(ctx)

    # 6️⃣ 사용자의 반응을 지워서 재사용 가능하게
    user = bot.get_user(payload.user_id) or await bot.fetch_user(payload.user_id)
    try:
        await message.remove_reaction(payload.emoji, user)
    except discord.Forbidden:
        # Manage Messages 권한이 없을 때
        await channel.send(
            f'{ctx.author.mention} 반응을 지울 수 없어요. (권한 부족?)'
        )
    except Exception as e:
        print(f'반응 삭제 실패: {e}')

# ────────────────────────────────────────────────────────────────────────
# 7️⃣ 실행

if __name__ == "__main__":
    # 토큰은 환경 변수로부터 읽어옵니다.
    # 윈도우 예시: set DISCORD_TOKEN=여기에_토큰을_붙여
    # 리눅스/맥 예시: export DISCORD_TOKEN=여기에_토큰을_붙여
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")
    bot.run(token)
