import discord
from discord.ext import commands
import asyncio
import os
import tempfile

from typecast.client import Typecast
from typecast.models import TTSRequest, Output


# =========================================================
# ==================== 여기만 수정 ========================
# =========================================================

DISCORD_TOKEN = "MTU0MjUyODY3NjQwNTQ0ODcyNQ.GfNhLm.ZReiDTXOd9j7g3ORFpHe0HE09M2mXxKJXXf-hU"

TYPECAST_API_KEY = "__pltFsxhNJKKwxCJ62hs4aqiKVcBRZsU52Mk4ZgsCRLs"


# =========================================================
# ==================== 목소리 설정 =========================
# =========================================================

VOICES = {
    "1": "tc_61532cab9119555d352f5c69",
    "2": "tc_5c547544fcfee90007fed455"
}

DEFAULT_VOICE = "1"

current_voice = {}


# =========================================================
# ==================== Discord 설정 ========================
# =========================================================

intents = discord.Intents.default()

intents.message_content = True
intents.voice_states = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# ==================== Typecast ===========================
# =========================================================

client = Typecast(
    api_key=TYPECAST_API_KEY
)


# =========================================================
# ==================== 봇 시작 =============================
# =========================================================

@bot.event
async def on_ready():

    print("====================================")
    print("정딸봇 로그인 성공!")
    print(f"봇 이름 : {bot.user}")
    print(f"봇 ID   : {bot.user.id}")
    print("====================================")


# =========================================================
# ==================== 메시지 처리 ==========================
# =========================================================

@bot.event
async def on_message(message):

    # 봇이 보낸 메시지는 무시
    if message.author.bot:
        return


    print(f"[메시지 확인] {message.content}")


    # -----------------------------------------------------
    # 정딸아 도와줘
    # -----------------------------------------------------

    if "정딸아 도와줘" in message.content.lower():

        await send_help(message.channel)

        return


    # -----------------------------------------------------
    # ★ 중요 ★
    #
    # 일반 메시지는 아무것도 하지 않는다.
    #
    # 명령어만 process_commands()로 넘긴다.
    # -----------------------------------------------------

    await bot.process_commands(message)


# =========================================================
# ==================== !입장 ===============================
# =========================================================

@bot.command(name="입장")
async def join(ctx):

    print("[명령어] !입장 실행됨")


    # 사용자가 음성채널에 있는지 확인
    if ctx.author.voice is None:

        await ctx.send(
            "먼저 음성 채널에 들어가~아이!"
        )

        return


    channel = ctx.author.voice.channel


    try:

        # 이미 봇이 음성채널에 있는 경우
        if ctx.voice_client is not None:

            vc = ctx.voice_client


            # 연결되어 있으면
            if vc.is_connected():

                # 같은 채널
                if vc.channel.id == channel.id:

                    await ctx.send(
                        f"이미 {channel.name}에 있어 아이!"
                    )

                    return


                # 다른 채널이면 이동
                await vc.move_to(channel)

                await ctx.send(
                    f"{channel.name}으로 이동했어~아이!"
                )

                return


        # 새로 연결
        await channel.connect()


        await ctx.send(
            f"{channel.name}에 등장했어~아이~!"
        )


        print(
            f"[입장 성공] {channel.name}"
        )


    except discord.Forbidden:

        print(
            "[입장 실패] Discord 권한 없음"
        )

        await ctx.send(
            "음성채널에 들어갈 권한이 없어 아이!\n"
            "봇에게 **연결(Connect)** 권한과 "
            "**말하기(Speak)** 권한을 줘줘!"
        )


    except Exception as e:

        print("====================================")
        print("[입장 오류]")
        print(type(e).__name__)
        print(e)
        print("====================================")


        await ctx.send(
            "음성채널 입장 중 오류가 발생했어 아이!\n"
            f"`{type(e).__name__}: {e}`"
        )


# =========================================================
# ==================== !퇴장 ===============================
# =========================================================

@bot.command(name="퇴장")
async def leave(ctx):

    print("[명령어] !퇴장 실행됨")


    if ctx.voice_client is None:

        await ctx.send(
            "음성 채널에 있지 않잖아 아이."
        )

        return


    try:

        await ctx.voice_client.disconnect()


        await ctx.send(
            "나갔어아이!"
        )


    except Exception as e:

        print(
            f"[퇴장 오류] {type(e).__name__}: {e}"
        )

        await ctx.send(
            f"퇴장 오류: `{e}`"
        )


# =========================================================
# ==================== !목소리 ==============================
# =========================================================

@bot.command(name="목소리")
async def set_voice(
    ctx,
    number: str = None
):

    print(
        f"[명령어] !목소리 {number}"
    )


    if number not in VOICES:

        await ctx.send(
            "사용법:\n"
            "`!목소리 1`\n"
            "`!목소리 2`"
        )

        return


    current_voice[
        ctx.guild.id
    ] = number


    await ctx.send(
        f"목소리를 {number}번으로 변경했어 아이!"
    )


# =========================================================
# ==================== !읽어 ================================
# =========================================================

@bot.command(name="읽어")
async def read_text(
    ctx,
    *,
    text: str = None
):

    print(
        f"[명령어] !읽어 {text}"
    )


    # 읽을 내용이 없는 경우
    if not text:

        await ctx.send(
            "읽을 내용을 같이 적어줘 아이!\n"
            "예시: `!읽어 안녕하세요!`"
        )

        return


    # 봇이 음성채널에 있는지 확인
    if ctx.voice_client is None:

        await ctx.send(
            "먼저 `!입장`으로 음성채널에 불러줘 아이!"
        )

        return


    if not ctx.voice_client.is_connected():

        await ctx.send(
            "음성채널 연결이 끊어졌어 아이!"
        )

        return


    vc = ctx.voice_client


    try:

        # 현재 목소리
        voice_num = current_voice.get(
            ctx.guild.id,
            DEFAULT_VOICE
        )

        voice_id = VOICES[voice_num]


        # 현재 재생 중이면 기다림
        if vc.is_playing():

            await ctx.send(
                "잠깐만 아이~ 지금 읽고 있어!"
            )

            while vc.is_playing():

                await asyncio.sleep(0.3)


        # -------------------------------------------------
        # Typecast
        # -------------------------------------------------

        response = client.text_to_speech(

            TTSRequest(

                text=text,

                model="ssfm-v30",

                voice_id=voice_id,

                language="kor",

                output=Output(
                    audio_format="mp3"
                )
            )
        )


        # -------------------------------------------------
        # 임시 MP3
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as f:

            f.write(
                response.audio_data
            )

            temp_path = f.name


        # -------------------------------------------------
        # Discord 재생
        # -------------------------------------------------

        source = discord.FFmpegPCMAudio(
            temp_path
        )


        def after_play(error):

            if error:

                print(
                    f"[재생 오류] {error}"
                )


            if os.path.exists(temp_path):

                try:

                    os.remove(temp_path)

                except Exception:

                    pass


        vc.play(
            source,
            after=after_play
        )


    except Exception as e:

        print("====================================")
        print("[TTS 오류]")
        print(type(e).__name__)
        print(e)
        print("====================================")


        await ctx.send(
            f"TTS 오류가 발생했어 아이!\n"
            f"`{type(e).__name__}: {e}`"
        )


# =========================================================
# ==================== 도움말 ===============================
# =========================================================

async def send_help(channel):

    embed = discord.Embed(

        title="정딸봇 사용법 아이~!",

        description="내가 할 수 있는 것들을 알려줄게!",

        color=0xFF69B4
    )


    embed.add_field(
        name="!입장",
        value="현재 음성채널에 들어와!",
        inline=False
    )


    embed.add_field(
        name="!퇴장",
        value="음성채널에서 나가!",
        inline=False
    )


    embed.add_field(
        name="!목소리 1",
        value="1번 목소리로 변경!",
        inline=False
    )


    embed.add_field(
        name="!목소리 2",
        value="2번 목소리로 변경!",
        inline=False
    )


    embed.add_field(
        name="!읽어 내용",
        value="`!읽어 안녕하세요!`라고 하면 읽어줘!",
        inline=False
    )


    embed.add_field(
        name="일반 채팅",
        value="일반 채팅은 읽지 않아!",
        inline=False
    )


    await channel.send(
        embed=embed
    )


# =========================================================
# ==================== !도와줘 ==============================
# =========================================================

@bot.command(name="도와줘")
async def help_command(ctx):

    print("[명령어] !도와줘 실행됨")

    await send_help(
        ctx.channel
    )


# =========================================================
# ==================== 명령어 오류 ==========================
# =========================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

    # 존재하지 않는 명령어
    if isinstance(
        error,
        commands.CommandNotFound
    ):

        print(
            f"[없는 명령어] {ctx.message.content}"
        )

        return


    print("====================================")
    print("[명령어 오류]")
    print(f"입력 : {ctx.message.content}")
    print(f"종류 : {type(error).__name__}")
    print(f"내용 : {error}")
    print("====================================")


    await ctx.send(
        "명령어 실행 중 오류가 발생했어 아이!\n"
        f"`{type(error).__name__}: {error}`"
    )


# =========================================================
# ==================== 봇 실행 ==============================
# =========================================================

print("정딸봇을 시작하는 중...")

bot.run(
    DISCORD_TOKEN
)
