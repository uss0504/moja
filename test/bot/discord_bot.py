# bot.py
# 아직 Hello World 단계임.
import os
import discord
from discord.ext import commands

import dotenv
dotenv.load_dotenv()

# ① Intents 설정
intents = discord.Intents.default()
intents.message_content = True      # 메시지 내용 읽기

# ② 봇 객체 생성
bot = commands.Bot(command_prefix="!", intents=intents)

# ③ 이벤트: 봇이 준비되었을 때
@bot.event
async def on_ready():
    print(f"✅ {bot.user}이(가) 로그인했습니다!")

# ④ 커맨드: !ping 으로 Pong! 반환
@bot.command(name="핑")
async def ping(ctx: commands.Context):
    await ctx.send("퐁!")

# ⑤ (옵션) 슬래시 커맨드: /ping 으로 Pong! 반환
# @bot.tree.command(name="ping", description="Ping-Pong")
# async def ping_slash(interaction: discord.Interaction):
#     await interaction.response.send_message("Pong!")

import asyncio

@bot.command(name="랜덤캐릭")
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
    await ctx.send(out_text)

    
@bot.command(name="랜덤보스")
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
    await ctx.send(out_text)


# ⑥ 실행
if __name__ == "__main__":
    # 토큰은 환경 변수로부터 읽어옵니다.
    # 윈도우 예시: set DISCORD_TOKEN=여기에_토큰을_붙여
    # 리눅스/맥 예시: export DISCORD_TOKEN=여기에_토큰을_붙여
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")
    bot.run(token)

