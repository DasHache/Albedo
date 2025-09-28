import discord, re, aiohttp
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

handler= logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

apex_role = "Apex"
lol_role = "LoL"
cs_role = "CS"
valo_role = "Valo"
peak_role = "Peak"
over_role = 1421883935306027100
roleMessageId = 1421531983074426991

FALLBACKS = [
    "https://i.pinimg.com/736x/d3/6c/e0/d36ce01c2ff2642c1315082687354a22.jpg",
    "https://i.pinimg.com/736x/30/32/27/303227702bb7e7d0244180c31efce99d.jpg",
    "https://i.pinimg.com/736x/aa/02/dd/aa02dda330e050812f6fa84ff9ef829d.jpg",
    "https://i.pinimg.com/736x/b7/0f/db/b70fdbed72aab2127f8b97f1b007b980.jpg",
    "https://i.pinimg.com/736x/8a/4c/6d/8a4c6d9f33abb8bc5264e988cba320c5.jpg",
    "https://i.pinimg.com/736x/2f/2d/37/2f2d3796703b7cba182c05e5b3cf9970.jpg",
    "https://i.pinimg.com/736x/4a/21/74/4a217443b7d6a4b4a4bdea899901426a.jpg",
    "https://i.pinimg.com/736x/49/7f/e1/497fe1a5c6a2824b60406a60cc2a29db.jpg",
    "https://i.pinimg.com/736x/22/9d/9c/229d9c09c201a16ede2524a3811b678f.jpg",
    "https://i.pinimg.com/1200x/13/65/96/13659608385246d194f298ccfe0e7a95.jpg",
    "https://i.pinimg.com/736x/42/0d/b4/420db4b0ba98cfa82a264947602b33f0.jpg",
    "https://i.pinimg.com/1200x/1e/d0/2f/1ed02f1396fcf5662d0345aaeb408f18.jpg",
    "https://i.pinimg.com/1200x/6b/20/83/6b20835630dafa7261d8e343e1280cbd.jpg",
    "https://i.pinimg.com/736x/38/60/a5/3860a5fcaa3503ff9c17160e6d7d0176.jpg",
    "https://i.pinimg.com/1200x/9a/b2/81/9ab2818d0c12026c285ffcf24edf65bb.jpg"
]

HTTP_TIMEOUT = 8
IMG_EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif)(\?.*)?$", re.I)

def get_role(payload, guild):
    emoji = payload.emoji.name
    match emoji:
        case '🅰️':
            role = discord.utils.get(guild.roles, name=apex_role)
        case '🇨':
            role = discord.utils.get(guild.roles, name=cs_role)
        case '🇱':
            role = discord.utils.get(guild.roles, name=lol_role)
        case '🇻':
            role = discord.utils.get(guild.roles, name=valo_role)
        case '🇵':
            role = discord.utils.get(guild.roles, name=peak_role)
        case '🇴':
            role = discord.utils.get(guild.roles, id=over_role)
        case _:
            role = discord.utils.get(guild.roles, name="Grosse folle")
    return role

def is_image_url(url: str) -> bool:
    if IMG_EXT_RE.search(url or ""):
        return True
    try:
        h = requests.head(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
        ct = h.headers.get("Content-Type", "")
        return ct.startswith("image/")
    except Exception:
        return False

async def get_from_some_random_api(session: aiohttp.ClientSession) -> str | None:
    try:
        async with session.get(
            "https://some-random-api.com/animal/racoon",
            timeout=aiohttp.ClientTimeout(total=8),
        ) as r:
            if r.status != 200:
                return None
            d = await r.json()
            url = d.get("image")
            return url if is_image_url(url) else None
    except Exception:
        return None

async def get_raccoon_url(session: aiohttp.ClientSession) -> str:
    #url = await get_from_some_random_api(session)
    #if url is not None:
    #    return url
    return random.choice(FALLBACKS)

@bot.event
async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f"Welcome {member.name}-chan, have some cake !"
        await guild.system_channel.send(to_send)

@bot.event
async def on_message(message):
    if any(word in message.content.lower() for word in ["racoon", "racon", "raccoon"]):
        try:
            async with aiohttp.ClientSession() as session:
                url = await get_raccoon_url(session)
            await message.channel.send(url, reference=message)
        except Exception:
            await message.channel.send(
                "OwO !!! Unfortunately no raccoon is available right now to brighten your day. Get a heart instead <3~~"
                , reference=message)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if roleMessageId == payload.message_id:
        member = payload.member
        guild = member.guild
        await member.add_roles(get_role(payload, guild))


@bot.event
async def on_raw_reaction_remove(payload):
    guild = await(bot.fetch_guild(payload.guild_id))
    member = await(guild.fetch_member(payload.user_id))
    if member is not None:
        await member.remove_roles(get_role(payload, guild))
    else:
        print("Member not found")



bot.run(token, log_handler=handler, log_level=logging.DEBUG)