import discord, random, dotenv, json, os
from discord.ext import commands

dotenv.load_dotenv()

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 자동 삭제를 위한 
import asyncio
DELETE_AFTER = 120

async def delete_after(msg: discord.Message, delay: int):
    """
    주어진 메시지를 `delay` 초 뒤에 삭제합니다.
    - 봇이 “Manage Messages” 권한을 가지고 있어야 합니다.
    """
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except discord.Forbidden:
        # 권한 부족 시 사용자에게 알려줌
        await msg.channel.send(
            f"⚠️ {msg.author.mention} 봇이 메시지를 삭제할 수 없습니다. (Manage Messages 권한 필요)"
        )
    except Exception as e:
        print(f"[delete_after] 에러: {e}")

# 커맨드의 응답 메시지를 `delay` 초 뒤에 자동 삭제해 주는 데코레이터
def auto_delete(delay: int = 10):
    def decorator(func):
        async def wrapper(ctx, *args, **kwargs):
            reply = await func(ctx, *args, **kwargs)
            # 커맨드가 `ctx.send()` 를 반환하도록 설계되어야 함
            if isinstance(reply, discord.Message):
                asyncio.create_task(delete_after(reply, delay))
            return reply
        return wrapper
    return decorator

# ────────────────────────────────────────────────────────────────────────
# 1️⃣ 제어 메시지의 ID를 저장할 전역 변수
CONTROL_MESSAGE_ID = 1481681635626848301       # 초기값: None
# 모자디코 메세지 - 1481681635626848301
# 테스트 - 1532744688640069822

# ────────────────────────────────────────────────────────────────────────
# 2️⃣ 제어 메시지 보낼 채널 ID (예시: 123456789012345678)
CONTROL_CHANNEL_ID = 1437940729547849888
# 모자 디코 채널 - 1437940729547849888
# 테스트 채널 - 1435258015077892096

def load_control_message_ids():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, encoding="utf-8") as config_file:
        config = json.load(config_file)

    discord_config = config.get("discord", {})
    if not isinstance(discord_config, dict):
        raise ValueError("'discord' 설정은 객체여야 합니다.")

    configured_channels = discord_config.get("control_channels", [])
    if not isinstance(configured_channels, list):
        raise ValueError("'discord.control_channels' 설정은 배열이어야 합니다.")

    if not configured_channels:
        return {CONTROL_CHANNEL_ID: CONTROL_MESSAGE_ID}

    channel_ids = {}
    for index, channel_config in enumerate(configured_channels):
        if not isinstance(channel_config, dict):
            raise ValueError(f"discord.control_channels[{index}] 설정은 객체여야 합니다.")

        channel_id = channel_config.get("channel_id")
        message_id = channel_config.get("message_id")
        if isinstance(channel_id, bool) or not isinstance(channel_id, int) or channel_id <= 0:
            raise ValueError(f"discord.control_channels[{index}].channel_id는 양의 정수여야 합니다.")
        if message_id is not None and (
            isinstance(message_id, bool) or not isinstance(message_id, int) or message_id <= 0
        ):
            raise ValueError(
                f"discord.control_channels[{index}].message_id는 양의 정수 또는 null이어야 합니다."
            )
        if channel_id in channel_ids:
            raise ValueError(f"제어 채널 ID가 중복되었습니다: {channel_id}")

        channel_ids[channel_id] = message_id

    return channel_ids


CONTROL_MESSAGE_IDS = load_control_message_ids()

# ────────────────────────────────────────────────────────────────────────
# 3️⃣ 리모컨 이모지 → 명령 매핑
EMOJI_CMD_MAP = {
    '🎲': 'roll',      # 주사위 굴리기
    '🙍‍♂️': 'randchar',      # 랜덤캐릭
    '👾': 'randboss',    # 랜덤보스
}

# ────────────────────────────────────────────────────────────────────────
# 4️⃣ 일반 명령어(기존 코드 그대로)
@bot.command(name='roll')
@auto_delete(DELETE_AFTER)
async def roll(ctx, times: int = 1):
    if times < 1 or times > 10:
        await ctx.send('⚠️ 1~10 사이 정수만 입력해 주세요.')
        return
    nums = [random.randint(1, 20) for _ in range(times)]
    return await ctx.send(f'🎲 결과: {" | ".join(map(str, nums))}')

@bot.command(name='randchar')
@auto_delete(DELETE_AFTER)
async def calc_cmd(ctx):
    # 다른 파이썬 스크립트 실행해서 그 결과를 보여줌
    # 비동기 방식으로 실행 (python3 calc.py)
    process = await asyncio.create_subprocess_exec(
        "python3", "random_char.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await ctx.send(f"❌ 오류 발생:\n{stderr.decode().strip()}")
        return

    out_text = stdout.decode().strip()
    return await ctx.send(out_text)

@bot.command(name='randboss')
@auto_delete(DELETE_AFTER)
async def calc_cmd(ctx):
    # 다른 파이썬 스크립트 실행해서 그 결과를 보여줌
    # 비동기 방식으로 실행 (python3 calc.py)
    process = await asyncio.create_subprocess_exec(
        "python3", "random_boss.py",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await ctx.send(f"❌ 오류 발생:\n{stderr.decode().strip()}")
        return

    out_text = stdout.decode().strip()
    return await ctx.send(out_text)

# ────────────────────────────────────────────────────────────────────────
# 5️⃣ 설정된 각 채널에 제어 메시지 전송
@bot.event
async def on_ready():
    for channel_id, message_id in CONTROL_MESSAGE_IDS.items():
        channel = bot.get_channel(channel_id)
        if channel is None:
            try:
                channel = await bot.fetch_channel(channel_id)
            except (discord.NotFound, discord.Forbidden) as error:
                print(f"제어 채널 {channel_id}에 접근할 수 없습니다: {error}")
                continue

        if message_id is None:
            msg = await channel.send(
                "아래 이모티콘을 선택해 명령어를 실행해주세요.\n"
                "🎲 – 랜덤 숫자(1-20) 뽑기\n"
                "🙍‍♂️ – 랜덤 캐릭터 뽑기\n"
                "👾 – 랜덤 보스 뽑기\n"
                "결과 메세지는 일정 시간 뒤에 사라집니다."
            )
            CONTROL_MESSAGE_IDS[channel_id] = msg.id

            for emoji in EMOJI_CMD_MAP:
                await msg.add_reaction(emoji)

    print(f"Bot ready - Control messages: {CONTROL_MESSAGE_IDS}")

# ────────────────────────────────────────────────────────────────────────
# 6️⃣ 반응을 받아서 명령 실행
@bot.event
async def on_raw_reaction_add(payload):
    # 1️⃣ 제어 메시지인지 확인
    if CONTROL_MESSAGE_IDS.get(payload.channel_id) != payload.message_id:
        return

    # 2️⃣ 봇 자신의 반응은 무시
    if bot.user is not None and payload.user_id == bot.user.id:
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

    # 5️⃣ 명령 실행
    await cmd(ctx)

# ────────────────────────────────────────────────────────────────────────
# 7️⃣ 실행

if __name__ == "__main__":
    # 토큰은 .env로부터 읽어옵니다.
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")
    bot.run(token)
